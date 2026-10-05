import secrets
from datetime import timedelta
from .. import db
from ..models import Application, Session, now
from ..devices.service import get_device
from ..risk.engine import assess
from ..policies.engine import evaluate
from ..audit import log

SESSION_MINUTES = 30


def request_access(user, mfa_ok, app_name, device_id):
    """Returns (decision, reason, session_id_or_None). Deny by default."""
    app = Application.query.filter_by(name=app_name).first()
    if not app:
        log("ACCESS_DENIED", user.username, "DENY", "unknown application")
        return "DENY", "unknown application", None

    device = get_device(user.id, device_id)
    risk = assess(user, device, mfa_ok)
    d = evaluate(user, app, device, mfa_ok, risk.score)

    if d.decision != "ALLOW":
        ev = "POLICY_DENIED" if d.decision == "DENY" else "STEP_UP_REQUIRED"
        log(ev, user.username, d.decision, d.reason, app.name, risk.score)
        return d.decision, d.reason, None

    sid = secrets.token_urlsafe(32)
    db.session.add(Session(id=sid, user_id=user.id,
                           device_id=device.id if device else None,
                           application_id=app.id,
                           expires_at=now() + timedelta(minutes=SESSION_MINUTES)))
    db.session.commit()
    log("ACCESS_ALLOWED", user.username, "ALLOW", d.reason, app.name, risk.score, sid)
    return "ALLOW", d.reason, sid
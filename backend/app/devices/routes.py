import re
from flask import Blueprint, request, session, jsonify
from .. import db
from ..models import Device, User
from ..audit import log
from ..auth.routes import login_required
from ..auth.rbac import roles_required
from .service import posture_ok

bp = Blueprint("devices", __name__, url_prefix="/api/devices")
REG_VALUES = {"UNKNOWN", "REGISTERED"}
COMP_VALUES = {"COMPLIANT", "NON_COMPLIANT"}


def _current():
    return db.session.get(User, session["user_id"])


def _dto(d):
    return {"id": d.id, "user_id": d.user_id, "hostname": d.hostname,
            "operating_system": d.operating_system,
            "registration_status": d.registration_status,
            "compliance_status": d.compliance_status,
            "last_seen": d.last_seen.isoformat() if d.last_seen else None}


@bp.get("")
@login_required
def list_devices():
    u = _current()
    is_admin = session.get("mfa_ok") and any(r.name == "ADMIN" for r in u.roles)
    q = Device.query if is_admin else Device.query.filter_by(user_id=u.id)
    return jsonify([_dto(d) for d in q.all()])


@bp.post("/register")
@login_required
def register():
    data = request.get_json(silent=True) or {}
    hostname = str(data.get("hostname", "")).strip()
    os_name = str(data.get("operating_system", "")).strip()[:50]
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", hostname) or not os_name:
        return jsonify(error="valid hostname and operating_system required"), 400
    u = _current()
    if Device.query.filter_by(user_id=u.id, hostname=hostname).first():
        return jsonify(error="device already registered"), 409
    # Zero Trust: a self-registered device is NOT trusted until an admin approves it.
    d = Device(user_id=u.id, hostname=hostname, operating_system=os_name)
    db.session.add(d)
    db.session.commit()
    log("DEVICE_REGISTERED", u.username, "ALLOW", f"pending approval: {hostname}")
    return jsonify(_dto(d)), 201


@bp.patch("/<int:device_id>")
@roles_required("ADMIN")
def update_device(device_id):
    d = db.session.get(Device, device_id)
    if not d:
        return jsonify(error="not found"), 404
    data = request.get_json(silent=True) or {}
    reg, comp = data.get("registration_status"), data.get("compliance_status")
    if (reg is not None and reg not in REG_VALUES) or \
       (comp is not None and comp not in COMP_VALUES):
        return jsonify(error="invalid status value"), 400
    if data.get("approve") is True:
        d.registration_status = "REGISTERED"
        d.compliance_status = "COMPLIANT" if posture_ok(d.operating_system) else "NON_COMPLIANT"
    if reg:
        d.registration_status = reg
    if comp:
        d.compliance_status = comp
    db.session.commit()
    log("DEVICE_UPDATED", _current().username, "ALLOW",
        f"device {d.id}: {d.registration_status}/{d.compliance_status}")
    return jsonify(_dto(d))
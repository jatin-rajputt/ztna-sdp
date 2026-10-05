from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db, limiter
from ..models import User
from ..audit import log

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
MAX_FAILS, LOCK_MINUTES = 5, 10
DUMMY_HASH = generate_password_hash("dummy-password")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return jsonify(error="authentication required"), 401
        return f(*a, **kw)
    return wrapper


@bp.post("/login")
@limiter.limit("10/minute")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", ""))[:50]
    password = str(data.get("password", ""))
    user = User.query.filter_by(username=username).first()
    fail = (jsonify(error="invalid credentials"), 401)

    if user and user.locked_until and user.locked_until > utcnow():
        log("LOGIN_FAILURE", username, "DENY", "account locked")
        return fail

    # Always run a hash check so timing doesn't reveal valid usernames
    ok = check_password_hash(user.password_hash if user else DUMMY_HASH, password)
    if not (user and ok and user.status == "ACTIVE"):
        log("LOGIN_FAILURE", username, "DENY", "bad credentials or inactive")
        if user:
            user.failed_logins = (user.failed_logins or 0) + 1
            if user.failed_logins >= MAX_FAILS:
                user.locked_until = utcnow() + timedelta(minutes=LOCK_MINUTES)
                user.failed_logins = 0
                log("BRUTE_FORCE_DETECTED", username, "DENY", "lockout triggered")
            db.session.commit()
        return fail

    user.failed_logins, user.locked_until = 0, None
    db.session.commit()
    session.clear()  # prevents session fixation
    session["user_id"] = user.id
    session["mfa_ok"] = False
    log("LOGIN_SUCCESS", username, "ALLOW")
    return jsonify(message="password accepted", mfa_required=bool(user.mfa_enabled))


@bp.post("/logout")
@login_required
def logout():
    user = db.session.get(User, session["user_id"])
    log("LOGOUT", user.username if user else None)
    session.clear()
    return jsonify(message="logged out")


@bp.get("/me")
@login_required
def me():
    u = db.session.get(User, session["user_id"])
    return jsonify(username=u.username, roles=[r.name for r in u.roles])
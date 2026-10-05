from datetime import datetime, timezone
from . import db


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.ForeignKey("roles.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), default="ACTIVE")        # ACTIVE / DISABLED
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(64))
    failed_logins = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    roles = db.relationship("Role", secondary=user_roles)


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    hostname = db.Column(db.String(80))
    operating_system = db.Column(db.String(50))
    registration_status = db.Column(db.String(20), default="UNKNOWN")      # UNKNOWN / REGISTERED
    compliance_status = db.Column(db.String(20), default="NON_COMPLIANT")  # COMPLIANT / NON_COMPLIANT
    last_seen = db.Column(db.DateTime, default=now)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)   # INTERNAL_WEB / SECURITY_DASHBOARD
    upstream_url = db.Column(db.String(200))


class Policy(db.Model):
    __tablename__ = "policies"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.ForeignKey("roles.id"), nullable=False)
    application_id = db.Column(db.ForeignKey("applications.id"), nullable=False)
    mfa_required = db.Column(db.Boolean, default=True)
    device_required = db.Column(db.Boolean, default=True)
    max_risk = db.Column(db.Integer, default=50)


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.String(64), primary_key=True)   # random token
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    device_id = db.Column(db.ForeignKey("devices.id"))
    application_id = db.Column(db.ForeignKey("applications.id"))
    created_at = db.Column(db.DateTime, default=now)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=now)
    status = db.Column(db.String(10), default="ACTIVE")   # ACTIVE / EXPIRED / REVOKED


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=now)
    event = db.Column(db.String(40))
    username = db.Column(db.String(50))
    source_ip = db.Column(db.String(45))
    application = db.Column(db.String(50))
    risk_score = db.Column(db.Integer)
    decision = db.Column(db.String(10))
    reason = db.Column(db.String(200))
    session_id = db.Column(db.String(64))


class RiskEvent(db.Model):
    __tablename__ = "risk_events"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"))
    factor = db.Column(db.String(50))
    points = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=now)
from flask import request, has_request_context
from .. import db
from ..models import AuditLog


def log(event, username=None, decision=None, reason=None,
        application=None, risk_score=None, session_id=None):
    ip = request.remote_addr if has_request_context() else None
    db.session.add(AuditLog(event=event, username=username, source_ip=ip,
                            decision=decision, reason=reason, application=application,
                            risk_score=risk_score, session_id=session_id))
    db.session.commit()
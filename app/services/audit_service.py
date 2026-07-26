"""
app/services/audit_service.py
--------------------------------
Centralised audit logging service. Every route that creates, updates or
deletes a record should call AuditService.log(...) so a complete history is
retained for compliance & traceability, mirroring how enterprise systems
like SAP PM keep change documents.
"""

from flask_login import current_user
from app.extensions import db
from app.models.audit import AuditLog
from app.utils.helpers import get_client_ip


class AuditService:

    @staticmethod
    def log(action: str, entity_type: str, entity_id: int = None, description: str = ""):
        """Persist a single audit trail entry."""
        entry = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=get_client_ip(),
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_recent(limit: int = 20):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()

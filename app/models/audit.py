"""
app/models/audit.py
---------------------
Audit trail model. Every create / update / delete performed via the
application's services should call AuditService.log(...) which persists a
row here, giving administrators a full history of who changed what and when.
"""

from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(50), nullable=False)       # CREATE / UPDATE / DELETE / LOGIN / LOGOUT
    entity_type = db.Column(db.String(80), nullable=False)  # e.g. "Equipment", "Project"
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}#{self.entity_id}>"

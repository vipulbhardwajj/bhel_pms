"""
app/models/documents.py
-------------------------
File attachment models associated with Equipment records:

    Photo    - site photographs (installation / commissioning evidence)
    Document - general documents (test certificates, QAP, inspection reports)
    Drawing  - engineering drawings (GA drawings, P&ID, layout drawings)

All three store the file on disk under app/static/uploads/<type>/ and persist
metadata (original filename, stored filename, uploader, timestamp) in the
database.
"""

from datetime import datetime
from app.extensions import db


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    filename = db.Column(db.String(255), nullable=False)       # stored on-disk name
    original_filename = db.Column(db.String(255))
    caption = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploaded_by = db.relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Photo {self.filename}>"


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    document_type = db.Column(db.String(100))  # e.g. "Test Certificate", "QAP"
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploaded_by = db.relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Document {self.filename}>"


class Drawing(db.Model):
    __tablename__ = "drawings"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    drawing_number = db.Column(db.String(100))
    revision = db.Column(db.String(20))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploaded_by = db.relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Drawing {self.drawing_number} rev {self.revision}>"

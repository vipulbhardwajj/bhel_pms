"""
app/models/vendor.py
---------------------
Vendor master data - suppliers / OEMs / sub-contractors associated with
equipment supply, installation or commissioning.
"""

from datetime import datetime
from app.extensions import db


class Vendor(db.Model):
    """Represents a supplier, OEM or sub-contracting vendor."""

    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    vendor_code = db.Column(db.String(30), unique=True, nullable=False)
    contact_person = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(30))
    specialization = db.Column(db.String(200))  # e.g. "Pumps & Valves", "Electrical"
    rating = db.Column(db.Float, default=0.0)   # vendor performance rating 0-5
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    equipment_items = db.relationship("Equipment", backref="vendor", lazy="dynamic")

    def __repr__(self):
        return f"<Vendor {self.vendor_code} - {self.name}>"

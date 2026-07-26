"""
app/models/equipment.py
------------------------
Equipment Category (master data) and Equipment (transactional master) models.

Equipment is the lowest / leaf level of the plant hierarchy:

    Project -> Unit -> Area -> System -> Equipment

Each Equipment record tracks installation & commissioning progress
independently, along with vendor, drawing / PO references, assigned
engineer and supporting photo/document/drawing attachments.
"""

from datetime import datetime
from app.extensions import db


class EquipmentCategory(db.Model):
    """Master list of equipment categories (e.g. Pump, Valve, Motor, Transformer)."""

    __tablename__ = "equipment_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    equipment_items = db.relationship("Equipment", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<EquipmentCategory {self.code}>"


class EquipmentStatus:
    NOT_STARTED = "Not Started"
    PROCUREMENT = "Under Procurement"
    RECEIVED = "Received at Site"
    INSTALLATION = "Under Installation"
    INSTALLED = "Installed"
    COMMISSIONING = "Under Commissioning"
    COMMISSIONED = "Commissioned"
    DELAYED = "Delayed"

    ALL = [NOT_STARTED, PROCUREMENT, RECEIVED, INSTALLATION, INSTALLED,
           COMMISSIONING, COMMISSIONED, DELAYED]

    # Bootstrap contextual colour classes used consistently across templates
    BADGE_CLASS = {
        NOT_STARTED: "secondary",
        PROCUREMENT: "info",
        RECEIVED: "primary",
        INSTALLATION: "warning",
        INSTALLED: "success",
        COMMISSIONING: "warning",
        COMMISSIONED: "success",
        DELAYED: "danger",
    }


class Equipment(db.Model):
    """Leaf-level equipment master record with full progress tracking."""

    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey("systems.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("equipment_categories.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))
    assigned_engineer_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    equipment_name = db.Column(db.String(200), nullable=False)
    equipment_code = db.Column(db.String(50), nullable=False, index=True)
    drawing_number = db.Column(db.String(100))
    po_number = db.Column(db.String(100))
    status = db.Column(db.String(30), default=EquipmentStatus.NOT_STARTED, nullable=False)

    installation_progress = db.Column(db.Float, default=0.0)   # 0-100
    commissioning_progress = db.Column(db.Float, default=0.0)  # 0-100

    remarks = db.Column(db.Text)
    expected_date = db.Column(db.Date)
    actual_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("system_id", "equipment_code", name="uq_equipment_system_code"),
    )

    # --- Relationships ---
    photos = db.relationship("Photo", backref="equipment", cascade="all, delete-orphan", lazy="dynamic")
    documents = db.relationship("Document", backref="equipment", cascade="all, delete-orphan", lazy="dynamic")
    drawings = db.relationship("Drawing", backref="equipment", cascade="all, delete-orphan", lazy="dynamic")
    daily_progress_logs = db.relationship(
        "DailyProgress", backref="equipment", cascade="all, delete-orphan", lazy="dynamic"
    )
    weekly_progress_logs = db.relationship(
        "WeeklyProgress", backref="equipment", cascade="all, delete-orphan", lazy="dynamic"
    )
    monthly_progress_logs = db.relationship(
        "MonthlyProgress", backref="equipment", cascade="all, delete-orphan", lazy="dynamic"
    )

    # ------------------------------------------------------------------
    @property
    def is_overdue(self) -> bool:
        from datetime import date
        return bool(
            self.expected_date
            and not self.actual_date
            and date.today() > self.expected_date
        )

    @property
    def badge_class(self) -> str:
        return EquipmentStatus.BADGE_CLASS.get(self.status, "secondary")

    @property
    def project(self):
        """Convenience accessor to walk up the hierarchy to the Project."""
        return self.system.area.unit.project

    def __repr__(self):
        return f"<Equipment {self.equipment_code}>"

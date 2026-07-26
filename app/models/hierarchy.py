"""
app/models/hierarchy.py
------------------------
Mid-level hierarchy entities that sit between Project and Equipment:

    Unit    - a generating unit within a project (e.g. "Unit-1", "Unit-2")
    Area    - a functional plant area within a unit (e.g. "Boiler Area", "TG Area")
    System  - an engineering system within an area (e.g. "Coal Handling System")
"""

from datetime import datetime
from app.extensions import db


class Unit(db.Model):
    """A generating unit belonging to a Project."""

    __tablename__ = "units"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)  # e.g. "Unit-1 (800MW)"
    unit_code = db.Column(db.String(30), nullable=False)
    capacity_mw = db.Column(db.Float)
    overall_progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    areas = db.relationship("Area", backref="unit", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint("project_id", "unit_code", name="uq_unit_project_code"),)

    def recalculate_progress(self):
        areas = self.areas.all()
        if not areas:
            self.overall_progress = 0.0
            return
        total = sum(a.overall_progress or 0 for a in areas)
        self.overall_progress = round(total / len(areas), 2)

    def __repr__(self):
        return f"<Unit {self.unit_code}>"


class Area(db.Model):
    """A functional plant area within a Unit (e.g. Boiler, Turbine, ESP)."""

    __tablename__ = "areas"

    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("units.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    area_code = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    overall_progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    systems = db.relationship(
        "System", backref="area", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (db.UniqueConstraint("unit_id", "area_code", name="uq_area_unit_code"),)

    def recalculate_progress(self):
        systems = self.systems.all()
        if not systems:
            self.overall_progress = 0.0
            return
        total = sum(s.overall_progress or 0 for s in systems)
        self.overall_progress = round(total / len(systems), 2)

    def __repr__(self):
        return f"<Area {self.area_code}>"


class System(db.Model):
    """An engineering system within an Area (e.g. Coal Handling, Cooling Water)."""

    __tablename__ = "systems"

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    system_code = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    overall_progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    equipment_items = db.relationship(
        "Equipment", backref="system", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (db.UniqueConstraint("area_id", "system_code", name="uq_system_area_code"),)

    def recalculate_progress(self):
        items = self.equipment_items.all()
        if not items:
            self.overall_progress = 0.0
            return
        total = sum(((e.installation_progress or 0) + (e.commissioning_progress or 0)) / 2 for e in items)
        self.overall_progress = round(total / len(items), 2)

    def __repr__(self):
        return f"<System {self.system_code}>"

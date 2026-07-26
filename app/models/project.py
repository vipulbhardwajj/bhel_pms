from app.models.association import user_projects

from datetime import datetime
from app.extensions import db


class ProjectStatus:
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    DELAYED = "Delayed"

    ALL = [PLANNED, IN_PROGRESS, ON_HOLD, COMPLETED, DELAYED]


class Project(db.Model):
    """Represents an EPC / power plant project executed by BHEL."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(200))  # e.g. NTPC, NPCIL, State Genco
    location = db.Column(db.String(200))
    capacity_mw = db.Column(db.Float)  # total plant capacity in MW
    contract_value_crore = db.Column(db.Float)  # contract value in INR Crore
    start_date = db.Column(db.Date)
    scheduled_end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    status = db.Column(db.String(30), default=ProjectStatus.PLANNED, nullable=False)
    project_manager = db.Column(db.String(120))
    description = db.Column(db.Text)
    overall_progress = db.Column(db.Float, default=0.0)  # 0-100, cached/aggregate value
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_engineers = db.relationship(
    "User",
    secondary=user_projects,
    back_populates="assigned_projects",
    
)
    # --- Relationships ---
    units = db.relationship(
        "Unit", backref="project", cascade="all, delete-orphan", lazy="dynamic"
    )

    # ------------------------------------------------------------------
    def recalculate_progress(self):
        """Recompute overall_progress as the average of child Unit progress."""
        units = self.units.all()
        if not units:
            self.overall_progress = 0.0
            return
        total = sum(u.overall_progress or 0 for u in units)
        self.overall_progress = round(total / len(units), 2)

    @property
    def equipment_count(self) -> int:
        """Total equipment records nested under this project (all units/areas/systems)."""
        count = 0
        for unit in self.units:
            for area in unit.areas:
                for system in area.systems:
                    count += system.equipment_items.count()
        return count

    @property
    def is_delayed(self) -> bool:
        if not self.scheduled_end_date:
            return False
        from datetime import date
        return (
            self.status not in (ProjectStatus.COMPLETED,)
            and date.today() > self.scheduled_end_date
        )

    def __repr__(self):
        return f"<Project {self.project_code} - {self.name}>"

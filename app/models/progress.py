"""
app/models/progress.py
------------------------
Progress tracking models recorded against Equipment at three cadences:

    DailyProgress   - site engineers log daily installation/commissioning updates
    WeeklyProgress  - rolled-up weekly summary (planned vs actual)
    MonthlyProgress - rolled-up monthly summary for management reporting

Keeping three distinct tables (rather than one generic table with a "period
type" column) keeps queries simple and mirrors how real EPC monitoring tools
(Primavera P6 style) separate reporting cadences.
"""

from datetime import datetime
from app.extensions import db


class DailyProgress(db.Model):
    __tablename__ = "daily_progress"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    logged_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    log_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    installation_progress = db.Column(db.Float, default=0.0)
    commissioning_progress = db.Column(db.Float, default=0.0)
    activity_description = db.Column(db.Text)
    manpower_deployed = db.Column(db.Integer, default=0)
    hindrances = db.Column(db.Text)  # blockers / issues faced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logged_by = db.relationship("User", foreign_keys=[logged_by_id])

    def __repr__(self):
        return f"<DailyProgress eq={self.equipment_id} {self.log_date}>"


class WeeklyProgress(db.Model):
    __tablename__ = "weekly_progress"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    logged_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    planned_progress = db.Column(db.Float, default=0.0)
    actual_progress = db.Column(db.Float, default=0.0)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logged_by = db.relationship("User", foreign_keys=[logged_by_id])

    @property
    def variance(self):
        return round((self.actual_progress or 0) - (self.planned_progress or 0), 2)

    def __repr__(self):
        return f"<WeeklyProgress eq={self.equipment_id} {self.week_start_date}>"


class MonthlyProgress(db.Model):
    __tablename__ = "monthly_progress"

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    logged_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    planned_progress = db.Column(db.Float, default=0.0)
    actual_progress = db.Column(db.Float, default=0.0)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logged_by = db.relationship("User", foreign_keys=[logged_by_id])

    @property
    def variance(self):
        return round((self.actual_progress or 0) - (self.planned_progress or 0), 2)

    __table_args__ = (
        db.UniqueConstraint("equipment_id", "month", "year", name="uq_monthly_progress_period"),
    )

    def __repr__(self):
        return f"<MonthlyProgress eq={self.equipment_id} {self.month}/{self.year}>"

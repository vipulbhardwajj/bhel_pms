"""
app/services/dashboard_service.py
------------------------------------
Aggregation queries powering the main Dashboard: KPI cards, chart datasets
(pie / bar), upcoming deadlines and recent activity feed. Keeping this logic
in a service (rather than inline in the route) keeps routes thin and the
aggregation logic independently testable.
"""

from datetime import date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.project import Project, ProjectStatus
from app.models.equipment import Equipment, EquipmentStatus
from app.models.vendor import Vendor
from app.models.audit import AuditLog
from flask_login import current_user
from app.models.user import User

class DashboardService:
    @staticmethod
    def project_query():

        if current_user.is_admin:
            return Project.query

        if current_user.is_engineer:
            return (
                Project.query
                .join(Project.assigned_engineers)
                .filter(User.id == current_user.id)
            )

        return Project.query

    @staticmethod
    def get_kpis():
        projects = DashboardService.project_query()

        total_projects = projects.count()
        active_projects = projects.filter(
            Project.status.in_([ProjectStatus.IN_PROGRESS, ProjectStatus.DELAYED])
        ).count()
        total_equipment = Equipment.query.count()
        commissioned = Equipment.query.filter_by(status=EquipmentStatus.COMMISSIONED).count()
        delayed_projects = projects.filter(Project.status == ProjectStatus.DELAYED).count()
        total_vendors = Vendor.query.filter_by(is_active=True).count()

        avg_install = db.session.query(func.avg(Equipment.installation_progress)).scalar() or 0
        avg_commission = db.session.query(func.avg(Equipment.commissioning_progress)).scalar() or 0

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_equipment": total_equipment,
            "commissioned_equipment": commissioned,
            "delayed_projects": delayed_projects,
            "total_vendors": total_vendors,
            "avg_installation_progress": round(avg_install, 1),
            "avg_commissioning_progress": round(avg_commission, 1),
        }

    @staticmethod
    def get_status_distribution():
        """Equipment count grouped by status - feeds the dashboard pie chart."""
        results = (
            db.session.query(Equipment.status, func.count(Equipment.id))
            .group_by(Equipment.status)
            .all()
        )
        return {status: count for status, count in results}

    @staticmethod
    def get_project_progress_bar_data():
        """Project name + overall_progress - feeds the dashboard bar chart."""
        projects = DashboardService.project_query().order_by(Project.overall_progress.desc()).limit(10).all()
        return {
            "labels": [p.project_code for p in projects],
            "values": [p.overall_progress or 0 for p in projects],
        }

    @staticmethod
    def get_upcoming_deadlines(days_ahead: int = 14, limit: int = 10):
        horizon = date.today() + timedelta(days=days_ahead)
        return (
            Equipment.query.filter(
                Equipment.expected_date.isnot(None),
                Equipment.expected_date <= horizon,
                Equipment.actual_date.is_(None),
            )
            .order_by(Equipment.expected_date.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_activities(limit: int = 10):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_project_cards():
        """Return all projects (ordered newest first) for the dashboard card grid.
        Each Project already exposes `.units` and `.overall_progress`, and the
        template computes any additional per-card counts via helper properties."""
        return (
                    DashboardService.project_query()
                    .order_by(Project.created_at.desc())
                    .all()
                )

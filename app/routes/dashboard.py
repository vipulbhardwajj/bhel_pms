"""
app/routes/dashboard.py
--------------------------
Main Dashboard blueprint. Aggregates KPI cards, chart datasets, project
cards, upcoming deadlines, recent activity and notifications into a single
landing page for all authenticated users (content is the same across roles;
edit actions elsewhere are gated by role).
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services.dashboard_service import DashboardService
from app.services.notification_service import NotificationService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    # Lazily refresh deadline notifications whenever the dashboard loads.
    NotificationService.generate_deadline_alerts()

    kpis = DashboardService.get_kpis()
    status_distribution = DashboardService.get_status_distribution()
    bar_data = DashboardService.get_project_progress_bar_data()
    upcoming_deadlines = DashboardService.get_upcoming_deadlines()
    recent_activities = DashboardService.get_recent_activities()
    project_cards = DashboardService.get_project_cards()
    notifications = NotificationService.get_unread_for_user(current_user.id)

    return render_template(
        "dashboard/index.html",
        kpis=kpis,
        status_distribution=status_distribution,
        bar_data=bar_data,
        upcoming_deadlines=upcoming_deadlines,
        recent_activities=recent_activities,
        project_cards=project_cards,
        notifications=notifications,
    )

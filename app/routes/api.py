"""
app/routes/api.py
--------------------
Lightweight JSON API endpoints consumed by client-side JavaScript
(notification bell polling, Chart.js dataset refresh) without a full page
reload.
"""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.services.notification_service import NotificationService
from app.services.dashboard_service import DashboardService
from app.models.notification import Notification
from app.extensions import db

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/notifications/unread-count")
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})


@api_bp.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    NotificationService.mark_all_read(current_user.id)
    return jsonify({"success": True})


@api_bp.route("/dashboard/status-distribution")
@login_required
def status_distribution():
    return jsonify(DashboardService.get_status_distribution())


@api_bp.route("/dashboard/project-progress")
@login_required
def project_progress():
    return jsonify(DashboardService.get_project_progress_bar_data())

"""
app/routes/reports.py
------------------------
Reports hub: lets users pick a project and generate a PDF progress report,
or export the full equipment master to Excel. Individual export endpoints
also live on their respective blueprints (projects.export_pdf,
equipment.export_excel) - this blueprint provides the discoverable landing
page tying them together.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from app.models.project import Project

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():
    projects = Project.query.order_by(Project.name).all()
    return render_template("reports/index.html", projects=projects)

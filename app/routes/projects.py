from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_file,
    current_app,
)

from flask_login import login_required, current_user
from app.utils.project_access import get_accessible_projects
from app.extensions import db
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.forms.project_forms import ProjectForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService
from app.services.pdf_service import PDFService

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


# ==========================================================
# List Projects
# ==========================================================
@projects_bp.route("/")
@login_required
def list_projects():

    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = get_accessible_projects()

    # -----------------------------
    # Search
    # -----------------------------
    if search:

        like = f"%{search}%"

        query = query.filter(
            db.or_(
                Project.name.ilike(like),
                Project.project_code.ilike(like),
                Project.client_name.ilike(like),
            )
        )

    # -----------------------------
    # Status Filter
    # -----------------------------
    if status_filter:

        query = query.filter(
            Project.status == status_filter
        )

    pagination = query.order_by(
        Project.created_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config["ITEMS_PER_PAGE"],
        error_out=False,
    )

    return render_template(
        "projects/list.html",
        pagination=pagination,
        projects=pagination.items,
        search=search,
        status_filter=status_filter,
        statuses=ProjectStatus.ALL,
    )


# ==========================================================
# Create Project
# ==========================================================
@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_project():

    form = ProjectForm()

    form.load_engineers()

    if form.validate_on_submit():

        project = Project()

        project.project_code = form.project_code.data
        project.name = form.name.data
        project.client_name = form.client_name.data
        project.location = form.location.data
        project.capacity_mw = form.capacity_mw.data
        project.contract_value_crore = form.contract_value_crore.data
        project.start_date = form.start_date.data
        project.scheduled_end_date = form.scheduled_end_date.data
        project.actual_end_date = form.actual_end_date.data
        project.status = form.status.data
        project.project_manager = form.project_manager.data
        project.description = form.description.data

        # -----------------------------
        # Assign Engineers
        # -----------------------------
        engineers = User.query.filter(
                User.id.in_(form.assigned_engineers.data)
            ).all()

        project.assigned_engineers = engineers

        db.session.add(project)
        db.session.commit()

        AuditService.log(
            "CREATE",
            "Project",
            project.id,
            f"Created project {project.project_code}",
        )

        flash(
            "Project created successfully.",
            "success"
        )

        return redirect(
            url_for("projects.list_projects")
        )

    return render_template(
        "projects/form.html",
        form=form,
        title="New Project",
    )


# ==========================================================
# Project Details
# ==========================================================
@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):

    project = Project.query.get_or_404(project_id)

    return render_template(
        "projects/detail.html",
        project=project,
    )


# ==========================================================
# Edit Project
# ==========================================================
@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_project(project_id):

    project = Project.query.get_or_404(project_id)

    form = ProjectForm(obj=project)

    form.load_engineers()

    # -----------------------------
    # Preselect assigned engineers
    # -----------------------------
    if request.method == "GET":

        form.assigned_engineers.data = [
            engineer.id
            for engineer in project.assigned_engineers
        ]

    if form.validate_on_submit():

        project.project_code = form.project_code.data
        project.name = form.name.data
        project.client_name = form.client_name.data
        project.location = form.location.data
        project.capacity_mw = form.capacity_mw.data
        project.contract_value_crore = form.contract_value_crore.data
        project.start_date = form.start_date.data
        project.scheduled_end_date = form.scheduled_end_date.data
        project.actual_end_date = form.actual_end_date.data
        project.status = form.status.data
        project.project_manager = form.project_manager.data
        project.description = form.description.data

        # -----------------------------
        # Update Engineer Assignment
        # -----------------------------
        engineers = User.query.filter(
            User.id.in_(form.assigned_engineers.data)
        ).all()

        project.assigned_engineers = engineers
        
        db.session.commit()

        AuditService.log(
            "UPDATE",
            "Project",
            project.id,
            f"Updated project {project.project_code}",
        )

        flash(
            "Project updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "projects.detail",
                project_id=project.id,
            )
        )

    return render_template(
        "projects/form.html",
        form=form,
        title="Edit Project",
        project=project,
    )


# ==========================================================
# Delete Project
# ==========================================================
@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_project(project_id):

    project = Project.query.get_or_404(project_id)

    code = project.project_code

    db.session.delete(project)
    db.session.commit()

    AuditService.log(
        "DELETE",
        "Project",
        project.id,
        f"Deleted project {code}",
    )

    flash(
        "Project deleted.",
        "info"
    )

    return redirect(
        url_for("projects.list_projects")
    )


# ==========================================================
# Export PDF
# ==========================================================
@projects_bp.route("/<int:project_id>/report/pdf")
@login_required
def export_pdf(project_id):

    project = Project.query.get_or_404(project_id)

    buffer = PDFService.generate_project_report(project)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{project.project_code}_progress_report.pdf",
        mimetype="application/pdf",
    )
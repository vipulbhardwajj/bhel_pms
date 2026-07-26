"""
app/routes/systems.py
------------------------
CRUD blueprint for the System hierarchy level (child of Area, parent of
Equipment).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.utils.project_access import get_accessible_projects
from app.extensions import db
from app.models.hierarchy import System, Area, Unit
from app.forms.project_forms import SystemForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService
from app.models.hierarchy import Area, Unit
from app.utils.project_access import get_accessible_projects
systems_bp = Blueprint("systems", __name__, url_prefix="/systems")


def _populate_area_choices(form):

    project_ids = [
        p.id
        for p in get_accessible_projects().all()
    ]

    areas = (
        Area.query
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
        .order_by(Area.name)
        .all()
    )

    form.area_id.choices = [
        (a.id, f"{a.area_code} - {a.name}")
        for a in areas
    ]
@systems_bp.route("/")
@login_required
def list_systems():
    area_id = request.args.get("area_id", type=int)
    project_ids = [p.id for p in get_accessible_projects().all()]
    project_ids = [
            p.id
            for p in get_accessible_projects().all()
    ]

    query = (
        System.query
        .join(System.area)
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
    )
    if area_id:
        query = query.filter_by(area_id=area_id)
    systems = query.order_by(System.name).all()
    areas = (
                Area.query
                .join(Area.unit)
                .filter(Unit.project_id.in_(project_ids))
                .order_by(Area.name)
                .all()
            )
    return render_template("systems/list.html", systems=systems, areas=areas, selected_area=area_id)


@systems_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_system():
    form = SystemForm()
    _populate_area_choices(form)
    if form.validate_on_submit():
        system = System()
        form.populate_obj(system)
        db.session.add(system)
        db.session.commit()
        AuditService.log("CREATE", "System", system.id, f"Created system {system.system_code}")
        flash("System created successfully.", "success")
        return redirect(url_for("systems.list_systems"))
    return render_template("systems/form.html", form=form, title="New System")


@systems_bp.route("/<int:system_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_system(system_id):
    system = System.query.get_or_404(system_id)
    form = SystemForm(obj=system)
    _populate_area_choices(form)
    if form.validate_on_submit():
        form.populate_obj(system)
        db.session.commit()
        AuditService.log("UPDATE", "System", system.id, f"Updated system {system.system_code}")
        flash("System updated successfully.", "success")
        return redirect(url_for("systems.list_systems"))
    return render_template("systems/form.html", form=form, title="Edit System", system=system)


@systems_bp.route("/<int:system_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_system(system_id):
    system = System.query.get_or_404(system_id)
    code = system.system_code
    db.session.delete(system)
    db.session.commit()
    AuditService.log("DELETE", "System", system_id, f"Deleted system {code}")
    flash("System deleted.", "info")
    return redirect(url_for("systems.list_systems"))

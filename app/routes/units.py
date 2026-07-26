"""
app/routes/units.py
----------------------
CRUD blueprint for the Unit hierarchy level (child of Project).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.utils.project_access import get_accessible_projects
from app.extensions import db
from app.models.hierarchy import Unit
from app.models.project import Project
from app.forms.project_forms import UnitForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService

units_bp = Blueprint("units", __name__, url_prefix="/units")


def _populate_project_choices(form):
    projects = get_accessible_projects().order_by(Project.name).all()

    form.project_id.choices = [
        (p.id, f"{p.project_code} - {p.name}")
        for p in projects
    ]


@units_bp.route("/")
@login_required
def list_units():
    project_id = request.args.get("project_id", type=int)
    accessible_projects = get_accessible_projects().all()

    project_ids = [p.id for p in accessible_projects]

    query = Unit.query.filter(Unit.project_id.in_(project_ids))
    if project_id:
        query = query.filter_by(project_id=project_id)
    units = query.order_by(Unit.name).all()
    projects = get_accessible_projects().order_by(Project.name).all()
    return render_template("units/list.html", units=units, projects=projects, selected_project=project_id)


@units_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_unit():
    form = UnitForm()
    _populate_project_choices(form)
    if form.validate_on_submit():
        unit = Unit()
        form.populate_obj(unit)
        db.session.add(unit)
        db.session.commit()
        AuditService.log("CREATE", "Unit", unit.id, f"Created unit {unit.unit_code}")
        flash("Unit created successfully.", "success")
        return redirect(url_for("units.list_units"))
    return render_template("units/form.html", form=form, title="New Unit")


@units_bp.route("/<int:unit_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    form = UnitForm(obj=unit)
    _populate_project_choices(form)
    if form.validate_on_submit():
        form.populate_obj(unit)
        db.session.commit()
        AuditService.log("UPDATE", "Unit", unit.id, f"Updated unit {unit.unit_code}")
        flash("Unit updated successfully.", "success")
        return redirect(url_for("units.list_units"))
    return render_template("units/form.html", form=form, title="Edit Unit", unit=unit)


@units_bp.route("/<int:unit_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    code = unit.unit_code
    db.session.delete(unit)
    db.session.commit()
    AuditService.log("DELETE", "Unit", unit_id, f"Deleted unit {code}")
    flash("Unit deleted.", "info")
    return redirect(url_for("units.list_units"))

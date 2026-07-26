"""
app/routes/areas.py
----------------------
CRUD blueprint for the Area hierarchy level (child of Unit).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.utils.project_access import get_accessible_projects
from app.extensions import db
from app.models.hierarchy import Area, Unit
from app.forms.project_forms import AreaForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService

areas_bp = Blueprint("areas", __name__, url_prefix="/areas")


def _populate_unit_choices(form):

    # Get accessible projects
    project_ids = [
        p.id
        for p in get_accessible_projects().all()
    ]

    # Get units belonging only to those projects
    units = (
        Unit.query
        .filter(Unit.project_id.in_(project_ids))
        .order_by(Unit.name)
        .all()
    )

    form.unit_id.choices = [
        (u.id, f"{u.unit_code} - {u.name}")
        for u in units
    ]


@areas_bp.route("/")
@login_required
def list_areas():
    unit_id = request.args.get("unit_id", type=int)
    project_ids = [
        p.id
        for p in get_accessible_projects().all()
    ]

    query = (
        Area.query
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
    )
    if unit_id:
        query = query.filter_by(unit_id=unit_id)
    areas = query.order_by(Area.name).all()
    units = (
                Unit.query
                .filter(Unit.project_id.in_(project_ids))
                .order_by(Unit.name)
                .all()
            )
    return render_template("areas/list.html", areas=areas, units=units, selected_unit=unit_id)


@areas_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_area():
    form = AreaForm()
    _populate_unit_choices(form)
    if form.validate_on_submit():
        area = Area()
        form.populate_obj(area)
        db.session.add(area)
        db.session.commit()
        AuditService.log("CREATE", "Area", area.id, f"Created area {area.area_code}")
        flash("Area created successfully.", "success")
        return redirect(url_for("areas.list_areas"))
    return render_template("areas/form.html", form=form, title="New Area")


@areas_bp.route("/<int:area_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_area(area_id):
    area = Area.query.get_or_404(area_id)
    form = AreaForm(obj=area)
    _populate_unit_choices(form)
    if form.validate_on_submit():
        form.populate_obj(area)
        db.session.commit()
        AuditService.log("UPDATE", "Area", area.id, f"Updated area {area.area_code}")
        flash("Area updated successfully.", "success")
        return redirect(url_for("areas.list_areas"))
    return render_template("areas/form.html", form=form, title="Edit Area", area=area)


@areas_bp.route("/<int:area_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_area(area_id):
    area = Area.query.get_or_404(area_id)
    code = area.area_code
    db.session.delete(area)
    db.session.commit()
    AuditService.log("DELETE", "Area", area_id, f"Deleted area {code}")
    flash("Area deleted.", "info")
    return redirect(url_for("areas.list_areas"))

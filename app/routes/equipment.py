"""
app/routes/equipment.py
--------------------------
Equipment master CRUD, detail view (photos/documents/drawings tabs), and
Excel import/export endpoints. This is the most feature-rich blueprint since
Equipment is the leaf node of the plant hierarchy where day-to-day progress
tracking and file attachments happen.
"""

import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    send_file, send_from_directory, current_app
)
from flask_login import login_required, current_user
from app.models.hierarchy import System, Area, Unit
from app.utils.project_access import get_accessible_projects
from app.extensions import db
from app.models.equipment import Equipment, EquipmentCategory, EquipmentStatus
from app.models.hierarchy import System
from app.models.vendor import Vendor
from app.models.user import User
from app.models.documents import Photo, Document, Drawing
from app.utils.access import require_equipment_access
from app.forms.equipment_forms import (
    EquipmentForm, EquipmentCategoryForm, PhotoUploadForm, DocumentUploadForm, DrawingUploadForm
)
from app.utils.decorators import editor_required
from app.utils.validators import allowed_image, allowed_document, allowed_drawing
from app.utils.helpers import save_uploaded_file
from app.services.audit_service import AuditService
from app.services.excel_service import ExcelService
from app.utils.project_access import get_accessible_projects
from app.models.hierarchy import System, Area, Unit
equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")


def _populate_choices(form):

    project_ids = [p.id for p in get_accessible_projects().all()]

    systems = (
        System.query
        .join(System.area)
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
        .order_by(System.name)
        .all()
    )

    form.system_id.choices = [
        (s.id, f"{s.system_code} - {s.name}")
        for s in systems
    ]

    form.category_id.choices = [(0, "-- None --")] + [
        (c.id, c.name)
        for c in EquipmentCategory.query.order_by(EquipmentCategory.name)
    ]

    form.vendor_id.choices = [(0, "-- None --")] + [
        (v.id, v.name)
        for v in Vendor.query.filter_by(is_active=True).order_by(Vendor.name)
    ]

    form.assigned_engineer_id.choices = [(0, "-- Unassigned --")] + [
        (u.id, u.full_name)
        for u in User.query.filter_by(role="Engineer").order_by(User.full_name)
    ]

@equipment_bp.route("/")
@login_required
def list_equipment():
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    system_filter = request.args.get("system_id", type=int)
    page = request.args.get("page", 1, type=int)

    project_ids = [p.id for p in get_accessible_projects().all()]

    query = (
        Equipment.query
        .join(Equipment.system)
        .join(System.area)
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
    )
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Equipment.equipment_name.ilike(like), Equipment.equipment_code.ilike(like))
        )
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    if system_filter:
        query = query.filter(Equipment.system_id == system_filter)

    pagination = query.order_by(Equipment.updated_at.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    systems = (
                    System.query
                    .join(System.area)
                    .join(Area.unit)
                    .filter(Unit.project_id.in_(project_ids))
                    .order_by(System.name)
                    .all()
                )

    return render_template(
        "equipment/list.html",
        pagination=pagination,
        equipment_items=pagination.items,
        search=search,
        status_filter=status_filter,
        system_filter=system_filter,
        systems=systems,
        statuses=EquipmentStatus.ALL,
    )


@equipment_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_equipment():
    form = EquipmentForm()
    _populate_choices(form)
    if form.validate_on_submit():
        eq = Equipment()
        form.populate_obj(eq)
        eq.category_id = eq.category_id or None
        eq.vendor_id = eq.vendor_id or None
        eq.assigned_engineer_id = eq.assigned_engineer_id or None
        db.session.add(eq)
        db.session.commit()
        eq.system.recalculate_progress()
        db.session.commit()
        AuditService.log("CREATE", "Equipment", eq.id, f"Created equipment {eq.equipment_code}")
        flash("Equipment created successfully.", "success")
        return redirect(url_for("equipment.detail", equipment_id=eq.id))
    return render_template("equipment/form.html", form=form, title="New Equipment")


@equipment_bp.route("/<int:equipment_id>")
@login_required
def detail(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    photo_form = PhotoUploadForm()
    document_form = DocumentUploadForm()
    drawing_form = DrawingUploadForm()
    return render_template(
        "equipment/detail.html", equipment=eq,
        photo_form=photo_form, document_form=document_form, drawing_form=drawing_form,
    )


@equipment_bp.route("/<int:equipment_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_equipment(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    form = EquipmentForm(obj=eq)
    _populate_choices(form)
    if request.method == "GET":
        form.category_id.data = eq.category_id or 0
        form.vendor_id.data = eq.vendor_id or 0
        form.assigned_engineer_id.data = eq.assigned_engineer_id or 0
    if form.validate_on_submit():
        form.populate_obj(eq)
        eq.category_id = eq.category_id or None
        eq.vendor_id = eq.vendor_id or None
        eq.assigned_engineer_id = eq.assigned_engineer_id or None
        db.session.commit()
        eq.system.recalculate_progress()
        db.session.commit()
        AuditService.log("UPDATE", "Equipment", eq.id, f"Updated equipment {eq.equipment_code}")
        flash("Equipment updated successfully.", "success")
        return redirect(url_for("equipment.detail", equipment_id=eq.id))
    return render_template("equipment/form.html", form=form, title="Edit Equipment", equipment=eq)


@equipment_bp.route("/<int:equipment_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_equipment(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    code = eq.equipment_code
    system = eq.system
    db.session.delete(eq)
    db.session.commit()
    system.recalculate_progress()
    db.session.commit()
    AuditService.log("DELETE", "Equipment", equipment_id, f"Deleted equipment {code}")
    flash("Equipment deleted.", "info")
    return redirect(url_for("equipment.list_equipment"))


# ----------------------------------------------------------------------
# Equipment Category master
# ----------------------------------------------------------------------
@equipment_bp.route("/categories")
@login_required
def list_categories():
    categories = EquipmentCategory.query.order_by(EquipmentCategory.name).all()
    return render_template("equipment/categories.html", categories=categories)


@equipment_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_category():
    form = EquipmentCategoryForm()
    if form.validate_on_submit():
        category = EquipmentCategory()
        form.populate_obj(category)
        db.session.add(category)
        db.session.commit()
        AuditService.log("CREATE", "EquipmentCategory", category.id, f"Created category {category.code}")
        flash("Equipment category created.", "success")
        return redirect(url_for("equipment.list_categories"))
    return render_template("equipment/category_form.html", form=form, title="New Equipment Category")


# ----------------------------------------------------------------------
# File uploads: photos / documents / drawings
# ----------------------------------------------------------------------
@equipment_bp.route("/<int:equipment_id>/upload/photo", methods=["POST"])
@login_required
@editor_required
def upload_photo(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    form = PhotoUploadForm()
    file = request.files.get("photo")
    if file and file.filename and allowed_image(file.filename):
        stored_name, original_name = save_uploaded_file(file, current_app.config["PHOTO_FOLDER"])
        photo = Photo(
            equipment_id=eq.id, uploaded_by_id=current_user.id,
            filename=stored_name, original_filename=original_name, caption=form.caption.data,
        )
        db.session.add(photo)
        db.session.commit()
        AuditService.log("CREATE", "Photo", photo.id, f"Uploaded photo for equipment {eq.equipment_code}")
        flash("Photo uploaded successfully.", "success")
    else:
        flash("Please select a valid image file (png, jpg, jpeg, gif, webp).", "danger")
    return redirect(url_for("equipment.detail", equipment_id=equipment_id))


@equipment_bp.route("/<int:equipment_id>/upload/document", methods=["POST"])
@login_required
@editor_required
def upload_document(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    form = DocumentUploadForm()
    file = request.files.get("document")
    if file and file.filename and allowed_document(file.filename):
        stored_name, original_name = save_uploaded_file(file, current_app.config["DOCUMENT_FOLDER"])
        document = Document(
            equipment_id=eq.id, uploaded_by_id=current_user.id,
            filename=stored_name, original_filename=original_name, document_type=form.document_type.data,
        )
        db.session.add(document)
        db.session.commit()
        AuditService.log("CREATE", "Document", document.id, f"Uploaded document for equipment {eq.equipment_code}")
        flash("Document uploaded successfully.", "success")
    else:
        flash("Please select a valid document file.", "danger")
    return redirect(url_for("equipment.detail", equipment_id=equipment_id))


@equipment_bp.route("/<int:equipment_id>/upload/drawing", methods=["POST"])
@login_required
@editor_required
def upload_drawing(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    require_equipment_access(eq)
    form = DrawingUploadForm()
    file = request.files.get("drawing")
    if file and file.filename and allowed_drawing(file.filename):
        stored_name, original_name = save_uploaded_file(file, current_app.config["DRAWING_FOLDER"])
        drawing = Drawing(
            equipment_id=eq.id, uploaded_by_id=current_user.id,
            filename=stored_name, original_filename=original_name,
            drawing_number=form.drawing_number.data, revision=form.revision.data,
        )
        db.session.add(drawing)
        db.session.commit()
        AuditService.log("CREATE", "Drawing", drawing.id, f"Uploaded drawing for equipment {eq.equipment_code}")
        flash("Drawing uploaded successfully.", "success")
    else:
        flash("Please select a valid drawing file.", "danger")
    return redirect(url_for("equipment.detail", equipment_id=equipment_id))


@equipment_bp.route("/files/photos/<path:filename>")
@login_required
def serve_photo(filename):
    return send_from_directory(current_app.config["PHOTO_FOLDER"], filename)


@equipment_bp.route("/files/documents/<path:filename>")
@login_required
def serve_document(filename):
    return send_from_directory(current_app.config["DOCUMENT_FOLDER"], filename, as_attachment=True)


@equipment_bp.route("/files/drawings/<path:filename>")
@login_required
def serve_drawing(filename):
    return send_from_directory(current_app.config["DRAWING_FOLDER"], filename)


# ----------------------------------------------------------------------
# Excel Import / Export
# ----------------------------------------------------------------------
@equipment_bp.route("/export/excel")
@login_required
def export_excel():
    project_ids = [p.id for p in get_accessible_projects().all()]

    equipment_items = (
        Equipment.query
        .join(Equipment.system)
        .join(System.area)
        .join(Area.unit)
        .filter(Unit.project_id.in_(project_ids))
        .all()
    )
    buffer = ExcelService.export_equipment(equipment_items)
    return send_file(
        buffer, as_attachment=True, download_name="equipment_master_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@equipment_bp.route("/import/template")
@login_required
def import_template():
    buffer = ExcelService.generate_import_template()
    return send_file(
        buffer, as_attachment=True, download_name="equipment_import_template.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@equipment_bp.route("/import/excel", methods=["GET", "POST"])
@login_required
@editor_required
def import_excel():
    if request.method == "POST":
        file = request.files.get("import_file")
        if not file or not file.filename.endswith((".xlsx", ".xls")):
            flash("Please upload a valid .xlsx file.", "danger")
            return redirect(url_for("equipment.import_excel"))
        result = ExcelService.import_equipment(file)
        AuditService.log(
            "IMPORT", "Equipment", None,
            f"Excel import: {result['created']} created, {result['updated']} updated, "
            f"{len(result['errors'])} errors.",
        )
        flash(
            f"Import complete: {result['created']} created, {result['updated']} updated.",
            "success" if not result["errors"] else "warning",
        )
        return render_template("equipment/import_result.html", result=result)
    return render_template("equipment/import.html")

"""
app/routes/vendors.py
------------------------
Vendor master CRUD blueprint with search and pagination.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required

from app.extensions import db
from app.models.vendor import Vendor
from app.forms.vendor_forms import VendorForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService

vendors_bp = Blueprint("vendors", __name__, url_prefix="/vendors")


@vendors_bp.route("/")
@login_required
def list_vendors():
    search = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Vendor.query
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Vendor.name.ilike(like), Vendor.vendor_code.ilike(like)))

    pagination = query.order_by(Vendor.name).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    return render_template("vendors/list.html", pagination=pagination, vendors=pagination.items, search=search)


@vendors_bp.route("/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor()
        form.populate_obj(vendor)
        db.session.add(vendor)
        db.session.commit()
        AuditService.log("CREATE", "Vendor", vendor.id, f"Created vendor {vendor.vendor_code}")
        flash("Vendor created successfully.", "success")
        return redirect(url_for("vendors.list_vendors"))
    return render_template("vendors/form.html", form=form, title="New Vendor")


@vendors_bp.route("/<int:vendor_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    form = VendorForm(obj=vendor)
    if form.validate_on_submit():
        form.populate_obj(vendor)
        db.session.commit()
        AuditService.log("UPDATE", "Vendor", vendor.id, f"Updated vendor {vendor.vendor_code}")
        flash("Vendor updated successfully.", "success")
        return redirect(url_for("vendors.list_vendors"))
    return render_template("vendors/form.html", form=form, title="Edit Vendor", vendor=vendor)


@vendors_bp.route("/<int:vendor_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    code = vendor.vendor_code
    db.session.delete(vendor)
    db.session.commit()
    AuditService.log("DELETE", "Vendor", vendor_id, f"Deleted vendor {code}")
    flash("Vendor deleted.", "info")
    return redirect(url_for("vendors.list_vendors"))

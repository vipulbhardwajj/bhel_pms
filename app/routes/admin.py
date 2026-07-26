"""
app/routes/admin.py
----------------------
Administrative blueprint restricted to the Admin role: user account
management and audit log viewer.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User, Role
from app.models.audit import AuditLog
from app.forms.auth_forms import UserForm
from app.utils.decorators import admin_required
from app.services.audit_service import AuditService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.full_name).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            employee_code=form.employee_code.data,
            full_name=form.full_name.data,
            email=form.email.data,
            username=form.username.data,
            role=form.role.data,
            department=form.department.data,
            designation=form.designation.data,
            phone=form.phone.data,
            is_active=form.is_active.data,
        )
        user.set_password(form.password.data or "Bhel@1234")
        db.session.add(user)
        db.session.commit()
        AuditService.log("CREATE", "User", user.id, f"Created user {user.username}")
        flash("User account created successfully.", "success")
        return redirect(url_for("admin.list_users"))
    return render_template("admin/user_form.html", form=form, title="New User")


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.employee_code = form.employee_code.data
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.username = form.username.data
        user.role = form.role.data
        user.department = form.department.data
        user.designation = form.designation.data
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        AuditService.log("UPDATE", "User", user.id, f"Updated user {user.username}")
        flash("User account updated successfully.", "success")
        return redirect(url_for("admin.list_users"))
    return render_template("admin/user_form.html", form=form, title="Edit User", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.list_users"))
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    AuditService.log("DELETE", "User", user_id, f"Deleted user {username}")
    flash("User account deleted.", "info")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/audit-logs")
@login_required
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    return render_template("admin/audit_logs.html", pagination=pagination, logs=pagination.items)

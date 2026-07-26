"""
app/utils/decorators.py
-------------------------
Custom route decorators implementing Role Based Access Control (RBAC) on top
of Flask-Login's `login_required`.

Usage:
    @roles_required(Role.ADMIN)
    def admin_only_view(): ...

    @editor_required   # Admin or Engineer
    def create_equipment(): ...
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.models.user import Role


def roles_required(*allowed_roles):
    """Restrict a view to one or more roles. Aborts with 403 otherwise."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in allowed_roles:
                flash("You do not have permission to access that page.", "danger")
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


def editor_required(view_func):
    """Shortcut decorator: allows Admin & Engineer, blocks Viewer."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.can_edit():
            flash("Viewers have read-only access. This action is restricted.", "danger")
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Shortcut decorator: Admin only."""
    return roles_required(Role.ADMIN)(view_func)

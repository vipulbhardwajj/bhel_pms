"""
app/routes/progress.py
-------------------------
Daily / Weekly / Monthly progress tracking blueprint. Logging a progress
entry also updates the parent Equipment's live progress percentages, which
then cascade up the hierarchy (System -> Area -> Unit -> Project).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.equipment import Equipment
from app.models.progress import DailyProgress, WeeklyProgress, MonthlyProgress
from app.forms.progress_forms import DailyProgressForm, WeeklyProgressForm, MonthlyProgressForm
from app.utils.decorators import editor_required
from app.services.audit_service import AuditService

progress_bp = Blueprint("progress", __name__, url_prefix="/progress")


def _populate_equipment_choices(form):
    form.equipment_id.choices = [
        (e.id, f"{e.equipment_code} - {e.equipment_name}") for e in Equipment.query.order_by(Equipment.equipment_name)
    ]


def _cascade_progress(equipment: Equipment):
    """Push updated progress upward through System -> Area -> Unit -> Project."""
    system = equipment.system
    system.recalculate_progress()
    area = system.area
    area.recalculate_progress()
    unit = area.unit
    unit.recalculate_progress()
    project = unit.project
    project.recalculate_progress()
    db.session.commit()


# ----------------------------------------------------------------------
# Daily Progress
# ----------------------------------------------------------------------
@progress_bp.route("/daily")
@login_required
def list_daily():
    page = request.args.get("page", 1, type=int)
    pagination = DailyProgress.query.order_by(DailyProgress.log_date.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    return render_template("progress/daily.html", pagination=pagination, logs=pagination.items)


@progress_bp.route("/daily/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_daily():
    form = DailyProgressForm()
    _populate_equipment_choices(form)
    if form.validate_on_submit():
        log = DailyProgress(logged_by_id=current_user.id)
        form.populate_obj(log)
        db.session.add(log)

        equipment = Equipment.query.get(form.equipment_id.data)
        equipment.installation_progress = form.installation_progress.data
        equipment.commissioning_progress = form.commissioning_progress.data
        db.session.commit()
        _cascade_progress(equipment)

        AuditService.log("CREATE", "DailyProgress", log.id, f"Daily progress logged for {equipment.equipment_code}")
        flash("Daily progress logged successfully.", "success")
        return redirect(url_for("progress.list_daily"))
    return render_template("progress/daily_form.html", form=form, title="Log Daily Progress")


# ----------------------------------------------------------------------
# Weekly Progress
# ----------------------------------------------------------------------
@progress_bp.route("/weekly")
@login_required
def list_weekly():
    page = request.args.get("page", 1, type=int)
    pagination = WeeklyProgress.query.order_by(WeeklyProgress.week_start_date.desc()).paginate(
        page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False
    )
    return render_template("progress/weekly.html", pagination=pagination, logs=pagination.items)


@progress_bp.route("/weekly/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_weekly():
    form = WeeklyProgressForm()
    _populate_equipment_choices(form)
    if form.validate_on_submit():
        log = WeeklyProgress(logged_by_id=current_user.id)
        form.populate_obj(log)
        db.session.add(log)
        db.session.commit()
        AuditService.log("CREATE", "WeeklyProgress", log.id, "Weekly progress logged.")
        flash("Weekly progress logged successfully.", "success")
        return redirect(url_for("progress.list_weekly"))
    return render_template("progress/weekly_form.html", form=form, title="Log Weekly Progress")


# ----------------------------------------------------------------------
# Monthly Progress
# ----------------------------------------------------------------------
@progress_bp.route("/monthly")
@login_required
def list_monthly():
    page = request.args.get("page", 1, type=int)
    pagination = MonthlyProgress.query.order_by(
        MonthlyProgress.year.desc(), MonthlyProgress.month.desc()
    ).paginate(page=page, per_page=current_app.config["ITEMS_PER_PAGE"], error_out=False)
    return render_template("progress/monthly.html", pagination=pagination, logs=pagination.items)


@progress_bp.route("/monthly/create", methods=["GET", "POST"])
@login_required
@editor_required
def create_monthly():
    form = MonthlyProgressForm()
    _populate_equipment_choices(form)
    if form.validate_on_submit():
        log = MonthlyProgress(logged_by_id=current_user.id)
        form.populate_obj(log)
        db.session.add(log)
        db.session.commit()
        AuditService.log("CREATE", "MonthlyProgress", log.id, "Monthly progress logged.")
        flash("Monthly progress logged successfully.", "success")
        return redirect(url_for("progress.list_monthly"))
    return render_template("progress/monthly_form.html", form=form, title="Log Monthly Progress")

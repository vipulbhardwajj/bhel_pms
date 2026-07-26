"""
app/forms/progress_forms.py
-------------------------------
Forms for logging Daily, Weekly and Monthly progress against an Equipment.
"""

from flask_wtf import FlaskForm
from wtforms import (
    SelectField, FloatField, DateField, TextAreaField, IntegerField
)
from wtforms.validators import DataRequired, Optional, NumberRange


class DailyProgressForm(FlaskForm):
    equipment_id = SelectField("Equipment", coerce=int, validators=[DataRequired()])
    log_date = DateField("Date", validators=[DataRequired()])
    installation_progress = FloatField(
        "Installation Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    commissioning_progress = FloatField(
        "Commissioning Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    activity_description = TextAreaField("Activity Description", validators=[Optional()])
    manpower_deployed = IntegerField("Manpower Deployed", validators=[Optional(), NumberRange(min=0)])
    hindrances = TextAreaField("Hindrances / Issues", validators=[Optional()])


class WeeklyProgressForm(FlaskForm):
    equipment_id = SelectField("Equipment", coerce=int, validators=[DataRequired()])
    week_start_date = DateField("Week Start Date", validators=[DataRequired()])
    week_end_date = DateField("Week End Date", validators=[DataRequired()])
    planned_progress = FloatField("Planned Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_progress = FloatField("Actual Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)])
    summary = TextAreaField("Summary", validators=[Optional()])


class MonthlyProgressForm(FlaskForm):
    equipment_id = SelectField("Equipment", coerce=int, validators=[DataRequired()])
    month = SelectField("Month", coerce=int, choices=[(i, i) for i in range(1, 13)], validators=[DataRequired()])
    year = IntegerField("Year", validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    planned_progress = FloatField("Planned Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)])
    actual_progress = FloatField("Actual Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)])
    summary = TextAreaField("Summary", validators=[Optional()])

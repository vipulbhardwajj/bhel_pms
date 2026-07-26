"""
app/forms/project_forms.py
-----------------------------
Forms for the Project -> Unit -> Area -> System hierarchy.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    DateField,
    SelectField,
    SelectMultipleField,
    TextAreaField
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange

from app.models.project import ProjectStatus
from app.models.user import User, Role


class ProjectForm(FlaskForm):

    project_code = StringField("Project Code", validators=[DataRequired(), Length(max=30)])
    name = StringField("Project Name", validators=[DataRequired(), Length(max=200)])
    client_name = StringField("Client", validators=[Optional(), Length(max=200)])
    location = StringField("Location", validators=[Optional(), Length(max=200)])
    capacity_mw = FloatField("Capacity (MW)", validators=[Optional(), NumberRange(min=0)])
    contract_value_crore = FloatField("Contract Value (INR Crore)", validators=[Optional(), NumberRange(min=0)])
    start_date = DateField("Start Date", validators=[Optional()])
    scheduled_end_date = DateField("Scheduled End Date", validators=[Optional()])
    actual_end_date = DateField("Actual End Date", validators=[Optional()])
    status = SelectField("Status", choices=[(s, s) for s in ProjectStatus.ALL], validators=[DataRequired()])
    project_manager = StringField("Project Manager", validators=[Optional(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional()])

    assigned_engineers = SelectMultipleField(
        "Assign Engineers",
        coerce=int,
        validators=[Optional()]
    )

    def load_engineers(self):
        engineers = User.query.filter_by(role=Role.ENGINEER).order_by(User.full_name).all()

        self.assigned_engineers.choices = [
            (e.id, f"{e.full_name} ({e.employee_code})")
            for e in engineers
        ]

class UnitForm(FlaskForm):
    project_id = SelectField("Project", coerce=int, validators=[DataRequired()])
    name = StringField("Unit Name", validators=[DataRequired(), Length(max=120)])
    unit_code = StringField("Unit Code", validators=[DataRequired(), Length(max=30)])
    capacity_mw = FloatField("Capacity (MW)", validators=[Optional(), NumberRange(min=0)])


class AreaForm(FlaskForm):
    unit_id = SelectField("Unit", coerce=int, validators=[DataRequired()])
    name = StringField("Area Name", validators=[DataRequired(), Length(max=120)])
    area_code = StringField("Area Code", validators=[DataRequired(), Length(max=30)])
    description = TextAreaField("Description", validators=[Optional()])


class SystemForm(FlaskForm):
    area_id = SelectField("Area", coerce=int, validators=[DataRequired()])
    name = StringField("System Name", validators=[DataRequired(), Length(max=120)])
    system_code = StringField("System Code", validators=[DataRequired(), Length(max=30)])
    description = TextAreaField("Description", validators=[Optional()])

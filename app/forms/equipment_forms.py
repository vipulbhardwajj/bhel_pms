"""
app/forms/equipment_forms.py
--------------------------------
Forms for Equipment Category master and the Equipment master record itself.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, SelectField, FloatField, DateField, TextAreaField, IntegerField
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from app.models.equipment import EquipmentStatus


class EquipmentCategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(max=120)])
    code = StringField("Category Code", validators=[DataRequired(), Length(max=20)])
    description = TextAreaField("Description", validators=[Optional()])


class EquipmentForm(FlaskForm):
    system_id = SelectField("System", coerce=int, validators=[DataRequired()])
    category_id = SelectField("Equipment Category", coerce=int, validators=[Optional()])
    vendor_id = SelectField("Vendor", coerce=int, validators=[Optional()])
    assigned_engineer_id = SelectField("Assigned Engineer", coerce=int, validators=[Optional()])

    equipment_name = StringField("Equipment Name", validators=[DataRequired(), Length(max=200)])
    equipment_code = StringField("Equipment Code", validators=[DataRequired(), Length(max=50)])
    drawing_number = StringField("Drawing Number", validators=[Optional(), Length(max=100)])
    po_number = StringField("PO Number", validators=[Optional(), Length(max=100)])
    status = SelectField("Status", choices=[(s, s) for s in EquipmentStatus.ALL], validators=[DataRequired()])

    installation_progress = FloatField(
        "Installation Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)], default=0
    )
    commissioning_progress = FloatField(
        "Commissioning Progress (%)", validators=[DataRequired(), NumberRange(min=0, max=100)], default=0
    )

    remarks = TextAreaField("Remarks", validators=[Optional()])
    expected_date = DateField("Expected Date", validators=[Optional()])
    actual_date = DateField("Actual Date", validators=[Optional()])


class PhotoUploadForm(FlaskForm):
    photo = FileField(
        "Photo", validators=[FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only!")]
    )
    caption = StringField("Caption", validators=[Optional(), Length(max=255)])


class DocumentUploadForm(FlaskForm):
    document = FileField(
        "Document",
        validators=[FileAllowed(["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"], "Invalid file type!")],
    )
    document_type = StringField("Document Type", validators=[Optional(), Length(max=100)])


class DrawingUploadForm(FlaskForm):
    drawing = FileField(
        "Drawing",
        validators=[FileAllowed(["pdf", "dwg", "dxf", "png", "jpg", "jpeg"], "Invalid file type!")],
    )
    drawing_number = StringField("Drawing Number", validators=[Optional(), Length(max=100)])
    revision = StringField("Revision", validators=[Optional(), Length(max=20)])

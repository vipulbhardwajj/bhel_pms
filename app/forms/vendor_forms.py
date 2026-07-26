"""
app/forms/vendor_forms.py
-----------------------------
Form for the Vendor master.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email


class VendorForm(FlaskForm):
    name = StringField("Vendor Name", validators=[DataRequired(), Length(max=200)])
    vendor_code = StringField("Vendor Code", validators=[DataRequired(), Length(max=30)])
    contact_person = StringField("Contact Person", validators=[Optional(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional()])
    gst_number = StringField("GST Number", validators=[Optional(), Length(max=30)])
    specialization = StringField("Specialization", validators=[Optional(), Length(max=200)])
    rating = FloatField("Rating (0-5)", validators=[Optional(), NumberRange(min=0, max=5)], default=0)
    is_active = BooleanField("Active", default=True)

"""
app/forms/auth_forms.py
--------------------------
WTForms definitions for login and user account management.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from app.models.user import Role


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")


class UserForm(FlaskForm):
    """Used by Admins to create / edit user accounts."""

    employee_code = StringField("Employee Code", validators=[DataRequired(), Length(max=20)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField(
        "Password",
        validators=[Optional(), Length(min=6, message="Password must be at least 6 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[EqualTo("password", message="Passwords must match.")]
    )
    role = SelectField("Role", choices=[(r, r) for r in Role.ALL], validators=[DataRequired()])
    department = StringField("Department", validators=[Optional(), Length(max=120)])
    designation = StringField("Designation", validators=[Optional(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    is_active = BooleanField("Active", default=True)

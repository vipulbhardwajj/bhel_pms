from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt
from app.models.association import user_projects

class Role:
    """Simple string constants for user roles (kept out of an Enum so raw
    SQL / seed scripts can use plain strings without importing the class)."""

    ADMIN = "Admin"
    ENGINEER = "Engineer"
    VIEWER = "Viewer"

    ALL = [ADMIN, ENGINEER, VIEWER]


class User(UserMixin, db.Model):
    """Represents an application user / employee account."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.VIEWER)
    department = db.Column(db.String(120))
    designation = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    profile_photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)

    # --- Relationships ---

    assigned_projects = db.relationship(
    "Project",
    secondary=user_projects,
    back_populates="assigned_engineers",
)
    assigned_equipment = db.relationship(
        "Equipment", backref="assigned_engineer", foreign_keys="Equipment.assigned_engineer_id"
    )
    audit_logs = db.relationship("AuditLog", backref="user", lazy="dynamic")
    notifications = db.relationship("Notification", backref="recipient", lazy="dynamic")

    def set_password(self, raw_password: str) -> None:
        """Hash and store the given plaintext password."""
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, raw_password)

   
    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_engineer(self) -> bool:
        return self.role == Role.ENGINEER

    @property
    def is_viewer(self) -> bool:
        return self.role == Role.VIEWER

    def can_edit(self) -> bool:
        """Admins and Engineers may create/update records; Viewers cannot."""
        return self.role in (Role.ADMIN, Role.ENGINEER)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

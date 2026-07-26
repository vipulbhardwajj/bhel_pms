"""
app/models/__init__.py
------------------------
Aggregates all SQLAlchemy models so they can be imported simply via
`from app.models import User, Project, Equipment, ...` and so that
Flask-Migrate / `db.create_all()` sees every mapped class.
"""

from app.models.user import User, Role
from app.models.project import Project, ProjectStatus
from app.models.hierarchy import Unit, Area, System
from app.models.equipment import EquipmentCategory, Equipment, EquipmentStatus
from app.models.vendor import Vendor
from app.models.progress import DailyProgress, WeeklyProgress, MonthlyProgress
from app.models.documents import Photo, Document, Drawing
from app.models.notification import Notification, NotificationType
from app.models.audit import AuditLog
from app.models.association import user_projects

__all__ = [
    "User", "Role",
    "Project", "ProjectStatus",
    "Unit", "Area", "System",
    "EquipmentCategory", "Equipment", "EquipmentStatus",
    "Vendor",
    "DailyProgress", "WeeklyProgress", "MonthlyProgress",
    "Photo", "Document", "Drawing",
    "Notification", "NotificationType",
    "AuditLog",
    "user_projects",
]

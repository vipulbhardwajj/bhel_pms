from app.models.project import Project
from app.models.user import User
from flask_login import current_user


def get_accessible_projects():
    """
    Returns a SQLAlchemy query containing only projects
    the logged-in user is allowed to access.
    """

    if current_user.is_admin:
        return Project.query

    if current_user.is_engineer:
        return (
            Project.query
            .join(Project.assigned_engineers)
            .filter(User.id == current_user.id)
        )

    # Viewer
    return Project.query
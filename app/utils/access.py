from flask import abort
from flask_login import current_user

from app.models.project import Project
from app.models.hierarchy import Unit, Area, System
from app.models.equipment import Equipment

from flask_login import current_user


def has_project_access(project_id):

    if current_user.is_admin:
        return True

    return any(
        project.id == project_id
        for project in current_user.assigned_projects
    )

def require_project_access(project_id):

    if not has_project_access(project_id):
        abort(403)


def require_equipment_access(equipment):

    project_id = (
        equipment.system
        .area
        .unit
        .project_id
    )

    require_project_access(project_id)


def require_system_access(system):

    project_id = (
        system.area
        .unit
        .project_id
    )

    require_project_access(project_id)


def require_area_access(area):

    project_id = (
        area.unit
        .project_id
    )

    require_project_access(project_id)


def require_unit_access(unit):

    require_project_access(unit.project_id)
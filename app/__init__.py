import os
from flask import Flask, render_template
from config import config_by_name

from app.extensions import db, login_manager, bcrypt, migrate


def create_app(config_name=None):
    """Application factory. `config_name` selects development / production /
    testing configuration; defaults to the APP_ENV environment variable."""

    config_name = config_name or os.environ.get("APP_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["PHOTO_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DOCUMENT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DRAWING_FOLDER"], exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_template_helpers(app)
    _register_error_handlers(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def _register_blueprints(app):
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.projects import projects_bp
    from app.routes.units import units_bp
    from app.routes.areas import areas_bp
    from app.routes.systems import systems_bp
    from app.routes.equipment import equipment_bp
    from app.routes.vendors import vendors_bp
    from app.routes.progress import progress_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(areas_bp)
    app.register_blueprint(systems_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Redirect app root to the dashboard (or login if unauthenticated)
    from flask import redirect, url_for
    from flask_login import current_user

    @app.route("/")
    def root():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))


def _register_template_helpers(app):
    from app.utils.helpers import format_date, format_datetime, days_until

    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_datetime"] = format_datetime
    app.jinja_env.filters["days_until"] = days_until

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            "app_name": app.config["APPLICATION_NAME"],
            "app_short_name": app.config["APPLICATION_SHORT_NAME"],
            "org_name": app.config["ORGANIZATION_NAME"],
            "current_year": datetime.utcnow().year,
        }


def _register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
   

    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "bhel-pms-dev-secret-key-change-in-production")
    JSON_SORT_KEYS = False

    # --- SQLAlchemy ---
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Uploads ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    PHOTO_FOLDER = os.path.join(UPLOAD_FOLDER, "photos")
    DOCUMENT_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
    DRAWING_FOLDER = os.path.join(UPLOAD_FOLDER, "drawings")
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB upload limit
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"}
    ALLOWED_DRAWING_EXTENSIONS = {"pdf", "dwg", "dxf", "png", "jpg", "jpeg"}

    # --- Session / Auth ---
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # --- Pagination ---
    ITEMS_PER_PAGE = 15

    # --- Company / Branding ---
    ORGANIZATION_NAME = "Bharat Heavy Electricals Limited"
    APPLICATION_NAME = "BHEL Project Monitoring System"
    APPLICATION_SHORT_NAME = "BHEL PMS"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "bhel_pms_dev.db")
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://bhel_user:bhel_password@localhost:5432/bhel_pms",
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

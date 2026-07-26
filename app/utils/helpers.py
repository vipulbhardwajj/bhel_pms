"""
app/utils/helpers.py
----------------------
Miscellaneous helper functions shared across routes and services: secure
file saving with UUID renaming, request metadata, and simple formatting
helpers exposed to Jinja templates via app/__init__.py context processors.
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request


def save_uploaded_file(file_storage, destination_folder: str) -> tuple:
    """
    Persist an uploaded werkzeug FileStorage object to disk using a
    collision-proof UUID based filename while preserving the original
    extension. Returns a tuple of (stored_filename, original_filename).
    """
    original_filename = secure_filename(file_storage.filename)
    extension = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    stored_filename = f"{uuid.uuid4().hex}.{extension}" if extension else uuid.uuid4().hex

    os.makedirs(destination_folder, exist_ok=True)
    file_storage.save(os.path.join(destination_folder, stored_filename))
    return stored_filename, original_filename


def get_client_ip() -> str:
    """Best-effort extraction of the client IP address, respecting proxies."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "unknown"


def generate_code(prefix: str, existing_count: int) -> str:
    """Generate a simple sequential master-data code, e.g. VEN-0001."""
    return f"{prefix}-{existing_count + 1:04d}"


def format_date(value):
    """Jinja filter: format a date/datetime as DD-MMM-YYYY (e.g. 19-Jul-2026)."""
    if not value:
        return "-"
    return value.strftime("%d-%b-%Y")


def format_datetime(value):
    """Jinja filter: format a datetime as DD-MMM-YYYY HH:MM."""
    if not value:
        return "-"
    return value.strftime("%d-%b-%Y %H:%M")


def days_until(value):
    """Return the (possibly negative) number of days between today and value."""
    if not value:
        return None
    delta = value - datetime.utcnow().date()
    return delta.days

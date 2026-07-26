"""
app/utils/validators.py
-------------------------
Small reusable validation helpers used by forms and services.
"""

import os
from flask import current_app


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Return True if the filename's extension is within the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def allowed_image(filename: str) -> bool:
    return allowed_file(filename, current_app.config["ALLOWED_IMAGE_EXTENSIONS"])


def allowed_document(filename: str) -> bool:
    return allowed_file(filename, current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"])


def allowed_drawing(filename: str) -> bool:
    return allowed_file(filename, current_app.config["ALLOWED_DRAWING_EXTENSIONS"])


def is_valid_progress(value) -> bool:
    """Progress percentages must be numeric and within 0-100."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return 0 <= v <= 100

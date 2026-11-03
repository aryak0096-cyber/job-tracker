"""Shared input validation for the HTML forms and the JSON API."""

from datetime import date, datetime

from .database import STATUSES


def clean_application(data, require_all=True):
    """Return (cleaned_dict, errors). `data` is a dict-like of raw input."""
    errors = {}
    cleaned = {}

    for field in ("company", "role"):
        value = (data.get(field) or "").strip()
        if not value:
            errors[field] = "This field is required."
        elif len(value) > 120:
            errors[field] = "Keep this under 120 characters."
        cleaned[field] = value

    status = (data.get("status") or "Applied").strip()
    if status not in STATUSES:
        errors["status"] = f"Status must be one of: {', '.join(STATUSES)}."
    cleaned["status"] = status

    applied = (data.get("applied_date") or "").strip() or date.today().isoformat()
    try:
        datetime.strptime(applied, "%Y-%m-%d")
    except ValueError:
        errors["applied_date"] = "Use the format YYYY-MM-DD."
    cleaned["applied_date"] = applied

    job_url = (data.get("job_url") or "").strip()
    if job_url and not job_url.lower().startswith(("http://", "https://")):
        errors["job_url"] = "URL must start with http:// or https://"
    cleaned["job_url"] = job_url

    cleaned["job_description"] = (data.get("job_description") or "").strip()
    cleaned["notes"] = (data.get("notes") or "").strip()
    return cleaned, errors

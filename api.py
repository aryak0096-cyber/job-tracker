"""JSON REST API under /api."""

from flask import Blueprint, jsonify, request

from . import analyzer, database
from .validation import clean_application

bp = Blueprint("api", __name__, url_prefix="/api")


def _error(message, status=400, **extra):
    return jsonify({"error": message, **extra}), status


@bp.get("/applications")
def list_applications():
    rows = database.list_applications(
        status=request.args.get("status") or None,
        search=(request.args.get("q") or "").strip() or None,
    )
    return jsonify([dict(r) for r in rows])


@bp.post("/applications")
def create_application():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object.")
    cleaned, errors = clean_application(payload)
    if errors:
        return _error("Validation failed.", 422, fields=errors)
    app_id = database.create_application(cleaned)
    return jsonify(database.row_to_dict(database.get_application(app_id))), 201


@bp.get("/applications/<int:app_id>")
def get_application(app_id):
    row = database.get_application(app_id)
    if row is None:
        return _error("Application not found.", 404)
    return jsonify(dict(row))


@bp.put("/applications/<int:app_id>")
def update_application(app_id):
    if database.get_application(app_id) is None:
        return _error("Application not found.", 404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object.")
    cleaned, errors = clean_application(payload)
    if errors:
        return _error("Validation failed.", 422, fields=errors)
    database.update_application(app_id, cleaned)
    return jsonify(database.row_to_dict(database.get_application(app_id)))


@bp.delete("/applications/<int:app_id>")
def delete_application(app_id):
    if database.get_application(app_id) is None:
        return _error("Application not found.", 404)
    database.delete_application(app_id)
    return "", 204


@bp.get("/stats")
def stats():
    return jsonify(database.application_stats())


@bp.post("/analyze")
def analyze():
    """Body: {"job_description": "..."}; uses the latest uploaded resume."""
    payload = request.get_json(silent=True) or {}
    job_description = (payload.get("job_description") or "").strip()
    if not job_description:
        return _error("job_description is required.", 422)
    resume = database.latest_resume()
    if resume is None:
        return _error("Upload a resume first.", 409)
    return jsonify(analyzer.compare(resume["skills"], job_description))

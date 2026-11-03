"""HTML pages."""

from collections import Counter

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from . import analyzer, database
from .database import STATUSES
from .validation import clean_application

bp = Blueprint("views", __name__)


@bp.route("/")
def dashboard():
    stats = database.application_stats()
    resume = database.latest_resume()

    top_missing = []
    if resume:
        counter = Counter()
        for app_row in database.list_applications():
            if app_row["job_description"]:
                result = analyzer.compare(resume["skills"], app_row["job_description"])
                counter.update(result["missing"])
        top_missing = counter.most_common(8)

    recent = database.list_applications()[:5]
    return render_template(
        "dashboard.html",
        stats=stats,
        resume=resume,
        top_missing=top_missing,
        recent=recent,
        statuses=STATUSES,
    )


# ---------------------------------------------------------------- applications

@bp.route("/applications")
def applications():
    status = request.args.get("status") or None
    search = (request.args.get("q") or "").strip() or None
    rows = database.list_applications(status=status, search=search)
    return render_template(
        "applications.html",
        applications=rows,
        statuses=STATUSES,
        current_status=status,
        query=search or "",
    )


@bp.route("/applications/new", methods=("GET", "POST"))
def new_application():
    if request.method == "POST":
        cleaned, errors = clean_application(request.form)
        if not errors:
            app_id = database.create_application(cleaned)
            flash("Application added.", "success")
            return redirect(url_for("views.application_detail", app_id=app_id))
        return render_template(
            "application_form.html", form=cleaned, errors=errors, statuses=STATUSES, editing=False
        ), 400
    return render_template(
        "application_form.html", form={}, errors={}, statuses=STATUSES, editing=False
    )


@bp.route("/applications/<int:app_id>")
def application_detail(app_id):
    row = database.get_application(app_id)
    if row is None:
        abort(404)
    resume = database.latest_resume()
    analysis = None
    if resume and row["job_description"]:
        analysis = analyzer.compare(resume["skills"], row["job_description"])
    return render_template(
        "application_detail.html",
        application=row,
        resume=resume,
        analysis=analysis,
        statuses=STATUSES,
    )


@bp.route("/applications/<int:app_id>/edit", methods=("GET", "POST"))
def edit_application(app_id):
    row = database.get_application(app_id)
    if row is None:
        abort(404)
    if request.method == "POST":
        cleaned, errors = clean_application(request.form)
        if not errors:
            database.update_application(app_id, cleaned)
            flash("Application updated.", "success")
            return redirect(url_for("views.application_detail", app_id=app_id))
        return render_template(
            "application_form.html", form=cleaned, errors=errors, statuses=STATUSES, editing=True
        ), 400
    return render_template(
        "application_form.html", form=dict(row), errors={}, statuses=STATUSES, editing=True
    )


@bp.route("/applications/<int:app_id>/status", methods=("POST",))
def change_status(app_id):
    if database.get_application(app_id) is None:
        abort(404)
    status = request.form.get("status")
    if status not in STATUSES:
        abort(400)
    database.set_status(app_id, status)
    flash(f"Status changed to {status}.", "success")
    return redirect(request.referrer or url_for("views.applications"))


@bp.route("/applications/<int:app_id>/delete", methods=("POST",))
def delete_application(app_id):
    if database.get_application(app_id) is None:
        abort(404)
    database.delete_application(app_id)
    flash("Application deleted.", "success")
    return redirect(url_for("views.applications"))


# ---------------------------------------------------------------------- resume

@bp.route("/resume", methods=("GET", "POST"))
def resume():
    if request.method == "POST":
        uploaded = request.files.get("resume")
        if uploaded is None or not uploaded.filename:
            flash("Choose a PDF file first.", "error")
            return redirect(url_for("views.resume"))
        if not uploaded.filename.lower().endswith(".pdf"):
            flash("Only PDF files are supported.", "error")
            return redirect(url_for("views.resume"))
        try:
            text = analyzer.extract_text_from_pdf(uploaded.stream)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("views.resume"))

        skills = analyzer.extract_skills(text)
        database.save_resume(uploaded.filename, text, skills)
        flash(f"Resume analysed: {len(skills)} skills found.", "success")
        return redirect(url_for("views.resume"))

    current = database.latest_resume()
    grouped = analyzer.group_by_category(current["skills"]) if current else {}
    return render_template("resume.html", resume=current, grouped=grouped)


# --------------------------------------------------------------------- analyzer

@bp.route("/analyze", methods=("GET", "POST"))
def analyze():
    """Paste any job description and compare it with the uploaded resume."""
    resume_row = database.latest_resume()
    analysis = None
    job_description = ""
    if request.method == "POST":
        job_description = request.form.get("job_description", "").strip()
        if not resume_row:
            flash("Upload a resume first.", "error")
            return redirect(url_for("views.resume"))
        if not job_description:
            flash("Paste a job description to analyse.", "error")
        else:
            analysis = analyzer.compare(resume_row["skills"], job_description)
    return render_template(
        "analyze.html", resume=resume_row, analysis=analysis, job_description=job_description
    )

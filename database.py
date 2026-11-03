"""SQLite helpers: connection handling, schema and queries."""

import json
import sqlite3
from datetime import date

from flask import current_app, g

STATUSES = ["Wishlist", "Applied", "Interview", "Offer", "Rejected", "Withdrawn"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    company       TEXT NOT NULL,
    role          TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'Applied',
    applied_date  TEXT NOT NULL,
    job_url       TEXT DEFAULT '',
    job_description TEXT DEFAULT '',
    notes         TEXT DEFAULT '',
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT NOT NULL,
    text        TEXT NOT NULL,
    skills      TEXT NOT NULL,          -- JSON list
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        get_db().executescript(SCHEMA)
        get_db().commit()


# ---------------------------------------------------------------- applications

def list_applications(status=None, search=None):
    sql = "SELECT * FROM applications"
    clauses, params = [], []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if search:
        clauses.append("(company LIKE ? OR role LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY applied_date DESC, id DESC"
    return get_db().execute(sql, params).fetchall()


def get_application(app_id):
    return get_db().execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()


def create_application(data):
    db = get_db()
    cur = db.execute(
        """INSERT INTO applications
           (company, role, status, applied_date, job_url, job_description, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data["company"],
            data["role"],
            data.get("status", "Applied"),
            data.get("applied_date") or date.today().isoformat(),
            data.get("job_url", ""),
            data.get("job_description", ""),
            data.get("notes", ""),
        ),
    )
    db.commit()
    return cur.lastrowid


def update_application(app_id, data):
    db = get_db()
    db.execute(
        """UPDATE applications SET company = ?, role = ?, status = ?, applied_date = ?,
           job_url = ?, job_description = ?, notes = ? WHERE id = ?""",
        (
            data["company"],
            data["role"],
            data["status"],
            data["applied_date"],
            data.get("job_url", ""),
            data.get("job_description", ""),
            data.get("notes", ""),
            app_id,
        ),
    )
    db.commit()


def set_status(app_id, status):
    db = get_db()
    db.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
    db.commit()


def delete_application(app_id):
    db = get_db()
    db.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    db.commit()


def row_to_dict(row):
    return dict(row) if row is not None else None


# ---------------------------------------------------------------------- resume

def save_resume(filename, text, skills):
    db = get_db()
    db.execute(
        "INSERT INTO resumes (filename, text, skills) VALUES (?, ?, ?)",
        (filename, text, json.dumps(skills)),
    )
    db.commit()


def latest_resume():
    row = get_db().execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return None
    resume = dict(row)
    resume["skills"] = json.loads(resume["skills"])
    return resume


# ----------------------------------------------------------------------- stats

def application_stats():
    rows = get_db().execute(
        "SELECT status, COUNT(*) AS n FROM applications GROUP BY status"
    ).fetchall()
    by_status = {status: 0 for status in STATUSES}
    for row in rows:
        by_status[row["status"]] = row["n"]

    total = sum(by_status.values())
    submitted = total - by_status["Wishlist"]
    responded = by_status["Interview"] + by_status["Offer"] + by_status["Rejected"]
    progressed = by_status["Interview"] + by_status["Offer"]

    def pct(part, whole):
        return round(100 * part / whole) if whole else 0

    monthly = get_db().execute(
        """SELECT substr(applied_date, 1, 7) AS month, COUNT(*) AS n
           FROM applications WHERE status != 'Wishlist'
           GROUP BY month ORDER BY month DESC LIMIT 6"""
    ).fetchall()

    return {
        "total": total,
        "submitted": submitted,
        "by_status": by_status,
        "response_rate": pct(responded, submitted),
        "interview_rate": pct(progressed, submitted),
        "monthly": [{"month": r["month"], "count": r["n"]} for r in reversed(monthly)],
    }

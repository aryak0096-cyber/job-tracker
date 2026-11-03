# Smart Job Application Tracker with Resume Analyzer

A Flask web app that tracks your job applications and tells you how well your resume matches each job description. Upload a PDF resume, paste job descriptions, and see matched skills, missing skills, and concrete suggestions.

## Features

- **Application tracking**: add, edit, delete, search and filter applications; change status from a dropdown (Wishlist, Applied, Interview, Offer, Rejected, Withdrawn).
- **Resume analysis**: upload a text-based PDF; skills are extracted with `pdfplumber` and a categorised skill taxonomy (languages, frameworks, databases, cloud, data/ML, testing, security).
- **Job match**: compare your resume with any job description. See a match percentage, matched / missing / extra skills, and improvement suggestions grouped by category.
- **Dashboard**: totals, response rate, interview rate, status breakdown, applications per month, and the skills most often missing across your saved job descriptions.
- **JSON REST API** for everything above.
- Light and dark mode, works without JavaScript.

## Tech stack

Python 3.10+, Flask, SQLite (standard library `sqlite3`), pdfplumber, HTML/CSS/JavaScript, pytest.

## Getting started

```bash
git clone https://github.com/<your-username>/job-tracker.git
cd job-tracker

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000. The SQLite database is created automatically in `instance/`.

Set a real secret key outside local development:

```bash
export SECRET_KEY="a-long-random-string"      # Windows: set SECRET_KEY=...
```

## Running the tests

```bash
pytest
```

## Project structure

```
job-tracker/
├── run.py                  # entry point
├── requirements.txt
├── tracker/
│   ├── __init__.py         # app factory
│   ├── database.py         # SQLite schema + queries + stats
│   ├── analyzer.py         # PDF text extraction, skill extraction, matching
│   ├── skills.py           # skill taxonomy (edit this to add your own skills)
│   ├── validation.py       # shared input validation
│   ├── views.py            # HTML pages
│   ├── api.py              # JSON API
│   ├── templates/
│   └── static/
└── tests/
```

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/applications?status=&q=` | List applications |
| POST | `/api/applications` | Create (JSON body) |
| GET | `/api/applications/<id>` | Fetch one |
| PUT | `/api/applications/<id>` | Update |
| DELETE | `/api/applications/<id>` | Delete |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/analyze` | `{"job_description": "..."}` compared with your latest resume |

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/applications \
  -H "Content-Type: application/json" \
  -d '{"company": "Acme", "role": "Backend Developer", "status": "Applied"}'
```

## How the matching works

Skills are found by matching a curated list of skills and their aliases (for example `k8s` → Kubernetes) with word-boundary rules, so `java` does not match `javascript` and `C++`, `C#` and `.NET` work. The match percentage is the share of skills found in the job description that also appear on your resume. Add or change skills in `tracker/skills.py`.

## Limitations and ideas for next steps

- Scanned (image-only) PDFs are not supported; add OCR with `pytesseract`.
- Matching is keyword-based. Next step: TF-IDF or embeddings for semantic matching.
- Single-user, no login. Next step: Flask-Login and per-user data.
- Ideas: CSV export, follow-up reminders, Docker support, deployment to Render or Railway.

## License

MIT

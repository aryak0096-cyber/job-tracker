import io

JD = "Looking for Python, Flask, Docker and Kubernetes skills."


def add_app(client, **overrides):
    data = {"company": "Acme", "role": "Backend Dev", "status": "Applied",
            "applied_date": "2026-10-01", "job_description": JD}
    data.update(overrides)
    return client.post("/applications/new", data=data, follow_redirects=False)


# ----------------------------------------------------------------- HTML pages

def test_pages_load_when_empty(client):
    for url in ("/", "/applications", "/applications/new", "/resume", "/analyze"):
        assert client.get(url).status_code == 200


def test_add_view_edit_delete_flow(client):
    response = add_app(client)
    assert response.status_code == 302

    page = client.get("/applications")
    assert b"Acme" in page.data

    detail = client.get("/applications/1")
    assert detail.status_code == 200 and b"Backend Dev" in detail.data

    edit = client.post("/applications/1/edit", data={
        "company": "Acme Corp", "role": "Senior Dev", "status": "Interview",
        "applied_date": "2026-10-02"}, follow_redirects=True)
    assert b"Acme Corp" in edit.data

    assert client.post("/applications/1/delete").status_code == 302
    assert client.get("/applications/1").status_code == 404


def test_form_validation_errors(client):
    response = add_app(client, company="", applied_date="not-a-date")
    assert response.status_code == 400
    assert b"This field is required." in response.data
    assert b"YYYY-MM-DD" in response.data


def test_status_change_and_filter(client):
    add_app(client)
    client.post("/applications/1/status", data={"status": "Offer"})
    assert b"Acme" in client.get("/applications?status=Offer").data
    assert b"Acme" not in client.get("/applications?status=Rejected").data
    assert client.post("/applications/1/status", data={"status": "Bogus"}).status_code == 400


def test_search(client):
    add_app(client, company="Globex", role="Data Analyst")
    assert b"Globex" in client.get("/applications?q=analyst").data
    assert b"Globex" not in client.get("/applications?q=zzz").data


def test_html_is_escaped(client):
    add_app(client, company="<script>alert(1)</script>")
    assert b"<script>alert(1)</script>" not in client.get("/applications").data


# --------------------------------------------------------------------- resume

def upload(client, content, name="resume.pdf"):
    return client.post(
        "/resume",
        data={"resume": (io.BytesIO(content), name)},
        content_type="multipart/form-data",
        follow_redirects=True,
    )


def test_resume_upload_and_match(client, resume_pdf):
    add_app(client)
    response = upload(client, resume_pdf)
    assert b"skills found" in response.data

    detail = client.get("/applications/1")
    assert b"Resume match" in detail.data
    assert b"Kubernetes" in detail.data  # listed as missing

    dashboard = client.get("/")
    # The sample resume mentions Docker, so only Kubernetes is a gap.
    assert b"Skills to work on" in dashboard.data and b"Kubernetes" in dashboard.data


def test_resume_rejects_non_pdf_and_garbage(client):
    assert b"Only PDF files are supported." in upload(client, b"hello", "resume.txt").data
    assert b"Could not read this PDF" in upload(client, b"not a real pdf", "resume.pdf").data


def test_analyze_requires_resume(client):
    response = client.post("/analyze", data={"job_description": JD}, follow_redirects=True)
    assert b"Upload a resume first." in response.data


def test_analyze_page(client, resume_pdf):
    upload(client, resume_pdf)
    response = client.post("/analyze", data={"job_description": JD})
    assert response.status_code == 200
    assert b"Resume match" in response.data


# ------------------------------------------------------------------------ API

def test_api_crud(client):
    created = client.post("/api/applications", json={
        "company": "Initech", "role": "Engineer", "status": "Applied"})
    assert created.status_code == 201
    app_id = created.get_json()["id"]

    assert client.get(f"/api/applications/{app_id}").get_json()["company"] == "Initech"
    assert len(client.get("/api/applications").get_json()) == 1

    updated = client.put(f"/api/applications/{app_id}", json={
        "company": "Initech", "role": "Engineer", "status": "Offer"})
    assert updated.get_json()["status"] == "Offer"

    assert client.delete(f"/api/applications/{app_id}").status_code == 204
    assert client.get(f"/api/applications/{app_id}").status_code == 404


def test_api_validation(client):
    response = client.post("/api/applications", json={"company": "", "role": "x"})
    assert response.status_code == 422
    assert "company" in response.get_json()["fields"]
    assert client.post("/api/applications", data="nope").status_code == 400


def test_api_stats(client):
    for status in ("Applied", "Interview", "Rejected", "Wishlist"):
        client.post("/api/applications", json={"company": "C", "role": "R", "status": status})
    stats = client.get("/api/stats").get_json()
    assert stats["total"] == 4
    assert stats["submitted"] == 3
    assert stats["by_status"]["Interview"] == 1
    assert stats["response_rate"] == 67  # 2 of 3 submitted got a response
    assert stats["interview_rate"] == 33


def test_api_analyze(client, resume_pdf):
    assert client.post("/api/analyze", json={"job_description": JD}).status_code == 409
    upload(client, resume_pdf)
    result = client.post("/api/analyze", json={"job_description": JD}).get_json()
    assert result["matched"] == ["Docker", "Flask", "Python"]
    assert result["missing"] == ["Kubernetes"]
    assert result["match_percent"] == 75
    assert client.post("/api/analyze", json={}).status_code == 422

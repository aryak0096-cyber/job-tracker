import io

import pytest
from reportlab.pdfgen import canvas

from tracker import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite")})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def make_pdf(lines):
    """Build a small text-based PDF in memory and return its bytes."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    for line in lines:
        pdf.drawString(60, y, line)
        y -= 18
    pdf.save()
    return buffer.getvalue()


@pytest.fixture()
def resume_pdf():
    return make_pdf(
        [
            "Jane Doe - Backend Developer",
            "Skills: Python, Flask, SQLite, Git, GitHub, REST APIs, HTML, CSS, JavaScript",
            "Experience: built a Flask REST API with pytest unit tests and Docker.",
        ]
    )

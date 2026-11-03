import io

import pytest

from tracker import analyzer


def test_extract_skills_basic():
    text = "Experienced with Python, Flask and SQLite. Uses Git daily."
    assert analyzer.extract_skills(text) == ["Flask", "Git", "Python", "SQLite"]


def test_java_does_not_match_javascript():
    assert analyzer.extract_skills("I know JavaScript well") == ["JavaScript"]
    assert "Java" in analyzer.extract_skills("Java and JavaScript")


def test_special_character_skills():
    skills = analyzer.extract_skills("Worked in C++, C# and .NET plus Node.js.")
    assert {"C++", "C#", ".NET", "Node.js"} <= set(skills)


def test_case_insensitive_and_punctuation():
    assert "Python" in analyzer.extract_skills("PYTHON.")
    assert "Docker" in analyzer.extract_skills("(docker)")


def test_empty_text():
    assert analyzer.extract_skills("") == []
    assert analyzer.extract_skills(None) == []


def test_compare_match_and_missing():
    result = analyzer.compare(
        ["Python", "Flask", "Git"],
        "We need Python, Flask, Docker and Kubernetes experience.",
    )
    assert result["matched"] == ["Flask", "Python"]
    assert result["missing"] == ["Docker", "Kubernetes"]
    assert result["extra"] == ["Git"]
    assert result["match_percent"] == 50
    assert any("DevOps" in tip for tip in result["suggestions"])


def test_compare_no_known_skills():
    result = analyzer.compare(["Python"], "Must be a team player.")
    assert result["match_percent"] is None
    assert result["matched"] == [] and result["missing"] == []


def test_compare_full_match():
    result = analyzer.compare(["Python", "Flask"], "Python and Flask required")
    assert result["match_percent"] == 100
    assert result["missing"] == []


def test_pdf_extraction(resume_pdf):
    text = analyzer.extract_text_from_pdf(io.BytesIO(resume_pdf))
    assert "Flask" in text
    skills = analyzer.extract_skills(text)
    assert {"Python", "Flask", "SQLite", "Git", "Docker", "pytest"} <= set(skills)


def test_invalid_pdf_raises():
    with pytest.raises(ValueError):
        analyzer.extract_text_from_pdf(io.BytesIO(b"this is not a pdf"))

"""Resume parsing and resume-vs-job-description skill matching."""

import re
from collections import defaultdict

import pdfplumber

from .skills import category_of, flat_skills

# Pre-compile one regex per skill. The look-around groups stop partial matches
# (e.g. "java" inside "javascript") while still allowing c++, c# and .net.
_BOUNDARY_BEFORE = r"(?<![A-Za-z0-9+#])"
_BOUNDARY_AFTER = r"(?![A-Za-z0-9+#])"


def _compile_patterns():
    patterns = {}
    for name, (_category, aliases) in flat_skills().items():
        alternatives = "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True))
        patterns[name] = re.compile(
            f"{_BOUNDARY_BEFORE}(?:{alternatives}){_BOUNDARY_AFTER}", re.IGNORECASE
        )
    return patterns


_PATTERNS = _compile_patterns()


def extract_text_from_pdf(file_obj):
    """Return all text from a PDF file object. Raises ValueError if unreadable."""
    try:
        with pdfplumber.open(file_obj) as pdf:
            pages = [(page.extract_text() or "") for page in pdf.pages]
    except Exception as exc:  # pdfplumber raises several different error types
        raise ValueError(f"Could not read this PDF: {exc}") from exc

    text = "\n".join(pages).strip()
    if not text:
        raise ValueError(
            "No text found in this PDF. It may be a scanned image; "
            "please upload a text-based PDF."
        )
    return text


def extract_skills(text):
    """Return the sorted list of canonical skills mentioned in `text`."""
    if not text:
        return []
    return sorted(name for name, pattern in _PATTERNS.items() if pattern.search(text))


def group_by_category(skills):
    grouped = defaultdict(list)
    for skill in skills:
        grouped[category_of(skill)].append(skill)
    return {cat: sorted(items) for cat, items in sorted(grouped.items())}


def compare(resume_skills, job_description):
    """Compare resume skills against the skills a job description asks for."""
    resume_set = set(resume_skills)
    job_skills = set(extract_skills(job_description))

    matched = sorted(resume_set & job_skills)
    missing = sorted(job_skills - resume_set)
    extra = sorted(resume_set - job_skills)

    if job_skills:
        match_percent = round(100 * len(matched) / len(job_skills))
    else:
        match_percent = None  # nothing recognisable in the job description

    return {
        "job_skills": sorted(job_skills),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_percent": match_percent,
        "suggestions": build_suggestions(matched, missing, match_percent),
    }


def build_suggestions(matched, missing, match_percent):
    if match_percent is None:
        return [
            "No known skills were found in this job description. "
            "Paste the full text of the posting for a better comparison."
        ]

    suggestions = []
    if match_percent >= 80:
        suggestions.append("Strong match. Tailor your summary to this role and apply.")
    elif match_percent >= 50:
        suggestions.append(
            "Decent match. Highlight your matched skills near the top of your resume."
        )
    else:
        suggestions.append(
            "Low match. Consider building a small project with the missing skills "
            "before applying, or target roles closer to your current skills."
        )

    for category, skills in group_by_category(missing).items():
        suggestions.append(
            f"{category}: if you have used {', '.join(skills)}, add it to your resume "
            f"with a concrete example. If not, a small project would close the gap."
        )

    if matched:
        suggestions.append(
            "Mirror the job posting's wording for your matched skills "
            f"({', '.join(matched[:6])}) so applicant-tracking systems pick them up."
        )
    return suggestions

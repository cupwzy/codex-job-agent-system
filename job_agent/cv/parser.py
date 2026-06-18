from __future__ import annotations

import hashlib
import re
from pathlib import Path

from job_agent.models import CVProfile, EducationItem, ExperienceItem


DOMAIN_TERMS = {
    "geoscience",
    "geology",
    "geophysics",
    "seismic",
    "reservoir",
    "petroleum",
    "energy",
    "renewable",
    "carbon",
    "machine learning",
    "data science",
    "python",
    "gis",
}

TOOL_TERMS = {
    "python",
    "sql",
    "pandas",
    "numpy",
    "scikit-learn",
    "sklearn",
    "tensorflow",
    "pytorch",
    "arcgis",
    "qgis",
    "petrel",
    "kingdom",
    "power bi",
    "tableau",
    "excel",
    "matlab",
}


def extract_text_from_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(content)
    if suffix == ".docx":
        return _extract_docx(content)
    return content.decode("utf-8", errors="ignore")


def parse_cv_text(text: str) -> CVProfile:
    cleaned = normalize_whitespace(text)
    source_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]
    profile_id = f"cv_{source_hash}"
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    candidate_name = lines[0][:80] if lines else "Candidate"
    headline = next((line for line in lines[1:8] if 12 <= len(line) <= 120), "")
    skills = sorted(_find_terms(cleaned, DOMAIN_TERMS | TOOL_TERMS))
    tools = sorted(_find_terms(cleaned, TOOL_TERMS))
    education = _extract_education(lines)
    experience = _extract_experience(lines, cleaned)

    return CVProfile(
        profile_id=profile_id,
        candidate_name=candidate_name,
        headline=headline,
        education=education,
        skills=skills,
        tools=tools,
        experience=experience,
        raw_text=cleaned,
        source_hash=source_hash,
    )


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()


def _extract_pdf(content: bytes) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PDF parsing requires pymupdf. Install project dependencies first.") from exc

    doc = fitz.open(stream=content, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def _extract_docx(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("DOCX parsing requires python-docx. Install project dependencies first.") from exc

    from io import BytesIO

    document = Document(BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _find_terms(text: str, terms: set[str]) -> set[str]:
    lowered = text.lower()
    return {term for term in terms if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered)}


def _extract_education(lines: list[str]) -> list[EducationItem]:
    degree_pattern = re.compile(r"\b(phd|doctor|master|msc|m\.sc|bachelor|bsc|b\.sc|mba)\b", re.I)
    education = []
    for line in lines:
        if degree_pattern.search(line):
            education.append(EducationItem(degree=line[:120], evidence=line))
    return education[:5]


def _extract_experience(lines: list[str], full_text: str) -> list[ExperienceItem]:
    bullets = [line.lstrip("-* ") for line in lines if line.startswith(("-", "*", "•"))]
    domains = sorted(_find_terms(full_text, DOMAIN_TERMS))
    tools = sorted(_find_terms(full_text, TOOL_TERMS))
    if not bullets and full_text:
        bullets = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", full_text) if len(sentence.strip()) > 50]
    return [
        ExperienceItem(
            role="Extracted experience",
            bullets=bullets[:8],
            domains=domains,
            tools=tools,
            evidence="\n".join(bullets[:3]),
        )
    ]

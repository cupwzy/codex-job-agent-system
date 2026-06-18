from __future__ import annotations

import hashlib
import re

from job_agent.jobs.collectors import ManualJobInput
from job_agent.models import JobPosting


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
    "analytics",
}

SKILL_TERMS = {
    "python",
    "sql",
    "machine learning",
    "statistics",
    "geoscience",
    "geophysics",
    "reservoir",
    "seismic",
    "gis",
    "data visualization",
    "optimization",
    "forecasting",
    "cloud",
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


def normalize_manual_job(job_input: ManualJobInput) -> JobPosting:
    raw_text = job_input.raw_text.strip()
    digest = hashlib.sha256(f"{job_input.title}|{job_input.company}|{raw_text}".encode("utf-8")).hexdigest()[:16]
    text = raw_text.lower()
    required_skills = sorted(_find_terms(text, SKILL_TERMS))
    tools = sorted(_find_terms(text, TOOL_TERMS))
    domains = sorted(_find_terms(text, DOMAIN_TERMS))

    return JobPosting(
        job_id=f"job_{digest}",
        title=job_input.title.strip(),
        company=job_input.company.strip(),
        location=job_input.location.strip(),
        remote_policy=_remote_policy(text),
        seniority=_seniority(text),
        domains=domains,
        required_skills=required_skills,
        preferred_skills=[],
        tools=tools,
        requirements=_section_like_lines(raw_text, {"requirement", "qualification", "must", "experience"}),
        responsibilities=_section_like_lines(raw_text, {"responsibil", "deliver", "build", "develop", "lead"}),
        visa_sponsorship=_visa_signal(text),
        source="manual",
        url=job_input.url,
        raw_text=raw_text,
    )


def _find_terms(text: str, terms: set[str]) -> set[str]:
    return {term for term in terms if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text)}


def _remote_policy(text: str) -> str:
    if "hybrid" in text:
        return "hybrid"
    if "remote" in text:
        return "remote"
    if "onsite" in text or "on-site" in text:
        return "onsite"
    return "unknown"


def _seniority(text: str) -> str:
    if re.search(r"\b(intern|internship)\b", text):
        return "intern"
    if re.search(r"\b(junior|entry[- ]level|graduate)\b", text):
        return "junior"
    if re.search(r"\b(senior|principal|staff)\b", text):
        return "senior"
    if re.search(r"\b(lead|manager|head of)\b", text):
        return "lead"
    return "mid" if re.search(r"\b[3-7]\+?\s+years\b", text) else "unknown"


def _visa_signal(text: str) -> str:
    if "visa sponsorship" in text and re.search(r"\b(no|not|without)\b.{0,30}visa sponsorship", text):
        return "no"
    if "visa sponsorship" in text or "sponsor" in text:
        return "yes"
    return "unknown"


def _section_like_lines(raw_text: str, hints: set[str]) -> list[str]:
    lines = [line.strip(" -*\t") for line in raw_text.splitlines() if line.strip()]
    selected = [line for line in lines if any(hint in line.lower() for hint in hints)]
    return selected[:10]

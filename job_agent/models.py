from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class ExperienceItem:
    role: str = ""
    organization: str = ""
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    evidence: str = ""


@dataclass
class EducationItem:
    degree: str = ""
    field: str = ""
    institution: str = ""
    start_date: str | None = None
    end_date: str | None = None
    evidence: str = ""


@dataclass
class CVProfile:
    profile_id: str
    candidate_name: str = ""
    headline: str = ""
    locations: list[str] = field(default_factory=list)
    education: list[EducationItem] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    experience: list[ExperienceItem] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    work_authorization: str | None = None
    source_hash: str = ""
    raw_text: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    location: str = ""
    remote_policy: str = "unknown"
    seniority: str = "unknown"
    domains: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    visa_sponsorship: str = "unknown"
    source: str = "manual"
    url: str | None = None
    posted_at: str | None = None
    raw_text: str = ""
    collected_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MatchResult:
    match_id: str
    profile_id: str
    job_id: str
    overall_score: float
    score_breakdown: dict[str, float]
    matched_terms: list[str]
    missing_terms: list[str]
    explanation: str
    recommended_actions: list[str]
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GeneratedArtifact:
    artifact_id: str
    job_id: str
    profile_id: str
    artifact_type: str
    status: str
    content: str
    grounding_notes: list[dict[str, str]]
    unsupported_requirements: list[str]
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

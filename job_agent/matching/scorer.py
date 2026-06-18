from __future__ import annotations

import hashlib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from job_agent.config.scoring import DEFAULT_SCORING_WEIGHTS
from job_agent.models import CVProfile, JobPosting, MatchResult


def score_job(profile: CVProfile, job: JobPosting, weights: dict[str, float] | None = None) -> MatchResult:
    weights = weights or DEFAULT_SCORING_WEIGHTS
    cv_terms = {term.lower() for term in profile.skills + profile.tools}
    job_terms = {term.lower() for term in job.required_skills + job.tools + job.domains}
    matched = sorted(cv_terms & job_terms)
    missing = sorted(job_terms - cv_terms)

    technical_overlap = _ratio(len(matched), len(job_terms))
    semantic = _semantic_similarity(profile.raw_text, job.raw_text)
    domain = _ratio(len(set(profile.skills) & set(job.domains)), len(job.domains))
    seniority = _seniority_fit(job.seniority, profile.raw_text)
    tool_stack = _ratio(len(set(profile.tools) & set(job.tools)), len(job.tools))
    visa = 1.0 if job.visa_sponsorship in {"yes", "unknown"} else 0.35

    breakdown = {
        "technical_keyword_overlap": technical_overlap,
        "semantic_similarity": semantic,
        "domain_relevance": domain,
        "seniority_match": seniority,
        "tool_stack_alignment": tool_stack,
        "visa_sponsorship_relevance": visa,
    }
    overall = round(sum(breakdown[key] * weights[key] for key in weights), 3)
    match_id = "match_" + hashlib.sha256(f"{profile.profile_id}|{job.job_id}".encode("utf-8")).hexdigest()[:16]

    explanation = _explain(overall, matched, missing, job)
    actions = ["tailor CV"]
    if overall >= 0.62:
        actions.append("write cover letter")
    if overall < 0.35:
        actions.append("consider skipping unless strategic")

    return MatchResult(
        match_id=match_id,
        profile_id=profile.profile_id,
        job_id=job.job_id,
        overall_score=overall,
        score_breakdown={key: round(value, 3) for key, value in breakdown.items()},
        matched_terms=matched,
        missing_terms=missing,
        explanation=explanation,
        recommended_actions=actions,
    )


def _semantic_similarity(cv_text: str, job_text: str) -> float:
    if not cv_text.strip() or not job_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    matrix = vectorizer.fit_transform([cv_text, job_text])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.5
    return min(1.0, numerator / denominator)


def _seniority_fit(seniority: str, cv_text: str) -> float:
    lowered = cv_text.lower()
    if seniority in {"unknown", "mid"}:
        return 0.7
    if seniority == "intern":
        return 0.8
    if seniority == "junior":
        return 0.8
    if seniority in {"senior", "lead"} and any(term in lowered for term in ["senior", "lead", "manager", "principal", "10 years", "8 years"]):
        return 0.9
    return 0.55


def _explain(score: float, matched: list[str], missing: list[str], job: JobPosting) -> str:
    matched_text = ", ".join(matched[:6]) or "few explicit terms"
    missing_text = ", ".join(missing[:5]) or "no major extracted gaps"
    return (
        f"Score {score:.2f}: matched {matched_text}; gaps include {missing_text}. "
        f"Domain signals: {', '.join(job.domains) or 'not clearly extracted'}."
    )

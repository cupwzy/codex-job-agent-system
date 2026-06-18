from __future__ import annotations

from dataclasses import dataclass
import os

from job_agent.models import CVProfile, GeneratedArtifact, JobPosting, MatchResult, utc_now_iso


@dataclass
class DraftOptions:
    include_cover_letter: bool = True
    use_openai: bool = False
    model: str = "gpt-4.1-mini"


def generate_grounded_artifacts(
    profile: CVProfile,
    job: JobPosting,
    match: MatchResult,
    options: DraftOptions | None = None,
) -> list[GeneratedArtifact]:
    options = options or DraftOptions()
    if options.use_openai and os.getenv("OPENAI_API_KEY"):
        return _generate_with_openai(profile, job, match, options)
    return _generate_deterministic(profile, job, match, options)


def _generate_deterministic(
    profile: CVProfile,
    job: JobPosting,
    match: MatchResult,
    options: DraftOptions,
) -> list[GeneratedArtifact]:
    unsupported = match.missing_terms
    relevant_bullets = []
    for experience in profile.experience:
        relevant_bullets.extend(experience.bullets)
    relevant_bullets = relevant_bullets[:8]
    skills = sorted(set(profile.skills + profile.tools) & set(job.required_skills + job.tools + job.domains))

    cv_content = "\n".join(
        [
            profile.candidate_name or "Candidate",
            profile.headline or f"Candidate for {job.title}",
            "",
            f"Target role: {job.title} at {job.company}",
            "",
            "Relevant skills",
            ", ".join(skills) if skills else "Review required: no explicit overlap extracted.",
            "",
            "Experience highlights",
            *[f"- {bullet}" for bullet in relevant_bullets],
            "",
            "Grounding note",
            "This draft only reorders and emphasizes information extracted from the uploaded CV.",
        ]
    )
    artifacts = [
        GeneratedArtifact(
            artifact_id=f"artifact_cv_{job.job_id}_{profile.profile_id}",
            job_id=job.job_id,
            profile_id=profile.profile_id,
            artifact_type="tailored_cv",
            status="draft",
            content=cv_content,
            grounding_notes=_grounding(profile),
            unsupported_requirements=unsupported,
            created_at=utc_now_iso(),
        )
    ]

    if options.include_cover_letter:
        cover = "\n".join(
            [
                f"Dear {job.company} hiring team,",
                "",
                f"I am interested in the {job.title} role. My background aligns with the role through: "
                + (", ".join(match.matched_terms[:6]) if match.matched_terms else "the experience highlighted in my CV")
                + ".",
                "",
                "I would welcome the opportunity to discuss how my geoscience, energy, and data-focused experience can support your team.",
                "",
                "Sincerely,",
                profile.candidate_name or "Candidate",
            ]
        )
        artifacts.append(
            GeneratedArtifact(
                artifact_id=f"artifact_cover_{job.job_id}_{profile.profile_id}",
                job_id=job.job_id,
                profile_id=profile.profile_id,
                artifact_type="cover_letter",
                status="draft",
                content=cover,
                grounding_notes=_grounding(profile),
                unsupported_requirements=unsupported,
                created_at=utc_now_iso(),
            )
        )
    return artifacts


def _generate_with_openai(
    profile: CVProfile,
    job: JobPosting,
    match: MatchResult,
    options: DraftOptions,
) -> list[GeneratedArtifact]:
    try:
        from openai import OpenAI
    except ImportError:
        return _generate_deterministic(profile, job, match, options)

    client = OpenAI()
    prompt = f"""
Create a concise tailored CV draft for the target job.
Use only the CV facts below. Do not invent employers, dates, credentials, quantified outcomes, or tools.
Flag unsupported job requirements rather than claiming them.

CV facts:
{profile.to_dict()}

Job:
{job.to_dict()}

Match:
{match.to_dict()}
"""
    response = client.responses.create(model=options.model, input=prompt)
    content = response.output_text
    return [
        GeneratedArtifact(
            artifact_id=f"artifact_openai_cv_{job.job_id}_{profile.profile_id}",
            job_id=job.job_id,
            profile_id=profile.profile_id,
            artifact_type="tailored_cv",
            status="draft",
            content=content,
            grounding_notes=_grounding(profile),
            unsupported_requirements=match.missing_terms,
            created_at=utc_now_iso(),
        )
    ]


def _grounding(profile: CVProfile) -> list[dict[str, str]]:
    notes = []
    if profile.skills:
        notes.append({"claim": "skills", "source_evidence": ", ".join(profile.skills[:12])})
    for experience in profile.experience[:3]:
        if experience.evidence:
            notes.append({"claim": experience.role or "experience", "source_evidence": experience.evidence[:500]})
    return notes

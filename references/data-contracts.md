# Data Contracts

Use these shapes as implementation targets. Add fields when the project needs them, but keep the core names stable across modules.

## CV Profile

```json
{
  "profile_id": "cv_2026_001",
  "candidate_name": "string",
  "headline": "string",
  "locations": ["string"],
  "education": [
    {
      "degree": "string",
      "field": "string",
      "institution": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "evidence": "source snippet"
    }
  ],
  "skills": ["Python", "geophysics", "machine learning"],
  "tools": ["Petrel", "ArcGIS", "pandas"],
  "experience": [
    {
      "role": "string",
      "organization": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or present",
      "bullets": ["source-grounded achievement"],
      "domains": ["energy", "geoscience"],
      "tools": ["string"],
      "evidence": "source snippet"
    }
  ],
  "certifications": ["string"],
  "languages": ["string"],
  "work_authorization": "string or null",
  "source_hash": "string"
}
```

## Job Posting

```json
{
  "job_id": "job_2026_001",
  "title": "string",
  "company": "string",
  "location": "string",
  "remote_policy": "onsite | hybrid | remote | unknown",
  "seniority": "intern | junior | mid | senior | lead | unknown",
  "domains": ["geoscience", "energy", "machine learning"],
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "tools": ["string"],
  "requirements": ["string"],
  "responsibilities": ["string"],
  "visa_sponsorship": "yes | no | unknown",
  "source": "manual | public_source_name",
  "url": "string or null",
  "posted_at": "ISO date or null",
  "raw_text": "string",
  "collected_at": "ISO datetime"
}
```

## Match Result

```json
{
  "match_id": "match_2026_001",
  "profile_id": "cv_2026_001",
  "job_id": "job_2026_001",
  "overall_score": 0.0,
  "score_breakdown": {
    "technical_keyword_overlap": 0.0,
    "semantic_similarity": 0.0,
    "domain_relevance": 0.0,
    "seniority_match": 0.0,
    "tool_stack_alignment": 0.0,
    "visa_sponsorship_relevance": 0.0
  },
  "matched_terms": ["string"],
  "missing_terms": ["string"],
  "explanation": "short user-facing rationale",
  "recommended_actions": ["tailor CV", "write cover letter", "skip"]
}
```

## Generated Artifact

```json
{
  "artifact_id": "artifact_2026_001",
  "job_id": "job_2026_001",
  "profile_id": "cv_2026_001",
  "artifact_type": "tailored_cv | cover_letter",
  "status": "draft | approved | exported",
  "content": "string",
  "grounding_notes": [
    {
      "claim": "string",
      "source_evidence": "CV snippet or structured field"
    }
  ],
  "unsupported_requirements": ["string"],
  "created_at": "ISO datetime"
}
```

## Suggested SQLite Tables

- `cv_profiles`
- `job_postings`
- `pipeline_runs`
- `match_results`
- `generated_artifacts`
- `run_logs`

Store JSON payloads in text columns when the project is small. Use normalized tables for skills, tools, requirements, and match terms when filtering and reporting become important.

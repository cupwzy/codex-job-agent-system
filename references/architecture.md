# Architecture Blueprint

## Purpose

Build an end-to-end job hunting system for geoscience, energy, and data science roles with Codex as the orchestration layer and Streamlit as the human control surface.

## Core Components

### Codex Agent Layer

- Orchestrate workflow steps and tool calls.
- Manage pipeline run state and logs.
- Enforce output consistency across parsers, scrapers, scoring, and generation.
- Detect missing prerequisites such as CV profile, job records, API keys, or model availability.

### Job Collection Module

- Accept manual job text, URL metadata, and keyword/source searches.
- Scrape only allowed sources and public pages that comply with platform terms.
- Normalize raw postings into structured job objects.
- Preserve raw source text for auditability.

### CV Processing Module

- Parse PDF, DOCX, and text CV inputs.
- Extract education, skills, tools, experience, projects, publications, certifications, locations, work authorization, and domain keywords.
- Store a structured profile plus source snippets so generated outputs can be traced back to the CV.

### Matching and Scoring Engine

- Combine lexical overlap, semantic similarity, domain relevance, seniority fit, tool-stack alignment, and optional visa/sponsorship relevance.
- Return a numeric score plus a concise explanation.
- Keep scoring weights configurable and visible in outputs.

### CV Generation Engine

- Generate job-specific CV drafts and optional cover letters.
- Reorder and emphasize existing experience to match the job.
- Add keywords naturally only when supported by CV facts.
- Flag unsupported requirements as gaps instead of inventing claims.

### Streamlit Dashboard

- Provide upload, search, ranking, preview, approval, and export controls.
- Show status for each pipeline step and allow reruns.
- Keep user review visible before exporting tailored materials.

## Recommended Execution Flow

1. Load CV into the system.
2. Parse CV into a structured profile.
3. Input keywords, sources, or manual job records.
4. Collect job postings.
5. Normalize job data.
6. Run matching and scoring.
7. Rank jobs.
8. Select top N jobs.
9. Generate tailored CVs and optional cover letters.
10. Review in Streamlit.
11. Export or store approved outputs.

## Persistence

Use SQLite for local-first durability. Persist:

- CV profiles and source document hashes.
- Raw and normalized job records.
- Pipeline runs and logs.
- Match scores and explanations.
- Generated artifacts and approval status.

## Safety Invariants

- Do not submit job applications automatically.
- Do not send emails, LinkedIn messages, or other external communications without explicit confirmation.
- Do not scrape protected platforms or bypass access controls.
- Do not invent CV facts, dates, employers, credentials, projects, or quantified outcomes.
- Always distinguish generated drafts from approved final exports.

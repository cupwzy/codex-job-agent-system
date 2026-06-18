---
name: codex-job-agent-system
description: Build, extend, or operate a Codex Agent plus Streamlit job hunting automation system for geoscience, energy, and data science roles. Use when the user asks for a modular job-search pipeline, CV parsing, job scraping or normalization, CV-job matching and scoring, ranked recommendations, job-specific CV or cover-letter generation, Streamlit dashboards for application workflows, SQLite persistence, or safety constraints around grounded CV rewriting and no automatic job submissions.
---

# Codex Job Agent System

## Overview

Use this skill to design or implement a personal AI career agent that collects jobs, parses a CV, ranks opportunities, and generates grounded application materials through a Streamlit interface.

The system must preserve user control: never submit applications, send external messages, or invent CV facts without explicit user confirmation and source grounding.

## Workflow

1. Inspect the existing repository before creating files. Reuse project conventions, dependency managers, configuration, and folder names where present.
2. Separate the system into independently executable modules: CV processing, job collection, normalization, matching, generation, persistence, orchestration, and Streamlit UI.
3. Keep pipeline steps stateless where practical. Persist durable records in SQLite: CV profiles, job postings, match scores, generated artifacts, and run logs.
4. Add human-in-the-loop review before export, external communication, or any generated CV/cover-letter output being treated as final.
5. Verify the smallest meaningful path end to end: ingest sample CV text, ingest or mock job records, normalize, score, rank, generate grounded output, and display in Streamlit.

## Architecture

Read [references/architecture.md](references/architecture.md) when designing a new project, adding major modules, or explaining system structure.

Default package layout for a Python implementation:

```text
job_agent/
  agent/            # orchestration and pipeline state
  cv/               # parsing, extraction, profile schema
  jobs/             # collection, scraping adapters, normalization
  matching/         # similarity, weighted scoring, explanations
  generation/       # grounded CV and cover-letter drafting
  storage/          # SQLite models and migrations
  ui/               # Streamlit dashboard
  config/           # sources, weights, OpenAI/model settings
tests/
```

## Data Contracts

Read [references/data-contracts.md](references/data-contracts.md) before implementing parsers, database schemas, API boundaries, matching output, or export formats.

Use structured objects for all internal boundaries. Avoid passing raw scraped HTML, model prose, or loosely shaped dictionaries between modules once parsing is complete.

## Implementation Rules

- Prefer Python, pandas, SQLite, Streamlit, sklearn or sentence-transformers, PyMuPDF/pdfplumber, and the OpenAI API as requested unless the repository already chose compatible alternatives.
- Use source adapters that respect robots.txt, rate limits, platform terms, and authenticated access boundaries. Do not automate protected platforms without permission.
- Store raw job text separately from normalized job records so scoring can be audited.
- Make scoring explainable: return matched keywords, missing requirements, seniority fit, domain fit, tool-stack fit, and optional visa/sponsorship signals.
- Ground generated CVs in extracted CV facts. If a target job asks for a skill absent from the CV profile, mention it as a gap or transferable adjacency rather than adding it as experience.
- Keep OpenAI prompts deterministic and auditable: include source CV facts, job requirements, forbidden claims, and requested output format.
- Treat generated CVs and cover letters as drafts until the user approves them.

## Streamlit UI

Build the first screen as the working dashboard, not a marketing page. Include:

- CV upload and parsed-profile preview.
- Job search input, source selection, and manual job entry.
- Ranked job table with filters, scores, source URLs, and status.
- Match explanation panel for a selected job.
- Tailored CV and cover-letter preview with approval controls.
- Export actions for CSV, DOCX/PDF where supported, and stored run artifacts.

## Verification

For code changes, run targeted tests or a smoke test that exercises:

- CV parse to structured profile.
- Job ingestion to normalized job object.
- Matching and ranked score output.
- Grounded generation refusing or flagging unsupported claims.
- Streamlit import/startup path when UI code changes.

If live scraping or OpenAI credentials are unavailable, use fixtures and clearly report what was mocked.

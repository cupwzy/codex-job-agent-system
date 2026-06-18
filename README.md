# Codex Intelligent Job Agent System

A local-first Python and Streamlit application for geoscience, energy, and data science job hunting workflows.

The MVP supports CV ingestion, manual job entry, job normalization, explainable CV-job matching, grounded tailored CV drafts, SQLite persistence, and CSV export. It does not submit applications or send external messages.

## Features

- Parse CV text, PDF, DOCX, or TXT uploads into a structured profile.
- Add manual job postings with title, company, URL, location, and raw description.
- Normalize jobs into required skills, tools, domains, seniority, remote policy, and sponsorship signals.
- Score and rank jobs with an explainable weighted model.
- Generate grounded tailored CV drafts and optional cover letters.
- Persist CV profiles, jobs, match results, generated artifacts, and run logs in SQLite.
- Run a Streamlit dashboard for upload, scoring, review, approval, and export.

## Quick Start

```powershell
cd D:\codex-workspace\codex-job-agent-system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
streamlit run app.py
```

If you do not need PDF or DOCX parsing, paste CV text directly into the dashboard.

## Optional OpenAI Generation

The app works without OpenAI by using a deterministic grounded draft generator. To enable OpenAI-assisted rewriting, set:

```powershell
$env:OPENAI_API_KEY="your_api_key"
```

Generated outputs remain drafts and must be reviewed before export.

## Tests

```powershell
pytest
```

## Project Layout

```text
app.py
job_agent/
  agent/            # Orchestration
  cv/               # CV parsing and profile extraction
  jobs/             # Manual collection and normalization
  matching/         # Weighted scoring
  generation/       # Grounded CV and cover-letter drafting
  storage/          # SQLite persistence
  config/           # Scoring defaults
tests/
```

## Safety Constraints

- No automatic job application submission.
- No external communication without explicit confirmation.
- No protected-platform scraping or access-control bypass.
- No invented CV facts, dates, credentials, employers, projects, or quantified outcomes.
- All generated CV outputs are drafts until approved by the user.

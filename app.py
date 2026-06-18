from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from job_agent.agent.orchestrator import JobAgent
from job_agent.generation.drafter import DraftOptions
from job_agent.jobs.collectors import ManualJobInput
from job_agent.storage.sqlite_store import SQLiteStore


DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "job_agent.db"


def get_agent() -> JobAgent:
    DATA_DIR.mkdir(exist_ok=True)
    store = SQLiteStore(DB_PATH)
    store.initialize()
    return JobAgent(store=store)


st.set_page_config(page_title="Codex Job Agent", layout="wide")
st.title("Codex Intelligent Job Agent System")

agent = get_agent()

with st.sidebar:
    st.header("CV")
    uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])
    pasted_cv = st.text_area("Or paste CV text", height=220)
    parse_cv = st.button("Parse CV", type="primary")

    st.header("Job")
    title = st.text_input("Job title")
    company = st.text_input("Company")
    location = st.text_input("Location")
    url = st.text_input("URL")
    job_text = st.text_area("Job description", height=260)
    save_job = st.button("Save job")

if parse_cv:
    with st.spinner("Parsing CV..."):
        if uploaded_cv:
            profile = agent.ingest_cv_upload(uploaded_cv.name, uploaded_cv.getvalue())
        elif pasted_cv.strip():
            profile = agent.ingest_cv_text(pasted_cv)
        else:
            st.warning("Upload a CV or paste CV text first.")
            profile = None
    if profile:
        st.session_state["profile_id"] = profile.profile_id
        st.success(f"Parsed profile {profile.profile_id}")

if save_job:
    if not job_text.strip():
        st.warning("Paste a job description before saving.")
    else:
        job = agent.add_manual_job(
            ManualJobInput(
                title=title or "Untitled role",
                company=company or "Unknown company",
                location=location or "Unknown location",
                url=url or None,
                raw_text=job_text,
            )
        )
        st.session_state["selected_job_id"] = job.job_id
        st.success(f"Saved job {job.job_id}")

profiles = agent.list_profiles()
jobs = agent.list_jobs()

profile_col, job_col = st.columns([1, 2])

with profile_col:
    st.subheader("Profile")
    if profiles:
        profile_options = {f"{p.candidate_name or 'Candidate'} ({p.profile_id})": p.profile_id for p in profiles}
        selected_profile_id = st.selectbox("Active CV profile", options=list(profile_options.values()), format_func=lambda value: next(k for k, v in profile_options.items() if v == value))
        st.session_state["profile_id"] = selected_profile_id
        profile = agent.get_profile(selected_profile_id)
        st.json(profile.to_dict(), expanded=False)
    else:
        st.info("Parse a CV to begin.")

with job_col:
    st.subheader("Jobs")
    if jobs:
        job_rows = [
            {
                "job_id": job.job_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "domains": ", ".join(job.domains),
                "skills": ", ".join(job.required_skills[:8]),
                "url": job.url or "",
            }
            for job in jobs
        ]
        st.dataframe(pd.DataFrame(job_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Add a job posting to score it against your CV.")

st.divider()

score_col, draft_col = st.columns([1, 1])

with score_col:
    st.subheader("Ranked Matches")
    can_score = bool(profiles and jobs)
    if st.button("Run matching", disabled=not can_score):
        matches = agent.score_all(st.session_state["profile_id"])
        st.session_state["matches"] = [m.to_dict() for m in matches]

    match_rows = st.session_state.get("matches", [])
    if match_rows:
        df = pd.DataFrame(match_rows).sort_values("overall_score", ascending=False)
        st.dataframe(
            df[["job_id", "overall_score", "matched_terms", "missing_terms", "explanation"]],
            use_container_width=True,
            hide_index=True,
        )
        selected_job_id = st.selectbox("Select job for draft", options=df["job_id"].tolist())
        st.session_state["selected_job_id"] = selected_job_id
        selected_match = next((row for row in match_rows if row["job_id"] == selected_job_id), None)
        if selected_match:
            st.json(selected_match, expanded=False)
    else:
        st.caption("Run matching to rank saved jobs.")

with draft_col:
    st.subheader("Grounded Drafts")
    include_cover = st.checkbox("Include cover letter", value=True)
    if st.button("Generate draft", disabled=not (profiles and jobs and st.session_state.get("selected_job_id"))):
        artifacts = agent.generate_artifacts(
            profile_id=st.session_state["profile_id"],
            job_id=st.session_state["selected_job_id"],
            options=DraftOptions(include_cover_letter=include_cover),
        )
        st.session_state["artifacts"] = [artifact.to_dict() for artifact in artifacts]

    artifacts = st.session_state.get("artifacts", [])
    for artifact in artifacts:
        st.markdown(f"#### {artifact['artifact_type'].replace('_', ' ').title()} ({artifact['status']})")
        st.text_area(
            artifact["artifact_id"],
            artifact["content"],
            height=300 if artifact["artifact_type"] == "tailored_cv" else 220,
        )
        if artifact["unsupported_requirements"]:
            st.warning("Unsupported requirements: " + ", ".join(artifact["unsupported_requirements"]))

st.divider()

export_col, audit_col = st.columns([1, 1])
with export_col:
    st.subheader("Export")
    if st.button("Export ranked matches CSV", disabled=not st.session_state.get("matches")):
        export_path = agent.export_matches_csv(st.session_state["profile_id"], Path("exports"))
        st.success(f"Exported {export_path}")

with audit_col:
    st.subheader("Audit Log")
    st.dataframe(pd.DataFrame(agent.recent_logs()), use_container_width=True, hide_index=True)

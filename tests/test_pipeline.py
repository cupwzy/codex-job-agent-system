from __future__ import annotations

from pathlib import Path

from job_agent.agent.orchestrator import JobAgent
from job_agent.generation.drafter import DraftOptions
from job_agent.jobs.collectors import ManualJobInput
from job_agent.storage.sqlite_store import SQLiteStore


def test_end_to_end_pipeline(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "agent.db")
    store.initialize()
    agent = JobAgent(store)

    profile = agent.ingest_cv_text(
        """
        Alex Example
        Geoscience data scientist
        MSc Geophysics, Example University
        - Built Python and pandas workflows for seismic interpretation and reservoir analytics.
        - Used machine learning, SQL, ArcGIS, and scikit-learn for energy datasets.
        """
    )
    job = agent.add_manual_job(
        ManualJobInput(
            title="Energy Data Scientist",
            company="Example Energy",
            location="Houston",
            raw_text="""
            We need a data scientist with Python, SQL, machine learning, pandas,
            geoscience, reservoir, and seismic experience. Hybrid role.
            """,
        )
    )

    matches = agent.score_all(profile.profile_id)
    assert matches
    assert matches[0].job_id == job.job_id
    assert matches[0].overall_score > 0.45
    assert "python" in matches[0].matched_terms

    artifacts = agent.generate_artifacts(
        profile.profile_id,
        job.job_id,
        DraftOptions(include_cover_letter=True),
    )
    assert len(artifacts) == 2
    assert artifacts[0].status == "draft"
    assert "Grounding note" in artifacts[0].content


def test_storage_round_trip(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "agent.db")
    store.initialize()
    agent = JobAgent(store)

    profile = agent.ingest_cv_text("Candidate\nPython geoscience energy analytics")
    job = agent.add_manual_job(ManualJobInput(title="Analyst", company="Energy Co", raw_text="Python energy analytics"))

    assert agent.get_profile(profile.profile_id).profile_id == profile.profile_id
    assert agent.list_jobs()[0].job_id == job.job_id

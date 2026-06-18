from __future__ import annotations

from pathlib import Path

import pandas as pd

from job_agent.cv.parser import extract_text_from_upload, parse_cv_text
from job_agent.generation.drafter import DraftOptions, generate_grounded_artifacts
from job_agent.jobs.collectors import ManualJobInput
from job_agent.jobs.normalizer import normalize_manual_job
from job_agent.matching.scorer import score_job
from job_agent.models import CVProfile, GeneratedArtifact, JobPosting, MatchResult
from job_agent.storage.sqlite_store import SQLiteStore


class JobAgent:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def ingest_cv_upload(self, filename: str, content: bytes) -> CVProfile:
        text = extract_text_from_upload(filename, content)
        return self.ingest_cv_text(text)

    def ingest_cv_text(self, text: str) -> CVProfile:
        profile = parse_cv_text(text)
        self.store.save_profile(profile)
        return profile

    def add_manual_job(self, job_input: ManualJobInput) -> JobPosting:
        job = normalize_manual_job(job_input)
        self.store.save_job(job)
        return job

    def score_all(self, profile_id: str) -> list[MatchResult]:
        profile = self.store.get_profile(profile_id)
        matches = [score_job(profile, job) for job in self.store.list_jobs()]
        matches.sort(key=lambda match: match.overall_score, reverse=True)
        for match in matches:
            self.store.save_match(match)
        self.store.log("score_all", f"{profile_id}: {len(matches)} jobs")
        return matches

    def generate_artifacts(self, profile_id: str, job_id: str, options: DraftOptions | None = None) -> list[GeneratedArtifact]:
        profile = self.store.get_profile(profile_id)
        job = self.store.get_job(job_id)
        match = score_job(profile, job)
        artifacts = generate_grounded_artifacts(profile, job, match, options)
        for artifact in artifacts:
            self.store.save_artifact(artifact)
        return artifacts

    def list_profiles(self) -> list[CVProfile]:
        return self.store.list_profiles()

    def get_profile(self, profile_id: str) -> CVProfile:
        return self.store.get_profile(profile_id)

    def list_jobs(self) -> list[JobPosting]:
        return self.store.list_jobs()

    def recent_logs(self) -> list[dict[str, str]]:
        return self.store.recent_logs()

    def export_matches_csv(self, profile_id: str, export_dir: Path) -> Path:
        export_dir.mkdir(exist_ok=True)
        rows = [match.to_dict() for match in self.store.list_matches(profile_id)]
        path = export_dir / f"matches_{profile_id}.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        self.store.log("export_matches_csv", str(path))
        return path

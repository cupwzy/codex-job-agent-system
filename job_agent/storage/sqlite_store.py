from __future__ import annotations

import json
import sqlite3
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from job_agent.models import CVProfile, EducationItem, ExperienceItem, GeneratedArtifact, JobPosting, MatchResult, utc_now_iso

T = TypeVar("T")


class SQLiteStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists cv_profiles (
                  profile_id text primary key,
                  payload text not null,
                  created_at text not null
                );
                create table if not exists job_postings (
                  job_id text primary key,
                  payload text not null,
                  collected_at text not null
                );
                create table if not exists match_results (
                  match_id text primary key,
                  profile_id text not null,
                  job_id text not null,
                  payload text not null,
                  created_at text not null
                );
                create table if not exists generated_artifacts (
                  artifact_id text primary key,
                  profile_id text not null,
                  job_id text not null,
                  payload text not null,
                  created_at text not null
                );
                create table if not exists run_logs (
                  log_id integer primary key autoincrement,
                  event text not null,
                  detail text not null,
                  created_at text not null
                );
                """
            )

    def save_profile(self, profile: CVProfile) -> None:
        self._upsert("cv_profiles", "profile_id", profile.profile_id, profile.to_dict(), profile.created_at)
        self.log("save_profile", profile.profile_id)

    def get_profile(self, profile_id: str) -> CVProfile:
        payload = self._get_payload("cv_profiles", "profile_id", profile_id)
        return _profile_from_dict(payload)

    def list_profiles(self) -> list[CVProfile]:
        return [_profile_from_dict(payload) for payload in self._list_payloads("cv_profiles", "created_at desc")]

    def save_job(self, job: JobPosting) -> None:
        self._upsert("job_postings", "job_id", job.job_id, job.to_dict(), job.collected_at)
        self.log("save_job", job.job_id)

    def get_job(self, job_id: str) -> JobPosting:
        return _job_from_dict(self._get_payload("job_postings", "job_id", job_id))

    def list_jobs(self) -> list[JobPosting]:
        return [_job_from_dict(payload) for payload in self._list_payloads("job_postings", "collected_at desc")]

    def save_match(self, match: MatchResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert or replace into match_results
                  (match_id, profile_id, job_id, payload, created_at)
                values (?, ?, ?, ?, ?)
                """,
                (
                    match.match_id,
                    match.profile_id,
                    match.job_id,
                    json.dumps(match.to_dict()),
                    match.created_at,
                ),
            )

    def list_matches(self, profile_id: str) -> list[MatchResult]:
        with self._connect() as conn:
            rows = conn.execute(
                "select payload from match_results where profile_id = ? order by created_at desc",
                (profile_id,),
            ).fetchall()
        return [_match_from_dict(json.loads(row["payload"])) for row in rows]

    def save_artifact(self, artifact: GeneratedArtifact) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert or replace into generated_artifacts
                  (artifact_id, profile_id, job_id, payload, created_at)
                values (?, ?, ?, ?, ?)
                """,
                (
                    artifact.artifact_id,
                    artifact.profile_id,
                    artifact.job_id,
                    json.dumps(artifact.to_dict()),
                    artifact.created_at,
                ),
            )
        self.log("save_artifact", artifact.artifact_id)

    def log(self, event: str, detail: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into run_logs (event, detail, created_at) values (?, ?, ?)",
                (event, detail, utc_now_iso()),
            )

    def recent_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select event, detail, created_at from run_logs order by log_id desc limit ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _upsert(self, table: str, key_column: str, key: str, payload: dict[str, Any], timestamp: str) -> None:
        with self._connect() as conn:
            time_column = "created_at" if table != "job_postings" else "collected_at"
            conn.execute(
                f"insert or replace into {table} ({key_column}, payload, {time_column}) values (?, ?, ?)",
                (key, json.dumps(payload), timestamp),
            )

    def _get_payload(self, table: str, key_column: str, key: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(f"select payload from {table} where {key_column} = ?", (key,)).fetchone()
        if row is None:
            raise KeyError(f"{table} record not found: {key}")
        return json.loads(row["payload"])

    def _list_payloads(self, table: str, order_by: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(f"select payload from {table} order by {order_by}").fetchall()
        return [json.loads(row["payload"]) for row in rows]


def _filter_dataclass_payload(cls: type[T], payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {field.name for field in fields(cls)}
    return {key: value for key, value in payload.items() if key in allowed}


def _profile_from_dict(payload: dict[str, Any]) -> CVProfile:
    payload = dict(payload)
    payload["education"] = [EducationItem(**_filter_dataclass_payload(EducationItem, item)) for item in payload.get("education", [])]
    payload["experience"] = [ExperienceItem(**_filter_dataclass_payload(ExperienceItem, item)) for item in payload.get("experience", [])]
    return CVProfile(**_filter_dataclass_payload(CVProfile, payload))


def _job_from_dict(payload: dict[str, Any]) -> JobPosting:
    return JobPosting(**_filter_dataclass_payload(JobPosting, payload))


def _match_from_dict(payload: dict[str, Any]) -> MatchResult:
    return MatchResult(**_filter_dataclass_payload(MatchResult, payload))

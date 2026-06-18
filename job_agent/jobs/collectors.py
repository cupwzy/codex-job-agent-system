from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ManualJobInput:
    title: str
    company: str
    raw_text: str
    location: str = ""
    url: str | None = None

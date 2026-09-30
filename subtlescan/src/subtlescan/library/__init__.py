"""Curated, client-facing text per check (business impact, remediation, Terraform, effort)."""

from __future__ import annotations

from functools import cache
from importlib import resources

import yaml
from pydantic import BaseModel

from subtlescan.models import Effort


class LibraryEntry(BaseModel):
    title: str
    business_impact: str
    remediation: str
    terraform_fix: str | None = None
    effort: Effort


@cache
def load_library() -> dict[str, LibraryEntry]:
    entries: dict[str, LibraryEntry] = {}
    for f in sorted(resources.files(__package__).iterdir(), key=lambda p: p.name):
        if not f.name.endswith(".yaml"):
            continue
        for check_id, raw in (yaml.safe_load(f.read_text()) or {}).items():
            if check_id in entries:
                raise ValueError(f"library: duplicate entry {check_id} in {f.name}")
            entries[check_id] = LibraryEntry.model_validate(raw)
    return entries

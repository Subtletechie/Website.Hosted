from __future__ import annotations

from pydantic import BaseModel

from subtlescan.models.enums import GapReason, Provider


class CoverageGap(BaseModel):
    """Something we could not assess, and why. Shown to the client, never swallowed."""

    provider: Provider
    scope: str
    service: str
    reason: GapReason
    detail: str

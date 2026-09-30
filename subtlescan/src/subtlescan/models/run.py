from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from subtlescan.models.enums import Provider


class Run(BaseModel):
    client: str
    provider: Provider
    started_at: datetime
    finished_at: datetime | None = None
    tool_version: str
    tenant_id: str | None = None
    scopes: list[str] = Field(default_factory=list)  # subscriptions / accounts scanned
    services_scanned: list[str] = Field(default_factory=list)
    asset_count: int = 0
    finding_count: int = 0

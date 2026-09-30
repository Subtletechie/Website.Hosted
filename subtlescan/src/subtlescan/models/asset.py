from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from subtlescan.models.enums import Provider


class Asset(BaseModel):
    """A normalized cloud resource. Provider-specific settings live in `properties`."""

    id: str
    provider: Provider
    type: str  # normalized type, e.g. "azure.storage_account"
    name: str
    scope: str  # subscription id / AWS account id / tenant id
    location: str | None = None
    resource_group: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)
    properties: dict[str, Any] = Field(default_factory=dict)

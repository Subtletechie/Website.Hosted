from __future__ import annotations

from typing import Any

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra.constants import PREMIUM_ERROR_MARKERS
from subtlescan.collectors.entra.graph import GraphClient


def graph(ctx: AzureContext) -> GraphClient:
    client: GraphClient = ctx.client(GraphClient)
    return client


def tenant_id(ctx: AzureContext) -> str:
    if ctx.tenant_id is None:
        org = next(iter(graph(ctx).list("organization", {"$select": "id"})), None)
        if org is None:
            raise RuntimeError("could not determine tenant id from /organization")
        ctx.tenant_id = org["id"]
    return ctx.tenant_id


def is_premium_error(exc: BaseException) -> bool:
    text = f"{getattr(exc, 'graph_code', '')} {exc}"
    return any(m in text for m in PREMIUM_ERROR_MARKERS)


def compact(d: dict[str, Any] | None, *keys: str) -> list[Any]:
    """Safe nested lookup that returns [] for missing/null collections."""
    cur: Any = d or {}
    for k in keys:
        cur = (cur or {}).get(k)
    return list(cur or [])

"""Directory role assignments (active), marked time-bound where PIM shows an end date."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra.common import graph, is_premium_error, tenant_id
from subtlescan.collectors.entra.constants import GLOBAL_ADMIN_TEMPLATE, PRIVILEGED_ROLE_TEMPLATES
from subtlescan.models import Asset, GapReason, Provider

ASSET_TYPE = "entra.directory_role"


def _principal(p: dict[str, Any]) -> tuple[str, str]:
    kind = (p.get("@odata.type") or "#microsoft.graph.unknown").rsplit(".", 1)[-1]
    name = p.get("userPrincipalName") or p.get("displayName") or p.get("id", "?")
    return kind, name


def collect(ctx: AzureContext) -> list[Asset]:
    g = graph(ctx)
    tid = tenant_id(ctx)
    defs = {
        d["id"]: d
        for d in g.list(
            "roleManagement/directory/roleDefinitions", {"$select": "id,displayName,templateId,isPrivileged"}
        )
    }
    time_bound = _time_bound(ctx, tid)
    by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in g.list("roleManagement/directory/roleAssignments", {"$expand": "principal"}):
        kind, name = _principal(a.get("principal") or {"id": a.get("principalId")})
        by_role[a["roleDefinitionId"]].append(
            {
                "principal_id": a.get("principalId"),
                "principal_type": kind,
                "principal_name": name,
                "directory_scope": a.get("directoryScopeId", "/"),
                "time_bound": (a.get("principalId"), a["roleDefinitionId"]) in time_bound,
            }
        )
    assets = []
    for role_id, members in by_role.items():
        d = defs.get(role_id, {})
        template = d.get("templateId") or role_id
        assets.append(
            Asset(
                id=f"tenants/{tid}/directoryRoles/{template}",
                provider=Provider.ENTRA,
                type=ASSET_TYPE,
                name=d.get("displayName") or template,
                scope=tid,
                properties={
                    "template_id": template,
                    "privileged": bool(d.get("isPrivileged")) or template in PRIVILEGED_ROLE_TEMPLATES,
                    "admin_scope": template == GLOBAL_ADMIN_TEMPLATE,
                    "assignments": members,
                },
            )
        )
    return assets


def _time_bound(ctx: AzureContext, tid: str) -> set[tuple[str, str]]:
    """(principal, role) pairs whose active assignment expires (PIM). Needs Entra ID P2; optional."""
    try:
        rows = graph(ctx).list("roleManagement/directory/roleAssignmentScheduleInstances")
        return {(r["principalId"], r["roleDefinitionId"]) for r in rows if r.get("endDateTime")}
    except Exception as exc:  # noqa: BLE001
        if is_premium_error(exc):
            ctx.gap(
                tid,
                "entra.pim",
                GapReason.UNSUPPORTED,
                "No Entra ID P2 (PIM); every active role assignment is treated as permanent.",
            )
        else:
            reason, detail = ctx.classify(exc)
            ctx.gap(tid, "entra.pim", reason, detail)
        return set()

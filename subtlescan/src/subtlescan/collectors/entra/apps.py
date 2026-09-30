"""App registrations (credential lifetimes) and service principals (Graph application permissions).

Graph never returns secret values, only a 3-character `hint`; that hint is all we keep.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra.common import graph, tenant_id
from subtlescan.collectors.entra.constants import GRAPH_APP_ID, HIGH_PRIVILEGE_GRAPH_PERMISSIONS, MICROSOFT_TENANTS
from subtlescan.models import Asset, Provider

APP_TYPE = "entra.application"
SP_TYPE = "entra.service_principal"


def collect(ctx: AzureContext) -> list[Asset]:
    tid = tenant_id(ctx)
    assets: list[Asset] = []
    with ctx.guard(tid, "entra.applications"):
        assets += _applications(ctx, tid)
    with ctx.guard(tid, "entra.service_principals"):
        assets += _service_principals(ctx, tid)
    return assets


def _applications(ctx: AzureContext, tid: str) -> list[Asset]:
    out = []
    for app in graph(ctx).list("applications", {"$select": "id,appId,displayName,passwordCredentials,keyCredentials"}):
        out.append(
            Asset(
                id=f"tenants/{tid}/applications/{app['id']}",
                provider=Provider.ENTRA,
                type=APP_TYPE,
                name=app.get("displayName") or app["appId"],
                scope=tid,
                properties={
                    "app_id": app.get("appId"),
                    "secrets": [
                        {
                            "key_id": c.get("keyId"),
                            "name": c.get("displayName"),
                            "hint": c.get("hint"),
                            "valid_from": c.get("startDateTime"),
                            "expires": c.get("endDateTime"),
                        }
                        for c in app.get("passwordCredentials") or []
                    ],
                    "certificates": [
                        {"key_id": c.get("keyId"), "expires": c.get("endDateTime")}
                        for c in app.get("keyCredentials") or []
                    ],
                },
            )
        )
    return out


def _graph_permissions(ctx: AzureContext) -> dict[str, list[str]]:
    """principal object id -> Graph application permission names granted to it."""
    g = graph(ctx)
    graph_sp = g.get(f"servicePrincipals(appId='{GRAPH_APP_ID}')", {"$select": "id,appRoles"})
    names = {r["id"]: r["value"] for r in graph_sp.get("appRoles", [])}
    grants: dict[str, list[str]] = defaultdict(list)
    for a in g.list(f"servicePrincipals/{graph_sp['id']}/appRoleAssignedTo"):
        if a.get("appRoleId") in names:
            grants[a["principalId"]].append(names[a["appRoleId"]])
    return grants


def _service_principals(ctx: AzureContext, tid: str) -> list[Asset]:
    grants = _graph_permissions(ctx)
    out = []
    select = "id,appId,displayName,servicePrincipalType,appOwnerOrganizationId,accountEnabled"
    for sp in graph(ctx).list("servicePrincipals", {"$select": select, "$top": "999"}):
        perms = sorted(grants.get(sp["id"], []))
        props: dict[str, Any] = {
            "object_id": sp["id"],
            "app_id": sp.get("appId"),
            "sp_type": sp.get("servicePrincipalType"),
            "first_party": sp.get("appOwnerOrganizationId") in MICROSOFT_TENANTS,
            "owned_by_tenant": sp.get("appOwnerOrganizationId") == tid,
            "account_enabled": sp.get("accountEnabled"),
            "graph_app_permissions": perms,
            "admin_scope": bool(HIGH_PRIVILEGE_GRAPH_PERMISSIONS.intersection(perms)),
        }
        out.append(
            Asset(
                id=f"tenants/{tid}/servicePrincipals/{sp['id']}",
                provider=Provider.ENTRA,
                type=SP_TYPE,
                name=sp.get("displayName") or sp["id"],
                scope=tid,
                properties=props,
            )
        )
    return out

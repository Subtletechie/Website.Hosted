"""Users plus MFA registration state (userRegistrationDetails report)."""

from __future__ import annotations

from typing import Any

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra.common import graph, is_premium_error, tenant_id
from subtlescan.models import Asset, GapReason, Provider

ASSET_TYPE = "entra.user"


def collect(ctx: AzureContext) -> list[Asset]:
    g = graph(ctx)
    tid = tenant_id(ctx)
    users: dict[str, Asset] = {}
    for u in g.list(
        "users",
        {"$select": "id,displayName,userPrincipalName,userType,accountEnabled,onPremisesSyncEnabled", "$top": "999"},
    ):
        users[u["id"]] = Asset(
            id=f"tenants/{tid}/users/{u['id']}",
            provider=Provider.ENTRA,
            type=ASSET_TYPE,
            name=u.get("userPrincipalName") or u["id"],
            scope=tid,
            properties={
                "object_id": u["id"],
                "display_name": u.get("displayName"),
                "user_type": (u.get("userType") or "Member").lower(),
                "account_enabled": u.get("accountEnabled"),
                "cloud_only": not u.get("onPremisesSyncEnabled"),
                "internet_exposed": True,
            },
        )
    try:
        for r in g.list("reports/authenticationMethods/userRegistrationDetails"):
            asset = users.get(r.get("id", ""))
            if asset is not None:
                asset.properties |= _registration(r)
    except Exception as exc:  # noqa: BLE001
        reason, detail = ctx.classify(exc)
        if is_premium_error(exc):
            reason, detail = GapReason.UNSUPPORTED, "MFA registration report needs an Entra ID P1 licence."
        ctx.gap(tid, "entra.mfa_registration", reason, detail)
    return list(users.values())


def _registration(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "mfa_registered": bool(r.get("isMfaRegistered")),
        "is_admin": bool(r.get("isAdmin")),
        "mfa_methods": list(r.get("methodsRegistered") or []),
    }

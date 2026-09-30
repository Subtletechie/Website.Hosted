"""Tenant-wide settings: security defaults, Conditional Access, authorization (consent / guest) policy."""

from __future__ import annotations

from typing import Any

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra.common import compact, graph, is_premium_error, tenant_id
from subtlescan.models import Asset, GapReason, Provider

ASSET_TYPE = "entra.tenant"


def normalize_ca_policy(p: dict[str, Any]) -> dict[str, Any]:
    cond = p.get("conditions") or {}
    return {
        "id": p.get("id"),
        "name": p.get("displayName"),
        "state": p.get("state"),
        "include_users": compact(cond, "users", "includeUsers"),
        "exclude_users": compact(cond, "users", "excludeUsers"),
        "exclude_groups": compact(cond, "users", "excludeGroups"),
        "include_roles": compact(cond, "users", "includeRoles"),
        "include_applications": compact(cond, "applications", "includeApplications"),
        "client_app_types": compact(cond, "clientAppTypes"),
        "built_in_controls": compact(p, "grantControls", "builtInControls"),
    }


def collect(ctx: AzureContext) -> list[Asset]:
    g = graph(ctx)
    tid = tenant_id(ctx)
    org = g.get(f"organization/{tid}", {"$select": "id,displayName,verifiedDomains"})
    props: dict[str, Any] = {
        "internet_exposed": True,  # sign-in endpoints are public by design
        "security_defaults_enabled": None,
        "ca_policies": None,
        "ca_available": None,
        "user_consent_policies": None,
        "allow_invites_from": None,
        "verified_domains": [d.get("name") for d in org.get("verifiedDomains", [])],
    }
    with ctx.guard("tenant", "entra.security_defaults"):
        props["security_defaults_enabled"] = bool(
            g.get("policies/identitySecurityDefaultsEnforcementPolicy").get("isEnabled")
        )
    try:
        props["ca_policies"] = [normalize_ca_policy(p) for p in g.list("identity/conditionalAccess/policies")]
        props["ca_available"] = True
    except Exception as exc:  # noqa: BLE001
        if is_premium_error(exc):
            # No Entra ID P1: Conditional Access cannot exist, so "no policies" is the truth.
            props["ca_policies"], props["ca_available"] = [], False
            ctx.gap(
                tid,
                "entra.conditional_access",
                GapReason.UNSUPPORTED,
                "Tenant has no Entra ID P1 licence, so Conditional Access is unavailable.",
            )
        else:
            reason, detail = ctx.classify(exc)
            ctx.gap(tid, "entra.conditional_access", reason, detail)
    with ctx.guard("tenant", "entra.authorization_policy"):
        auth = g.get("policies/authorizationPolicy")
        props["user_consent_policies"] = compact(auth, "defaultUserRolePermissions", "permissionGrantPoliciesAssigned")
        props["allow_invites_from"] = auth.get("allowInvitesFrom")
    return [
        Asset(
            id=f"tenants/{tid}",
            provider=Provider.ENTRA,
            type=ASSET_TYPE,
            name=org.get("displayName") or tid,
            scope=tid,
            properties=props,
        )
    ]

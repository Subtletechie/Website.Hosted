from __future__ import annotations

from subtlescan.checks.entra.helpers import (
    MAX_PERMANENT_GLOBAL_ADMINS,
    enabled_policies,
    excluded_from,
    legacy_auth_allowed,
)
from subtlescan.checks.registry import Hit, check
from subtlescan.collectors.entra.constants import GLOBAL_ADMIN_TEMPLATE
from subtlescan.collectors.entra.roles import ASSET_TYPE as ROLE
from subtlescan.collectors.entra.tenant import ASSET_TYPE as TENANT
from subtlescan.inventory import Inventory
from subtlescan.models import Domain, Provider, Severity

LEGACY_CONSENT = "microsoft-user-default-legacy"


@check(id="ENTRA-ID-001", provider=Provider.ENTRA, severity=Severity.CRITICAL, domain=Domain.IDENTITY)
def no_baseline_sign_in_protection(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    if t is None or t.properties.get("security_defaults_enabled") is not False:
        return []
    if t.properties.get("ca_policies") is None or enabled_policies(t.properties):
        return []
    report_only = [p for p in t.properties["ca_policies"] if p.get("state") == "enabledForReportingButNotEnforced"]
    return [
        Hit(
            t,
            {
                "securityDefaults": "disabled",
                "enabledCaPolicies": 0,
                "reportOnlyCaPolicies": len(report_only),
                "conditionalAccessLicensed": t.properties.get("ca_available"),
            },
        )
    ]


@check(id="ENTRA-ID-002", provider=Provider.ENTRA, severity=Severity.HIGH, domain=Domain.IDENTITY)
def legacy_auth_not_blocked(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    # With no enforced CA at all, ENTRA-ID-001 already covers this; don't double-report.
    if t is None or not enabled_policies(t.properties) or legacy_auth_allowed(t.properties) is not True:
        return []
    return [
        Hit(
            t,
            {
                "securityDefaults": "disabled",
                "enabledCaPolicies": len(enabled_policies(t.properties)),
                "policiesBlockingLegacyAuth": 0,
            },
        )
    ]


@check(id="ENTRA-ID-004", provider=Provider.ENTRA, severity=Severity.HIGH, domain=Domain.IDENTITY)
def too_many_global_admins(inv: Inventory) -> list[Hit]:
    hits = []
    for role in inv.of_type(ROLE):
        if role.properties.get("template_id") != GLOBAL_ADMIN_TEMPLATE:
            continue
        permanent = [a for a in role.properties.get("assignments", []) if not a.get("time_bound")]
        if len(permanent) > MAX_PERMANENT_GLOBAL_ADMINS:
            hits.append(
                Hit(
                    role,
                    {
                        "permanentGlobalAdmins": len(permanent),
                        "recommendedMax": MAX_PERMANENT_GLOBAL_ADMINS,
                        "members": ", ".join(sorted(a["principal_name"] for a in permanent)),
                    },
                )
            )
    return hits


@check(id="ENTRA-ID-005", provider=Provider.ENTRA, severity=Severity.MEDIUM, domain=Domain.IDENTITY)
def no_break_glass_account(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    ga = next((r for r in inv.of_type(ROLE) if r.properties.get("template_id") == GLOBAL_ADMIN_TEMPLATE), None)
    if t is None or ga is None or t.properties.get("ca_policies") is None:
        return []
    policies = enabled_policies(t.properties)
    cloud_only = [
        a
        for a in ga.properties.get("assignments", [])
        if a.get("principal_type") == "user" and a["principal_name"].lower().endswith(".onmicrosoft.com")
    ]
    candidates = [a for a in cloud_only if all(excluded_from(p, a["principal_id"]) for p in policies)]
    if candidates:
        return []
    return [
        Hit(
            t,
            {
                "cloudOnlyGlobalAdmins": len(cloud_only),
                "excludedFromAllCaPolicies": 0,
                "enabledCaPolicies": len(policies),
            },
        )
    ]


@check(id="ENTRA-ID-006", provider=Provider.ENTRA, severity=Severity.MEDIUM, domain=Domain.IDENTITY)
def users_can_consent_to_apps(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    policies = (t.properties.get("user_consent_policies") if t else None) or []
    if t is None or not any(p.endswith(LEGACY_CONSENT) for p in policies):
        return []
    return [Hit(t, {"permissionGrantPoliciesAssigned": ", ".join(policies)})]


@check(id="ENTRA-ID-007", provider=Provider.ENTRA, severity=Severity.LOW, domain=Domain.IDENTITY)
def anyone_can_invite_guests(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    if t is None or t.properties.get("allow_invites_from") != "everyone":
        return []
    return [Hit(t, {"allowInvitesFrom": "everyone (including existing guests)"})]

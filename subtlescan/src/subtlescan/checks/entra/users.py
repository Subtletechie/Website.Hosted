from __future__ import annotations

from subtlescan.checks.registry import Hit, check
from subtlescan.collectors.entra.tenant import ASSET_TYPE as TENANT
from subtlescan.collectors.entra.users import ASSET_TYPE as USER
from subtlescan.inventory import Inventory
from subtlescan.models import Asset, Domain, Provider, Severity

MAX_EXAMPLES = 15


def _active_members_without_mfa(inv: Inventory) -> list[Asset]:
    return [
        u
        for u in inv.of_type(USER)
        if u.properties.get("mfa_registered") is False  # absent = report not readable
        and u.properties.get("user_type") == "member"
        and u.properties.get("account_enabled") is not False
    ]


@check(id="ENTRA-ID-003", provider=Provider.ENTRA, severity=Severity.HIGH, domain=Domain.IDENTITY)
def users_without_mfa(inv: Inventory) -> list[Hit]:
    t = inv.one(TENANT)
    missing = _active_members_without_mfa(inv)
    if t is None or not missing:
        return []
    members = [u for u in inv.of_type(USER) if u.properties.get("user_type") == "member"]
    names = sorted(u.name for u in missing)
    return [
        Hit(
            t,
            {
                "usersWithoutMfa": len(missing),
                "ofMembers": len(members),
                "examples": ", ".join(names[:MAX_EXAMPLES]) + (" …" if len(names) > MAX_EXAMPLES else ""),
            },
            name=f"{len(missing)} user account(s)",
        )
    ]


@check(id="ENTRA-ID-008", provider=Provider.ENTRA, severity=Severity.CRITICAL, domain=Domain.IDENTITY)
def admin_without_mfa(inv: Inventory) -> list[Hit]:
    return [
        Hit(
            u,
            {
                "isAdmin": True,
                "mfaRegistered": False,
                "methodsRegistered": ", ".join(u.properties.get("mfa_methods") or []) or "none",
            },
        )
        for u in _active_members_without_mfa(inv)
        if u.properties.get("is_admin")
    ]

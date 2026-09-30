from __future__ import annotations

from subtlescan.checks.registry import Hit, check
from subtlescan.collectors.azure.authorization import ADMIN_ROLES
from subtlescan.collectors.azure.authorization import ASSET_TYPE as ROLE_ASSIGNMENT
from subtlescan.collectors.entra.apps import SP_TYPE
from subtlescan.inventory import Inventory
from subtlescan.models import Domain, Provider, Severity


def _at_or_above_subscription(scope: str) -> bool:
    parts = [p for p in scope.split("/") if p]
    return scope == "/" or parts[:1] == ["providers"] or (len(parts) == 2 and parts[0].lower() == "subscriptions")


@check(id="AZ-IAM-001", provider=Provider.AZURE, severity=Severity.HIGH, domain=Domain.IDENTITY)
def service_principal_subscription_admin(inv: Inventory) -> list[Hit]:
    sp_names = {sp.properties.get("object_id"): sp.name for sp in inv.of_type(SP_TYPE)}
    hits = []
    for ra in inv.of_type(ROLE_ASSIGNMENT):
        p = ra.properties
        if p.get("principal_type") != "ServicePrincipal" or p.get("role_name") not in ADMIN_ROLES:
            continue
        if not _at_or_above_subscription(p.get("assignment_scope", "")):
            continue
        name = sp_names.get(p.get("principal_id")) or f"service principal {p.get('principal_id')}"
        hits.append(
            Hit(
                ra,
                {"role": p["role_name"], "scope": p["assignment_scope"], "principalId": p["principal_id"]},
                name=name,
            )
        )
    return hits

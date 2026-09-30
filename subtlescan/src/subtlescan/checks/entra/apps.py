from __future__ import annotations

from datetime import datetime

from subtlescan.checks.registry import Hit, check
from subtlescan.collectors.entra.apps import APP_TYPE, SP_TYPE
from subtlescan.collectors.entra.constants import HIGH_PRIVILEGE_GRAPH_PERMISSIONS
from subtlescan.inventory import Inventory
from subtlescan.models import Domain, Provider, Severity

MAX_SECRET_DAYS = 365


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


@check(id="ENTRA-APP-001", provider=Provider.ENTRA, severity=Severity.MEDIUM, domain=Domain.IDENTITY)
def long_lived_app_secrets(inv: Inventory) -> list[Hit]:
    hits = []
    for app in inv.of_type(APP_TYPE):
        long_lived = []
        for s in app.properties.get("secrets", []):
            start, end = _dt(s.get("valid_from")), _dt(s.get("expires"))
            if start and end and end > inv.as_of and (end - start).days > MAX_SECRET_DAYS:
                long_lived.append(
                    f"{s.get('hint') or '?'}… ({s.get('name') or 'unnamed'}, "
                    f"{(end - start).days} days, expires {end.date()})"
                )
        if long_lived:
            hits.append(Hit(app, {"longLivedSecrets": "; ".join(long_lived), "maxRecommendedDays": MAX_SECRET_DAYS}))
    return hits


@check(id="ENTRA-APP-002", provider=Provider.ENTRA, severity=Severity.HIGH, domain=Domain.IDENTITY)
def high_privilege_graph_permissions(inv: Inventory) -> list[Hit]:
    hits = []
    for sp in inv.of_type(SP_TYPE):
        if sp.properties.get("first_party"):
            continue
        risky = sorted(HIGH_PRIVILEGE_GRAPH_PERMISSIONS.intersection(sp.properties.get("graph_app_permissions", [])))
        if risky:
            hits.append(
                Hit(
                    sp,
                    {
                        "highPrivilegePermissions": ", ".join(risky),
                        "allGraphAppPermissions": len(sp.properties["graph_app_permissions"]),
                        "appId": sp.properties.get("app_id"),
                    },
                )
            )
    return hits

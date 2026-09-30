from __future__ import annotations

from subtlescan.checks.registry import Hit, check
from subtlescan.collectors.azure.storage import ASSET_TYPE
from subtlescan.inventory import Inventory
from subtlescan.models import Domain, Provider, Severity

MIN_SOFT_DELETE_DAYS = 7


@check(id="AZ-STG-001", provider=Provider.AZURE, severity=Severity.HIGH, domain=Domain.DATA)
def public_blob_access_allowed(inv: Inventory) -> list[Hit]:
    hits = []
    for sa in inv.of_type(ASSET_TYPE):
        value = sa.properties.get("allow_blob_public_access")
        if value is not False:  # None = never set; Azure treats it as allowed
            hits.append(Hit(sa, {"allowBlobPublicAccess": "not set (defaults to allowed)" if value is None else value}))
    return hits


@check(id="AZ-STG-002", provider=Provider.AZURE, severity=Severity.MEDIUM, domain=Domain.IDENTITY)
def shared_key_access_allowed(inv: Inventory) -> list[Hit]:
    hits = []
    for sa in inv.of_type(ASSET_TYPE):
        value = sa.properties.get("allow_shared_key_access")
        if value is not False:
            hits.append(Hit(sa, {"allowSharedKeyAccess": "not set (defaults to allowed)" if value is None else value}))
    return hits


@check(id="AZ-STG-003", provider=Provider.AZURE, severity=Severity.MEDIUM, domain=Domain.RECOVERY)
def blob_soft_delete_weak(inv: Inventory) -> list[Hit]:
    hits = []
    for sa in inv.of_type(ASSET_TYPE):
        if "blob_soft_delete_enabled" not in sa.properties:
            continue  # blob service not readable or not applicable; recorded as a coverage gap
        enabled = sa.properties["blob_soft_delete_enabled"]
        days = sa.properties.get("blob_soft_delete_days") or 0
        if not enabled or days < MIN_SOFT_DELETE_DAYS:
            hits.append(
                Hit(
                    sa,
                    {
                        "blobSoftDelete": "enabled" if enabled else "disabled",
                        "retentionDays": days if enabled else None,
                        "versioning": "enabled" if sa.properties.get("versioning_enabled") else "disabled",
                        "recommendedMinimumDays": MIN_SOFT_DELETE_DAYS,
                    },
                )
            )
    return hits

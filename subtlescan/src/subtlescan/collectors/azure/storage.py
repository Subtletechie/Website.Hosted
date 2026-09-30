"""Azure Storage accounts + blob service data-protection settings."""

from __future__ import annotations

from typing import Any

from azure.mgmt.storage import StorageManagementClient

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.models import Asset, Provider

ASSET_TYPE = "azure.storage_account"


def _v(value: Any) -> Any:
    """SDK enums -> plain strings."""
    return getattr(value, "value", value)


def resource_group_of(resource_id: str) -> str | None:
    parts = resource_id.split("/")
    lowered = [p.lower() for p in parts]
    if "resourcegroups" in lowered:
        return parts[lowered.index("resourcegroups") + 1]
    return None


def normalize_account(acct: Any, sub_id: str) -> Asset:
    acls = acct.network_rule_set
    public_network = _v(acct.public_network_access)
    default_action = _v(acls.default_action) if acls else None
    return Asset(
        id=acct.id,
        provider=Provider.AZURE,
        type=ASSET_TYPE,
        name=acct.name,
        scope=sub_id,
        location=acct.location,
        resource_group=resource_group_of(acct.id),
        tags=dict(acct.tags or {}),
        properties={
            "kind": _v(acct.kind),
            "sku": _v(acct.sku.name) if acct.sku else None,
            # None means "never set": Azure treats both of these as allowed.
            "allow_blob_public_access": acct.allow_blob_public_access,
            "allow_shared_key_access": acct.allow_shared_key_access,
            "minimum_tls_version": _v(acct.minimum_tls_version),
            "https_only": acct.enable_https_traffic_only,
            "public_network_access": public_network,
            "network_default_action": default_action,
            # Reachable from any internet address (no firewall, no private-only access).
            "internet_exposed": public_network != "Disabled" and default_action in (None, "Allow"),
        },
    )


def _blob_protection(client: Any, asset: Asset) -> dict[str, Any]:
    props = client.blob_services.get_service_properties(asset.resource_group, asset.name)
    soft = props.delete_retention_policy
    container_soft = props.container_delete_retention_policy
    return {
        "blob_soft_delete_enabled": bool(soft and soft.enabled),
        "blob_soft_delete_days": soft.days if soft and soft.enabled else None,
        "container_soft_delete_enabled": bool(container_soft and container_soft.enabled),
        "versioning_enabled": bool(props.is_versioning_enabled),
    }


def collect(ctx: AzureContext) -> list[Asset]:
    assets: list[Asset] = []
    for sub_id in ctx.subscriptions:
        client = ctx.client(StorageManagementClient, sub_id)
        with ctx.guard(sub_id, "storage.accounts"):
            accounts = [normalize_account(a, sub_id) for a in client.storage_accounts.list()]
            for asset in accounts:
                # Premium FileStorage / BlockBlob-less kinds have no blob service.
                if asset.properties["kind"] in ("StorageV2", "BlobStorage", "BlockBlobStorage", "Storage"):
                    with ctx.guard(sub_id, f"storage.blob_service:{asset.name}"):
                        asset.properties |= _blob_protection(client, asset)
            assets.extend(accounts)
    return assets

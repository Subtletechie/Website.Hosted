"""Azure RBAC role assignments that apply at subscription scope (including inherited from above)."""

from __future__ import annotations

from typing import Any

from azure.mgmt.authorization import AuthorizationManagementClient

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.models import Asset, Provider

ASSET_TYPE = "azure.role_assignment"
ADMIN_ROLES = {"Owner", "User Access Administrator", "Role Based Access Control Administrator"}


def _v(value: Any) -> Any:
    return getattr(value, "value", value)


def _last(resource_id: str) -> str:
    return resource_id.rstrip("/").rsplit("/", 1)[-1].lower()


def collect(ctx: AzureContext) -> list[Asset]:
    assets: list[Asset] = []
    for sub in ctx.subscriptions:
        scope = f"/subscriptions/{sub}"
        client = ctx.client(AuthorizationManagementClient, sub)
        with ctx.guard(sub, "authorization.role_assignments"):
            names = {_last(d.id): d.role_name for d in client.role_definitions.list(scope)}
            for ra in client.role_assignments.list_for_scope(scope, filter="atScope()"):
                role = names.get(_last(ra.role_definition_id), _last(ra.role_definition_id))
                assets.append(
                    Asset(
                        id=ra.id,
                        provider=Provider.AZURE,
                        type=ASSET_TYPE,
                        name=f"{role} on {ra.scope}",
                        scope=sub,
                        properties={
                            "principal_id": ra.principal_id,
                            "principal_type": _v(ra.principal_type),
                            "role_name": role,
                            "assignment_scope": ra.scope,
                            "admin_scope": role in ADMIN_ROLES,
                        },
                    )
                )
    return assets

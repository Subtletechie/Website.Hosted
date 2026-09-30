"""Microsoft Entra ID (tenant) collectors, read through Microsoft Graph."""

from __future__ import annotations

from subtlescan.collectors.azure.context import AzureContext
from subtlescan.collectors.entra import apps, roles, tenant, users
from subtlescan.models import Asset


def collect(ctx: AzureContext) -> list[Asset]:
    assets: list[Asset] = []
    for name, module in (("tenant", tenant), ("users", users), ("roles", roles), ("apps", apps)):
        with ctx.guard("tenant", f"entra.{name}"):
            assets.extend(module.collect(ctx))
    return assets

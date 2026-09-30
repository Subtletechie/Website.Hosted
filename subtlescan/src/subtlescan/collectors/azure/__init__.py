from __future__ import annotations

from collections.abc import Callable

from subtlescan.collectors.azure import storage
from subtlescan.collectors.azure.context import AzureContext
from subtlescan.models import Asset

Collector = Callable[[AzureContext], list[Asset]]

COLLECTORS: dict[str, Collector] = {
    "storage": storage.collect,
}


def collect_all(ctx: AzureContext) -> list[Asset]:
    assets: list[Asset] = []
    for name, collector in COLLECTORS.items():
        with ctx.guard("*", name):
            assets.extend(collector(ctx))
    return assets

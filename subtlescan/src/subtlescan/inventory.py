"""Normalized inventory: the only input checks see."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from pathlib import Path

from subtlescan import runfolder
from subtlescan.models import Asset


class Inventory:
    def __init__(self, assets: Iterable[Asset]) -> None:
        self.assets: list[Asset] = list(assets)
        self._by_type: dict[str, list[Asset]] = defaultdict(list)
        for a in self.assets:
            self._by_type[a.type].append(a)

    def of_type(self, asset_type: str) -> list[Asset]:
        return list(self._by_type.get(asset_type, []))

    def __iter__(self) -> Iterator[Asset]:
        return iter(self.assets)

    def __len__(self) -> int:
        return len(self.assets)

    @classmethod
    def load(cls, run_dir: Path) -> Inventory:
        return cls(runfolder.read_inventory(run_dir))

    def save(self, run_dir: Path) -> None:
        runfolder.write_inventory(run_dir, self.assets)

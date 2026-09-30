"""Framework mappings: frameworks/<key>.yaml holds a name, control titles, and check_id -> controls."""

from __future__ import annotations

from functools import cache
from importlib import resources

import yaml
from pydantic import BaseModel, Field


class Framework(BaseModel):
    key: str
    name: str
    controls: dict[str, str] = Field(default_factory=dict)
    mappings: dict[str, list[str]] = Field(default_factory=dict)


@cache
def load_frameworks() -> dict[str, Framework]:
    out: dict[str, Framework] = {}
    for f in sorted(resources.files(__package__).iterdir(), key=lambda p: p.name):
        if f.name.endswith(".yaml"):
            key = f.name.removesuffix(".yaml")
            fw = Framework.model_validate({"key": key, **yaml.safe_load(f.read_text())})
            unknown = {c for cs in fw.mappings.values() for c in cs} - fw.controls.keys()
            if unknown:
                raise ValueError(f"frameworks/{f.name}: controls used but not defined: {sorted(unknown)}")
            out[key] = fw
    return out


def mappings_for(check_id: str) -> dict[str, list[str]]:
    return {k: fw.mappings[check_id] for k, fw in load_frameworks().items() if check_id in fw.mappings}

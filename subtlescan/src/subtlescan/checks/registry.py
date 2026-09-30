"""Check registry.

A check is a pure function: Inventory in, list[Hit] out. It decides *whether* something is wrong
and records evidence. Everything client-facing (title, business impact, remediation, Terraform,
effort) comes from library/*.yaml, and framework mappings come from frameworks/*.yaml, so wording
can be tuned without touching logic.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from subtlescan.inventory import Inventory
from subtlescan.models import Asset, Domain, Provider, Severity


@dataclass(frozen=True)
class Hit:
    resource: Asset
    evidence: dict[str, Any] = field(default_factory=dict)


CheckFn = Callable[[Inventory], list[Hit]]


@dataclass(frozen=True)
class CheckSpec:
    id: str
    provider: Provider
    severity: Severity
    domain: Domain
    fn: CheckFn


REGISTRY: dict[str, CheckSpec] = {}


def check(*, id: str, provider: Provider, severity: Severity, domain: Domain) -> Callable[[CheckFn], CheckFn]:
    def register(fn: CheckFn) -> CheckFn:
        if id in REGISTRY:
            raise ValueError(f"duplicate check id {id}")
        REGISTRY[id] = CheckSpec(id=id, provider=provider, severity=severity, domain=domain, fn=fn)
        return fn

    return register


def load_all() -> dict[str, CheckSpec]:
    """Import every check module so its decorators run."""
    import subtlescan.checks.azure  # noqa: F401

    return REGISTRY


def checks_for(provider: Provider) -> list[CheckSpec]:
    return [c for c in load_all().values() if c.provider is provider]

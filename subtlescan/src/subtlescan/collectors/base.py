from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from subtlescan.models import CoverageGap, GapReason, Provider
from subtlescan.runlog import log

Classifier = Callable[[BaseException], tuple[GapReason, str]]


def default_classifier(exc: BaseException) -> tuple[GapReason, str]:
    return GapReason.ERROR, f"{type(exc).__name__}: {exc}"


@dataclass
class CollectContext:
    provider: Provider
    classify: Classifier = default_classifier
    gaps: list[CoverageGap] = field(default_factory=list)

    def gap(self, scope: str, service: str, reason: GapReason, detail: str) -> None:
        log.warning(
            "coverage gap: %s/%s %s: %s",
            scope,
            service,
            reason.value,
            detail,
            extra={"event": "coverage_gap", "scope": scope, "service": service, "reason": reason.value},
        )
        self.gaps.append(
            CoverageGap(provider=self.provider, scope=scope, service=service, reason=reason, detail=detail)
        )

    @contextmanager
    def guard(self, scope: str, service: str) -> Iterator[None]:
        """Turn any failure inside the block into a coverage gap instead of a crash."""
        try:
            yield
        except Exception as exc:  # noqa: BLE001 - degrading gracefully is the contract
            reason, detail = self.classify(exc)
            self.gap(scope, service, reason, detail)

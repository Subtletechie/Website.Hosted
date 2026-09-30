"""Hard rule 4: every check yields complete findings (library text, framework mappings, effort)."""

from __future__ import annotations

import pytest

from subtlescan.checks.registry import load_all
from subtlescan.frameworks import load_frameworks, mappings_for
from subtlescan.library import load_library

CHECKS = sorted(load_all())


@pytest.mark.parametrize("check_id", CHECKS)
def test_check_has_library_entry(check_id: str) -> None:
    entry = load_library()[check_id]
    assert entry.title and entry.business_impact.strip() and entry.remediation.strip()


@pytest.mark.parametrize("check_id", CHECKS)
def test_check_has_framework_mapping(check_id: str) -> None:
    assert mappings_for(check_id), f"{check_id} is not mapped to any framework"


def test_library_has_no_orphans() -> None:
    assert set(load_library()) <= set(CHECKS)


def test_frameworks_load_and_validate() -> None:
    assert {"soc2", "cis_azure", "nist_csf", "iso27001", "hipaa"} <= set(load_frameworks())

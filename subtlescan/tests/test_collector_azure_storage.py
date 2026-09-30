from __future__ import annotations

from conftest import SUB, fake_context

from subtlescan.collectors.azure import collect_all
from subtlescan.models import GapReason


def test_storage_collector_normalizes_recorded_fixtures() -> None:
    ctx = fake_context()
    assert ctx.discover_subscriptions() == [SUB]  # disabled subscription skipped
    assets = {a.name: a for a in collect_all(ctx)}
    assert set(assets) == {"acmecustomerdata", "acmelocked", "acmeoldfiles"}

    public = assets["acmecustomerdata"]
    assert public.resource_group == "rg-prod"
    assert public.tags == {"env": "prod"}
    assert public.properties["allow_blob_public_access"] is True
    assert public.properties["allow_shared_key_access"] is None
    assert public.properties["internet_exposed"] is True
    assert public.properties["blob_soft_delete_enabled"] is False
    assert public.properties["minimum_tls_version"] == "TLS1_2"

    locked = assets["acmelocked"].properties
    assert locked["internet_exposed"] is False
    assert locked["blob_soft_delete_days"] == 14
    assert locked["versioning_enabled"] is True


def test_missing_permission_becomes_coverage_gap_not_crash() -> None:
    ctx = fake_context()
    ctx.discover_subscriptions()
    assets = {a.name: a for a in collect_all(ctx)}
    # 403 on one account's blob service: account still inventoried, protection keys absent, gap logged.
    assert "blob_soft_delete_enabled" not in assets["acmeoldfiles"].properties
    assert [(g.service, g.reason) for g in ctx.gaps] == [
        ("storage.blob_service:acmeoldfiles", GapReason.MISSING_PERMISSION)
    ]


def test_list_failure_is_a_gap() -> None:
    ctx = fake_context(fail_list=True)
    ctx.discover_subscriptions()
    assert collect_all(ctx) == []
    assert ctx.gaps[0].service == "storage.accounts"
    assert ctx.gaps[0].reason is GapReason.MISSING_PERMISSION


def test_requested_subscription_not_visible_is_a_gap() -> None:
    ctx = fake_context()
    assert ctx.discover_subscriptions(["not-mine"]) == []
    assert ctx.gaps[0].scope == "not-mine"

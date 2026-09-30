from __future__ import annotations

from conftest import storage_asset

from subtlescan.checks.azure.storage import (
    blob_soft_delete_weak,
    public_blob_access_allowed,
    shared_key_access_allowed,
)
from subtlescan.inventory import Inventory


def inv(**props: object) -> Inventory:
    return Inventory([storage_asset(**props)])


class TestPublicBlobAccess:
    def test_fail_when_enabled(self) -> None:
        hits = public_blob_access_allowed(inv(allow_blob_public_access=True))
        assert len(hits) == 1 and hits[0].evidence == {"allowBlobPublicAccess": True}

    def test_fail_when_unset(self) -> None:
        hits = public_blob_access_allowed(inv(allow_blob_public_access=None))
        assert "defaults to allowed" in hits[0].evidence["allowBlobPublicAccess"]

    def test_pass_when_disabled(self) -> None:
        assert public_blob_access_allowed(inv(allow_blob_public_access=False)) == []


class TestSharedKeyAccess:
    def test_fail(self) -> None:
        assert len(shared_key_access_allowed(inv(allow_shared_key_access=None))) == 1

    def test_pass(self) -> None:
        assert shared_key_access_allowed(inv(allow_shared_key_access=False)) == []


class TestBlobSoftDelete:
    def test_fail_when_off(self) -> None:
        hits = blob_soft_delete_weak(inv(blob_soft_delete_enabled=False, blob_soft_delete_days=None))
        assert hits[0].evidence["blobSoftDelete"] == "disabled"

    def test_fail_when_too_short(self) -> None:
        assert len(blob_soft_delete_weak(inv(blob_soft_delete_enabled=True, blob_soft_delete_days=3))) == 1

    def test_pass(self) -> None:
        assert blob_soft_delete_weak(inv(blob_soft_delete_enabled=True, blob_soft_delete_days=14)) == []

    def test_skips_when_not_collected(self) -> None:
        assert blob_soft_delete_weak(inv()) == []

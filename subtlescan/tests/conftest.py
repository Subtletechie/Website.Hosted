from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.storage.models import BlobServiceProperties, StorageAccount

from subtlescan.collectors.azure.context import AzureContext, classify_azure_error
from subtlescan.models import Asset, Provider

FIXTURES = Path(__file__).parent / "fixtures"
SUB = "00000000-0000-0000-0000-000000000001"


def forbidden() -> HttpResponseError:
    err = HttpResponseError(message="The client does not have authorization to perform action")
    err.status_code = 403
    return err


class _Accounts:
    def __init__(self, accounts: list[dict[str, Any]], fail: bool) -> None:
        self._accounts, self._fail = accounts, fail

    def list(self) -> list[StorageAccount]:
        if self._fail:
            raise forbidden()
        return [StorageAccount(a) for a in self._accounts]


class _BlobServices:
    def __init__(self, props: dict[str, Any]) -> None:
        self._props = props

    def get_service_properties(self, resource_group_name: str, account_name: str) -> BlobServiceProperties:
        raw = self._props[account_name]
        if raw == "403":
            raise forbidden()
        return BlobServiceProperties(raw)


class FakeStorageClient:
    """Replays recorded ARM JSON through the real SDK model classes."""

    def __init__(self, fail_list: bool = False) -> None:
        accounts = json.loads((FIXTURES / "azure/storage_accounts.json").read_text())
        blob = json.loads((FIXTURES / "azure/blob_services.json").read_text())
        self.storage_accounts = _Accounts(accounts, fail_list)
        self.blob_services = _BlobServices(blob)


class _Sub:
    def __init__(self, sid: str, state: str = "Enabled") -> None:
        self.subscription_id, self.state = sid, state


class FakeSubscriptionClient:
    def __init__(self) -> None:
        class _Subs:
            def list(self) -> list[_Sub]:
                return [_Sub(SUB), _Sub("disabled-sub", "Disabled")]

        self.subscriptions = _Subs()


def fake_context(fail_list: bool = False) -> AzureContext:
    def factory(cls: type[Any], sub: str | None) -> Any:
        if cls.__name__ == "SubscriptionClient":
            return FakeSubscriptionClient()
        if cls.__name__ == "StorageManagementClient":
            return FakeStorageClient(fail_list)
        raise AssertionError(f"unexpected client {cls}")

    return AzureContext(provider=Provider.AZURE, classify=classify_azure_error, tenant_id="t", client_factory=factory)


@pytest.fixture
def azure_ctx() -> AzureContext:
    return fake_context()


def storage_asset(name: str = "sa1", **props: Any) -> Asset:
    return Asset(
        id=f"/subscriptions/{SUB}/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/{name}",
        provider=Provider.AZURE,
        type="azure.storage_account",
        name=name,
        scope=SUB,
        resource_group="rg",
        properties=props,
    )

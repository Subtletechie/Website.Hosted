from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from azure.core.exceptions import HttpResponseError
from azure.mgmt.authorization.v2022_04_01.models import RoleAssignment, RoleDefinition
from azure.mgmt.storage.models import BlobServiceProperties, StorageAccount

from subtlescan.collectors.azure.context import AzureContext, classify_azure_error
from subtlescan.collectors.entra.graph import GRAPH, GraphError
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


class FakeAuthorizationClient:
    def __init__(self) -> None:
        data = json.loads((FIXTURES / "azure/role_assignments.json").read_text())

        class _Defs:
            def list(self, scope: str) -> list[RoleDefinition]:
                return [RoleDefinition.deserialize(d) for d in data["definitions"]]

        class _Assignments:
            def list_for_scope(self, scope: str, filter: str | None = None) -> list[RoleAssignment]:
                return [RoleAssignment.deserialize(a) for a in data["assignments"]]

        self.role_definitions, self.role_assignments = _Defs(), _Assignments()


class FakeGraph:
    """Replays recorded Graph responses keyed by path (query string only for nextLink pages)."""

    def __init__(self, responses: dict[str, Any], errors: dict[str, GraphError] | None = None) -> None:
        self.responses, self.errors, self.calls = responses, errors or {}, []

    def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        path = path.removeprefix(GRAPH + "/")
        self.calls.append(path)
        if path in self.errors:
            raise self.errors[path]
        if path not in self.responses:
            raise GraphError(404, "Request_ResourceNotFound", path)
        return dict(self.responses[path])

    def list(self, path: str, params: dict[str, str] | None = None) -> Any:
        page = self.get(path, params)
        while True:
            yield from page.get("value", [])
            if not page.get("@odata.nextLink"):
                return
            page = self.get(page["@odata.nextLink"])


def weak_tenant_graph(errors: dict[str, GraphError] | None = None) -> FakeGraph:
    return FakeGraph(json.loads((FIXTURES / "entra/graph_weak_tenant.json").read_text()), errors)


def fake_context(fail_list: bool = False, graph: FakeGraph | None = None) -> AzureContext:
    graph = graph or weak_tenant_graph()

    def factory(cls: type[Any], sub: str | None) -> Any:
        clients = {
            "SubscriptionClient": FakeSubscriptionClient,
            "StorageManagementClient": lambda: FakeStorageClient(fail_list),
            "AuthorizationManagementClient": FakeAuthorizationClient,
            "GraphClient": lambda: graph,
        }
        if cls.__name__ not in clients:
            raise AssertionError(f"unexpected client {cls}")
        return clients[cls.__name__]()

    return AzureContext(provider=Provider.AZURE, classify=classify_azure_error, tenant_id=None, client_factory=factory)


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

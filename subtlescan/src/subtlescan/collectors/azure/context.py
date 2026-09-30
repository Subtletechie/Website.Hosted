from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError

from subtlescan.collectors.base import CollectContext
from subtlescan.models import GapReason, Provider

ClientFactory = Callable[[type[Any], str | None], Any]


def classify_azure_error(exc: BaseException) -> tuple[GapReason, str]:
    if isinstance(exc, ClientAuthenticationError):
        return GapReason.AUTH_FAILED, str(exc).splitlines()[0]
    if isinstance(exc, HttpResponseError):
        code = getattr(exc, "graph_code", None) or (getattr(exc.error, "code", None) if exc.error else None)
        first = (exc.message or str(exc)).splitlines()[0]
        label = f"HTTP {exc.status_code}" + (f" {code}" if code else "")
        detail = first if code and first.startswith(code) else f"{label}: {first}"
        if exc.status_code in (401, 403) or code in ("AuthorizationFailed", "Forbidden", "Authorization_RequestDenied"):
            return GapReason.MISSING_PERMISSION, detail
        if code in ("FeatureNotSupportedForAccount", "NotSupported", "OperationNotSupported"):
            return GapReason.UNSUPPORTED, detail
        return GapReason.ERROR, detail
    return GapReason.ERROR, f"{type(exc).__name__}: {exc}"


def azure_credential(tenant_id: str | None) -> TokenCredential:
    """Service principal from env if present, else the signed-in Azure CLI, else the default chain."""
    from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential

    client_id, secret = os.environ.get("AZURE_CLIENT_ID"), os.environ.get("AZURE_CLIENT_SECRET")
    tenant = tenant_id or os.environ.get("AZURE_TENANT_ID")
    if client_id and secret and tenant:
        return ClientSecretCredential(tenant, client_id, secret)
    if tenant:
        return AzureCliCredential(tenant_id=tenant)
    return DefaultAzureCredential()


def _sdk_factory(credential: TokenCredential) -> ClientFactory:
    def make(client_cls: type[Any], subscription_id: str | None) -> Any:
        if subscription_id is None:
            return client_cls(credential)
        return client_cls(credential, subscription_id)

    return make


@dataclass
class AzureContext(CollectContext):
    tenant_id: str | None = None
    subscriptions: list[str] = field(default_factory=list)
    client_factory: ClientFactory | None = None

    @classmethod
    def live(cls, tenant_id: str | None) -> AzureContext:
        cred = azure_credential(tenant_id)
        return cls(
            provider=Provider.AZURE,
            classify=classify_azure_error,
            tenant_id=tenant_id,
            client_factory=_sdk_factory(cred),
        )

    def client(self, client_cls: type[Any], subscription_id: str | None = None) -> Any:
        if self.client_factory is None:
            raise RuntimeError("AzureContext has no client factory")
        return self.client_factory(client_cls, subscription_id)

    def discover_subscriptions(self, only: list[str] | None = None) -> list[str]:
        """Enabled subscriptions the identity can see; `only` narrows the list."""
        from azure.mgmt.resource.subscriptions import SubscriptionClient

        found: list[str] = []
        with self.guard("tenant", "subscriptions"):
            for sub in self.client(SubscriptionClient).subscriptions.list():
                state = getattr(sub.state, "value", sub.state)
                if state in (None, "Enabled"):
                    found.append(sub.subscription_id)
        if only:
            missing = [s for s in only if s not in found]
            for s in missing:
                self.gap(
                    s,
                    "subscriptions",
                    GapReason.MISSING_PERMISSION,
                    "Subscription requested but not visible to the scanning identity (needs Reader).",
                )
            found = [s for s in found if s in only]
        self.subscriptions = found
        return found

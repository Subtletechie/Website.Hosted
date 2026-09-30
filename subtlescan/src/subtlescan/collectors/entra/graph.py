"""Minimal Microsoft Graph client. GET only, by construction: there is no method that sends anything else.

We use azure-core (already a dependency via azure-identity) rather than msgraph-sdk: the SDK is async-only,
pulls in the Kiota stack, and its generated models make recorded-JSON test fixtures awkward. Raw Graph JSON
in, plain dicts out.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from azure.core import PipelineClient
from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
    HeadersPolicy,
    NetworkTraceLoggingPolicy,
    RetryPolicy,
    UserAgentPolicy,
)
from azure.core.rest import HttpRequest

GRAPH = "https://graph.microsoft.com/v1.0"
SCOPE = "https://graph.microsoft.com/.default"
MAX_PAGES = 200  # SMB tenants; a runaway nextLink loop must not hang a scan


class GraphError(HttpResponseError):
    """HttpResponseError that keeps Graph's error code (e.g. Authorization_RequestDenied)."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message=f"{code}: {message}")
        self.status_code = status_code
        self.graph_code = code


class GraphClient:
    def __init__(self, credential: TokenCredential, base_url: str = GRAPH) -> None:
        self._base = base_url.rstrip("/")
        self._client: PipelineClient[HttpRequest, Any] = PipelineClient(
            base_url=self._base,
            policies=[
                HeadersPolicy({"ConsistencyLevel": "eventual"}),
                UserAgentPolicy("subtlescan"),
                RetryPolicy(),
                BearerTokenCredentialPolicy(credential, SCOPE),
                NetworkTraceLoggingPolicy(),
            ],
        )

    def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        url = path if path.startswith("https://") else f"{self._base}/{path.lstrip('/')}"
        if not url.startswith(self._base):
            raise ValueError(f"refusing to follow a link outside Graph: {url}")
        resp = self._client.send_request(HttpRequest("GET", url, params=params or {}))
        if resp.status_code >= 400:
            try:
                err = resp.json().get("error", {})
            except ValueError:
                err = {}
            raise GraphError(resp.status_code, err.get("code", "Unknown"), err.get("message", resp.text()[:200]))
        body: dict[str, Any] = resp.json()
        return body

    def list(self, path: str, params: dict[str, str] | None = None) -> Iterator[dict[str, Any]]:
        """Iterate a collection across @odata.nextLink pages."""
        page = self.get(path, params)
        for _ in range(MAX_PAGES):
            yield from page.get("value", [])
            nxt = page.get("@odata.nextLink")
            if not nxt:
                return
            page = self.get(nxt)

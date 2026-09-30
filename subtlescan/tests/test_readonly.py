"""Hard rule 1: collectors are read-only. Fail if any write-verb method is referenced in collectors/."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import subtlescan.collectors

COLLECTORS = Path(subtlescan.collectors.__file__).parent

WRITE_VERB = re.compile(
    r"^(begin_)?(create|update|delete|put|patch|set|remove|regenerate|rotate|purge|start|stop|restart|"
    r"deallocate|failover|revoke|grant|add|attach|detach|associate|disassociate|modify|enable|disable|"
    r"tag|untag|run|invoke|post|write|upload|copy|move|restore|import|register|deregister|unregister|"
    r"reset|terminate|reboot|apply|execute|send|publish|lock|unlock|assign|unassign)(_|$)"
)


# The Graph client's single HTTP chokepoint. test_graph_client_only_sends_get proves it can only send GET.
ALLOWED = {"entra/graph.py": {"send_request"}}


def write_calls(source: str) -> list[str]:
    """Write-verb method calls, write-verb names passed as strings (getattr / boto3 style), and any
    reference to an Azure `begin_*` long-running operation (always a mutation). Plain attribute reads
    such as `props.delete_retention_policy` are data, not calls, and are allowed."""
    found = []
    for node in ast.walk(ast.parse(source)):
        name = None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node, ast.Attribute) and node.attr.startswith("begin_"):
            name = node.attr
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            name = node.value
        if name and WRITE_VERB.match(name):
            found.append(f"{name} (line {node.lineno})")
    return sorted(set(found))


def test_detector_catches_writes() -> None:
    src = (
        'c.storage_accounts.begin_create(x)\nc.delete_bucket()\ngetattr(c, "put_object")\nc.update(tags)\n'
        "op = c.vaults.begin_delete\n"
    )
    assert len(write_calls(src)) == 5
    reads = "c.storage_accounts.list()\nc.get_service_properties()\nd.setdefault(1)\np.delete_retention_policy\n"
    assert write_calls(reads) == []


def test_collectors_reference_no_write_verbs() -> None:
    offenders = {}
    files = sorted(COLLECTORS.rglob("*.py"))
    assert files, "no collector sources found"
    for path in files:
        rel = str(path.relative_to(COLLECTORS))
        hits = [h for h in write_calls(path.read_text()) if h.split(" ")[0] not in ALLOWED.get(rel, set())]
        if hits:
            offenders[rel] = hits
    assert offenders == {}, f"write-verb calls in collectors: {offenders}"


def test_graph_client_only_sends_get() -> None:
    tree = ast.parse((COLLECTORS / "entra/graph.py").read_text())
    requests = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "HttpRequest"]
    assert requests, "expected the Graph client to build HttpRequest objects"
    for call in requests:
        method = call.args[0]
        assert isinstance(method, ast.Constant) and method.value == "GET", ast.unparse(call)
    public = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    assert set(public) == {"get", "list"}, public

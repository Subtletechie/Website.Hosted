"""Shared interpretation of Entra settings (also used by toxic-combination rules)."""

from __future__ import annotations

from typing import Any

LEGACY_CLIENT_APP_TYPES = {"exchangeActiveSync", "other"}
MAX_PERMANENT_GLOBAL_ADMINS = 4


def enabled_policies(tenant_props: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in tenant_props.get("ca_policies") or [] if p.get("state") == "enabled"]


def blocks_legacy_auth(policy: dict[str, Any]) -> bool:
    return (
        policy.get("state") == "enabled"
        and "block" in policy.get("built_in_controls", [])
        and set(policy.get("client_app_types", [])) >= LEGACY_CLIENT_APP_TYPES
        and "All" in policy.get("include_users", [])
        and "All" in policy.get("include_applications", [])
    )


def legacy_auth_allowed(tenant_props: dict[str, Any]) -> bool | None:
    """True/False, or None when we could not read enough to say."""
    if tenant_props.get("security_defaults_enabled"):
        return False  # security defaults block legacy authentication
    if tenant_props.get("security_defaults_enabled") is None or tenant_props.get("ca_policies") is None:
        return None
    return not any(blocks_legacy_auth(p) for p in tenant_props["ca_policies"])


def excluded_from(policy: dict[str, Any], user_id: str) -> bool:
    # Group exclusions are not expanded; assume a group exclusion may cover the user (no false alarms).
    return user_id in policy.get("exclude_users", []) or bool(policy.get("exclude_groups"))

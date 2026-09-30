from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from subtlescan.checks.azure.iam import service_principal_subscription_admin
from subtlescan.checks.entra import apps, tenant, users
from subtlescan.collectors.entra.constants import GLOBAL_ADMIN_TEMPLATE
from subtlescan.inventory import Inventory
from subtlescan.models import Asset, Provider

NOW = datetime(2026, 9, 30, tzinfo=UTC)
TENANT_OK: dict[str, Any] = {
    "security_defaults_enabled": False,
    "ca_policies": [
        {
            "id": "mfa",
            "state": "enabled",
            "include_users": ["All"],
            "include_applications": ["All"],
            "client_app_types": ["all"],
            "built_in_controls": ["mfa"],
            "exclude_users": ["bg"],
            "exclude_groups": [],
        },
        {
            "id": "legacy",
            "state": "enabled",
            "include_users": ["All"],
            "include_applications": ["All"],
            "client_app_types": ["exchangeActiveSync", "other"],
            "built_in_controls": ["block"],
            "exclude_users": ["bg"],
            "exclude_groups": [],
        },
    ],
    "user_consent_policies": ["ManagePermissionGrantsForSelf.microsoft-user-default-low"],
    "allow_invites_from": "adminsAndGuestInviters",
}


def asset(t: str, name: str = "x", **props: Any) -> Asset:
    return Asset(id=f"tenants/t/{t}/{name}", provider=Provider.ENTRA, type=t, name=name, scope="t", properties=props)


def tenant_asset(**overrides: Any) -> Asset:
    return asset("entra.tenant", "Acme", **(TENANT_OK | overrides))


def ga_role(*members: tuple[str, str], time_bound: set[str] | None = None) -> Asset:
    return asset(
        "entra.directory_role",
        "Global Administrator",
        template_id=GLOBAL_ADMIN_TEMPLATE,
        assignments=[
            {
                "principal_id": pid,
                "principal_name": upn,
                "principal_type": "user",
                "time_bound": pid in (time_bound or set()),
            }
            for pid, upn in members
        ],
    )


def inv(*assets: Asset) -> Inventory:
    return Inventory(assets, as_of=NOW)


BG = ("bg", "bg-01@acme.onmicrosoft.com")


class TestBaselineProtection:
    def test_fail_no_defaults_no_ca(self) -> None:
        hits = tenant.no_baseline_sign_in_protection(inv(tenant_asset(ca_policies=[])))
        assert hits[0].evidence["enabledCaPolicies"] == 0

    def test_report_only_does_not_count(self) -> None:
        report_only = [dict(p, state="enabledForReportingButNotEnforced") for p in TENANT_OK["ca_policies"]]
        assert len(tenant.no_baseline_sign_in_protection(inv(tenant_asset(ca_policies=report_only)))) == 1

    @pytest.mark.parametrize(
        "override", [{}, {"security_defaults_enabled": True, "ca_policies": []}, {"ca_policies": None}]
    )  # None = unreadable: no false alarm
    def test_pass(self, override: dict[str, Any]) -> None:
        assert tenant.no_baseline_sign_in_protection(inv(tenant_asset(**override))) == []


class TestLegacyAuth:
    def test_fail_when_ca_exists_but_no_block(self) -> None:
        assert len(tenant.legacy_auth_not_blocked(inv(tenant_asset(ca_policies=TENANT_OK["ca_policies"][:1])))) == 1

    def test_block_scoped_to_some_users_does_not_count(self) -> None:
        partial = dict(TENANT_OK["ca_policies"][1], include_users=["u1"])
        assert (
            len(tenant.legacy_auth_not_blocked(inv(tenant_asset(ca_policies=[TENANT_OK["ca_policies"][0], partial]))))
            == 1
        )

    def test_pass(self) -> None:
        assert tenant.legacy_auth_not_blocked(inv(tenant_asset())) == []

    def test_security_defaults_pass(self) -> None:
        assert tenant.legacy_auth_not_blocked(inv(tenant_asset(security_defaults_enabled=True))) == []


class TestGlobalAdmins:
    members = [(f"u{i}", f"admin{i}@acme.com") for i in range(5)]

    def test_fail_over_four(self) -> None:
        hits = tenant.too_many_global_admins(inv(ga_role(*self.members)))
        assert hits[0].evidence["permanentGlobalAdmins"] == 5

    def test_pim_time_bound_not_counted(self) -> None:
        assert tenant.too_many_global_admins(inv(ga_role(*self.members, time_bound={"u0"}))) == []


class TestBreakGlass:
    def test_fail_when_no_cloud_only_excluded_admin(self) -> None:
        hits = tenant.no_break_glass_account(inv(tenant_asset(), ga_role(("u1", "ceo@acme.com"))))
        assert hits[0].evidence["cloudOnlyGlobalAdmins"] == 0

    def test_fail_when_cloud_only_admin_not_excluded(self) -> None:
        assert (
            len(tenant.no_break_glass_account(inv(tenant_asset(), ga_role(("u9", "admin@acme.onmicrosoft.com"))))) == 1
        )

    def test_pass(self) -> None:
        assert tenant.no_break_glass_account(inv(tenant_asset(), ga_role(("u1", "ceo@acme.com"), BG))) == []


class TestConsentAndGuests:
    def test_consent_fail(self) -> None:
        t = tenant_asset(user_consent_policies=["ManagePermissionGrantsForSelf.microsoft-user-default-legacy"])
        assert len(tenant.users_can_consent_to_apps(inv(t))) == 1

    def test_consent_pass(self) -> None:
        assert tenant.users_can_consent_to_apps(inv(tenant_asset())) == []

    def test_guests_fail(self) -> None:
        assert len(tenant.anyone_can_invite_guests(inv(tenant_asset(allow_invites_from="everyone")))) == 1

    def test_guests_pass(self) -> None:
        assert tenant.anyone_can_invite_guests(inv(tenant_asset())) == []


def user(name: str, **props: Any) -> Asset:
    return asset("entra.user", name, **({"user_type": "member", "account_enabled": True} | props))


class TestMfa:
    def test_members_without_mfa(self) -> None:
        i = inv(
            tenant_asset(),
            user("a", mfa_registered=False),
            user("b", mfa_registered=True),
            user("guest", user_type="guest", mfa_registered=False),
            user("left", account_enabled=False, mfa_registered=False),
        )
        hits = users.users_without_mfa(i)
        assert hits[0].evidence["usersWithoutMfa"] == 1 and hits[0].evidence["examples"] == "a"
        assert hits[0].name == "1 user account(s)"

    def test_members_pass(self) -> None:
        assert users.users_without_mfa(inv(tenant_asset(), user("a", mfa_registered=True))) == []

    def test_unknown_registration_is_not_a_finding(self) -> None:
        assert users.users_without_mfa(inv(tenant_asset(), user("a"))) == []

    def test_admin_without_mfa(self) -> None:
        i = inv(user("admin", mfa_registered=False, is_admin=True), user("a", mfa_registered=False, is_admin=False))
        assert [h.resource.name for h in users.admin_without_mfa(i)] == ["admin"]

    def test_admin_pass(self) -> None:
        assert users.admin_without_mfa(inv(user("admin", mfa_registered=True, is_admin=True))) == []


def secret(start: str, end: str) -> dict[str, str]:
    return {"hint": "Ab1", "name": "s", "valid_from": start, "expires": end}


class TestApps:
    def test_long_lived_secret(self) -> None:
        a = asset("entra.application", "app", secrets=[secret("2025-01-01T00:00:00Z", "2027-06-01T00:00:00Z")])
        hits = apps.long_lived_app_secrets(inv(a))
        assert "Ab1…" in hits[0].evidence["longLivedSecrets"]

    def test_short_or_expired_secrets_pass(self) -> None:
        a = asset(
            "entra.application",
            "app",
            secrets=[
                secret("2026-06-01T00:00:00Z", "2026-12-01T00:00:00Z"),
                secret("2020-01-01T00:00:00Z", "2023-01-01T00:00:00Z"),
            ],
        )
        assert apps.long_lived_app_secrets(inv(a)) == []

    def test_high_privilege_graph(self) -> None:
        sp = asset("entra.service_principal", "sync", graph_app_permissions=["Mail.Read", "User.Read.All"])
        assert apps.high_privilege_graph_permissions(inv(sp))[0].evidence["highPrivilegePermissions"] == "Mail.Read"

    def test_graph_pass_low_privilege_or_first_party(self) -> None:
        low = asset("entra.service_principal", "a", graph_app_permissions=["User.Read.All"])
        ms = asset("entra.service_principal", "b", graph_app_permissions=["Mail.Read"], first_party=True)
        assert apps.high_privilege_graph_permissions(inv(low, ms)) == []


def assignment(role: str, ptype: str, scope: str) -> Asset:
    return Asset(
        id=f"{scope}/providers/Microsoft.Authorization/roleAssignments/{role}{ptype}",
        provider=Provider.AZURE,
        type="azure.role_assignment",
        name=role,
        scope="s",
        properties={"principal_id": "sp1", "principal_type": ptype, "role_name": role, "assignment_scope": scope},
    )


class TestServicePrincipalAdmin:
    def test_fail_owner_at_subscription(self) -> None:
        sp = asset("entra.service_principal", "deploy", object_id="sp1")
        hits = service_principal_subscription_admin(
            inv(sp, assignment("Owner", "ServicePrincipal", "/subscriptions/s"))
        )
        assert hits[0].name == "deploy"

    def test_fail_inherited_from_management_group(self) -> None:
        a = assignment(
            "User Access Administrator", "ServicePrincipal", "/providers/Microsoft.Management/managementGroups/root"
        )
        assert len(service_principal_subscription_admin(inv(a))) == 1

    @pytest.mark.parametrize(
        "role,ptype,scope",
        [
            ("Contributor", "ServicePrincipal", "/subscriptions/s"),
            ("Owner", "User", "/subscriptions/s"),
            ("Owner", "ServicePrincipal", "/subscriptions/s/resourceGroups/rg-app"),
        ],
    )
    def test_pass(self, role: str, ptype: str, scope: str) -> None:
        assert service_principal_subscription_admin(inv(assignment(role, ptype, scope))) == []

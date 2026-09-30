from __future__ import annotations

from conftest import fake_context, weak_tenant_graph

from subtlescan.collectors.entra import collect
from subtlescan.collectors.entra.graph import GraphError
from subtlescan.models import Asset, GapReason

TID = "11111111-1111-1111-1111-111111111111"


def by_type(assets: list[Asset], t: str) -> dict[str, Asset]:
    return {a.name: a for a in assets if a.type == t}


def test_collects_tenant_users_roles_apps() -> None:
    ctx = fake_context()
    assets = collect(ctx)
    assert ctx.tenant_id == TID  # discovered from /organization
    assert ctx.gaps == []

    tenant = by_type(assets, "entra.tenant")["Acme Corp"].properties
    assert tenant["security_defaults_enabled"] is False
    assert [p["state"] for p in tenant["ca_policies"]] == ["enabled", "enabledForReportingButNotEnforced"]
    assert tenant["allow_invites_from"] == "everyone"

    users = by_type(assets, "entra.user")
    assert len(users) == 6  # both pages of @odata.nextLink
    assert users["it.admin@acme.com"].properties.items() >= {"is_admin": True, "mfa_registered": False}.items()
    assert users["old.staff@acme.com"].properties["account_enabled"] is False

    ga = by_type(assets, "entra.directory_role")["Global Administrator"].properties
    assert ga["admin_scope"] is True and len(ga["assignments"]) == 7
    assert [a["principal_name"] for a in ga["assignments"] if a["time_bound"]] == ["pim.user@acme.com"]

    app = by_type(assets, "entra.application")["HR Sync"].properties
    assert app["secrets"][0]["hint"] == "Xq7"
    assert "secretText" not in str(app)

    sps = by_type(assets, "entra.service_principal")
    assert sps["HR Sync"].properties["graph_app_permissions"] == ["Files.ReadWrite.All", "Mail.Read"]
    assert sps["HR Sync"].properties["admin_scope"] is True
    assert sps["Reporting"].properties["admin_scope"] is False
    assert sps["Office 365 Exchange Online"].properties["first_party"] is True


def test_no_p1_licence_means_no_ca_not_unknown() -> None:
    graph = weak_tenant_graph(
        {
            "identity/conditionalAccess/policies": GraphError(
                403, "Authentication_RequestFromNonPremiumTenantOrB2CTenant", "x"
            ),
            "reports/authenticationMethods/userRegistrationDetails": GraphError(
                403, "Authentication_RequestFromNonPremiumTenantOrB2CTenant", "x"
            ),
            "roleManagement/directory/roleAssignmentScheduleInstances": GraphError(
                400, "AadPremiumLicenseRequired", "x"
            ),
        }
    )
    ctx = fake_context(graph=graph)
    assets = collect(ctx)
    tenant = by_type(assets, "entra.tenant")["Acme Corp"].properties
    assert tenant["ca_policies"] == [] and tenant["ca_available"] is False
    assert all("mfa_registered" not in u.properties for u in by_type(assets, "entra.user").values())
    assert {g.service: g.reason for g in ctx.gaps} == {
        "entra.conditional_access": GapReason.UNSUPPORTED,
        "entra.mfa_registration": GapReason.UNSUPPORTED,
        "entra.pim": GapReason.UNSUPPORTED,
    }


def test_missing_permission_is_gap_and_unknown() -> None:
    graph = weak_tenant_graph(
        {
            "identity/conditionalAccess/policies": GraphError(
                403, "Authorization_RequestDenied", "Insufficient privileges"
            ),
            "servicePrincipals(appId='00000003-0000-0000-c000-000000000000')": GraphError(
                403, "Authorization_RequestDenied", "no"
            ),
        }
    )
    ctx = fake_context(graph=graph)
    assets = collect(ctx)
    assert by_type(assets, "entra.tenant")["Acme Corp"].properties["ca_policies"] is None  # unknown, not "none"
    assert by_type(assets, "entra.application")  # apps still collected
    reasons = {g.service: g.reason for g in ctx.gaps}
    assert reasons["entra.conditional_access"] is GapReason.MISSING_PERMISSION
    assert reasons["entra.service_principals"] is GapReason.MISSING_PERMISSION


def test_error_detail_formatting() -> None:
    from conftest import forbidden

    from subtlescan.collectors.azure.context import classify_azure_error

    assert classify_azure_error(forbidden())[1].startswith("HTTP 403: The client")
    reason, detail = classify_azure_error(GraphError(403, "Authorization_RequestDenied", "Insufficient privileges"))
    assert (reason, detail) == (GapReason.MISSING_PERMISSION, "Authorization_RequestDenied: Insufficient privileges")

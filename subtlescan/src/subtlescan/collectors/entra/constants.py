"""Well-known Entra identifiers and privilege lists shared by collectors and checks."""

from __future__ import annotations

GRAPH_APP_ID = "00000003-0000-0000-c000-000000000000"
GLOBAL_ADMIN_TEMPLATE = "62e90394-69f5-4237-9190-012177145e10"

# Used when Graph does not report `isPrivileged` on a role definition.
PRIVILEGED_ROLE_TEMPLATES = {
    GLOBAL_ADMIN_TEMPLATE,  # Global Administrator
    "e8611ab8-c189-46e8-94e1-60213ab1f814",  # Privileged Role Administrator
    "7be44c8a-adaf-4e2a-84d6-ab2649e08a13",  # Privileged Authentication Administrator
    "194ae4cb-b126-40b2-bd5b-6091b380977d",  # Security Administrator
    "b1be1c3e-b65d-4f19-8427-f6fa0d97feb9",  # Conditional Access Administrator
    "fe930be7-5e62-47db-91af-98c3a49a38b1",  # User Administrator
    "29232cdf-9323-42fd-ade2-1d097af3e4de",  # Exchange Administrator
    "f28a1f50-f6e7-4571-818b-6a12f2af6b6c",  # SharePoint Administrator
    "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3",  # Application Administrator
    "158c047a-c907-4556-b7ef-446551a6b5f7",  # Cloud Application Administrator
}

# Tenants that own Microsoft first-party service principals.
MICROSOFT_TENANTS = {"f8cdef31-a31e-4b4a-93e4-5f571e91255a", "72f988bf-86f1-41af-91ab-2d7cd011db47"}

# Graph application permissions that amount to tenant takeover or bulk data access.
HIGH_PRIVILEGE_GRAPH_PERMISSIONS = {
    "RoleManagement.ReadWrite.Directory",
    "AppRoleAssignment.ReadWrite.All",
    "Application.ReadWrite.All",
    "Application.ReadWrite.OwnedBy",
    "Directory.ReadWrite.All",
    "User.ReadWrite.All",
    "Group.ReadWrite.All",
    "GroupMember.ReadWrite.All",
    "Policy.ReadWrite.ConditionalAccess",
    "UserAuthenticationMethod.ReadWrite.All",
    "Mail.Read",
    "Mail.ReadWrite",
    "Mail.Send",
    "MailboxSettings.ReadWrite",
    "Files.Read.All",
    "Files.ReadWrite.All",
    "Sites.Read.All",
    "Sites.ReadWrite.All",
    "Sites.FullControl.All",
}

# Premium-license errors mean "feature not available in this tenant", not "we lack permission".
PREMIUM_ERROR_MARKERS = ("NonPremiumTenant", "RequestFromNonPremium", "AadPremiumLicenseRequired")

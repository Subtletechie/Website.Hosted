#!/usr/bin/env bash
# Creates a read-only app registration for a subtlescan assessment.
# Run by the CLIENT's admin in Azure Cloud Shell (Bash) or a signed-in `az` session.
#
#   Azure RBAC:   Reader + Security Reader on each subscription in scope
#   Microsoft Graph application permissions (read-only, admin consent required):
#     Directory.Read.All, Policy.Read.All, AuditLog.Read.All, Application.Read.All,
#     RoleManagement.Read.Directory, UserAuthenticationMethod.Read.All
#
# Nothing here can change resources. Delete the app registration after the engagement:
#   az ad app delete --id <appId>
set -euo pipefail

APP_NAME="${APP_NAME:-subtlescan-assessment-readonly}"
SECRET_DAYS="${SECRET_DAYS:-30}"
GRAPH_API="00000003-0000-0000-c000-000000000000"
GRAPH_PERMS=(Directory.Read.All Policy.Read.All AuditLog.Read.All Application.Read.All
             RoleManagement.Read.Directory UserAuthenticationMethod.Read.All)

TENANT_ID="$(az account show --query tenantId -o tsv)"
if [[ $# -gt 0 ]]; then
  SUBSCRIPTIONS=("$@")
else
  mapfile -t SUBSCRIPTIONS < <(az account list --query "[?state=='Enabled'].id" -o tsv)
fi
echo "Tenant: $TENANT_ID"
echo "Subscriptions in scope: ${SUBSCRIPTIONS[*]}"
read -r -p "Create read-only app '$APP_NAME'? [y/N] " ok
[[ "$ok" =~ ^[Yy]$ ]] || exit 1

APP_ID="$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)"
az ad sp create --id "$APP_ID" >/dev/null

for perm in "${GRAPH_PERMS[@]}"; do
  # Look up role ids at run time instead of hardcoding GUIDs.
  role_id="$(az ad sp show --id "$GRAPH_API" --query "appRoles[?value=='$perm'].id | [0]" -o tsv)"
  az ad app permission add --id "$APP_ID" --api "$GRAPH_API" --api-permissions "$role_id=Role" >/dev/null
done
echo "Granting admin consent for Graph read permissions..."
az ad app permission admin-consent --id "$APP_ID"

for sub in "${SUBSCRIPTIONS[@]}"; do
  for role in "Reader" "Security Reader"; do
    az role assignment create --assignee "$APP_ID" --role "$role" --scope "/subscriptions/$sub" >/dev/null
  done
  echo "Assigned Reader + Security Reader on $sub"
done

END_DATE="$(date -u -d "+${SECRET_DAYS} days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+"${SECRET_DAYS}"d +%Y-%m-%dT%H:%M:%SZ)"
SECRET="$(az ad app credential reset --id "$APP_ID" --end-date "$END_DATE" --query password -o tsv)"

cat <<OUT

Done. Send these to your assessor over a secure channel (not email in plain text):
  AZURE_TENANT_ID=$TENANT_ID
  AZURE_CLIENT_ID=$APP_ID
  AZURE_CLIENT_SECRET=$SECRET      # expires $END_DATE
Remove access after the engagement:  az ad app delete --id $APP_ID
OUT

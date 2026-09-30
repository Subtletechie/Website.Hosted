# subtlescan

Read-only, point-in-time security assessment of a small/medium business's Azure (and later AWS)
environment. Produces a client-ready Markdown report and a dashboard you can screen-share or send as
one offline HTML file. Powers the Subtletech Cloud Security Assessment engagement.

## Hard rules

1. **Read-only.** Collectors only call list/get/describe. `tests/test_readonly.py` fails the build if a
   write-verb call appears anywhere under `collectors/`.
2. **No secret values stored.** Secret findings record resource, setting name, and a redacted hint only.
3. **Local only.** Everything lives in `./runs/<client>/<timestamp>/`. No telemetry. The dashboard has a
   CSP of `default-src 'none'`, so it cannot make network requests.
4. **Complete findings.** Every check has curated text in `library/*.yaml` and at least one mapping in
   `frameworks/*.yaml` (enforced by `tests/test_catalog.py`).
5. **Degrade gracefully.** Missing permissions become coverage gaps in the report, never crashes.

## Quick start

```bash
uv sync
uv run subtlescan demo                          # fake run for "Northwind Dental Group"
uv run subtlescan ui --run runs/northwind-dental-group/<timestamp>
uv run subtlescan export --run runs/northwind-dental-group/<timestamp>
```

Real Azure scan (client runs `onboarding/azure_reader.sh` first and sends you the three values):

```bash
export AZURE_TENANT_ID=... AZURE_CLIENT_ID=... AZURE_CLIENT_SECRET=...
uv run subtlescan connect-check --provider azure --tenant $AZURE_TENANT_ID
uv run subtlescan scan --provider azure --client acme --tenant $AZURE_TENANT_ID
uv run subtlescan report --run runs/acme/<timestamp> --framework soc2
```

Without a service principal in the environment, `--tenant` uses your `az login` session.

## Commands

| Command | What it does |
|---|---|
| `connect-check` | Verifies credentials, lists visible subscriptions and coverage gaps. Writes nothing. |
| `scan` | collect → inventory → checks → scoring → `report.md` in a new run folder |
| `analyze --run` | Re-runs checks + scoring on an existing `inventory.json` (no cloud calls) |
| `report --run [--framework]` | Re-renders the Markdown report. Frameworks: `soc2`, `cis_azure`, `nist_csf`, `iso27001`, `hipaa` |
| `ui --run [--port]` | Dashboard on `127.0.0.1` only. Re-reads the run folder on each refresh. |
| `export --run [--out]` | One self-contained HTML file (inline CSS/JS/data) to send the client |
| `demo` | Writes a previous + current fake run (~30 findings) for demos and UI work |

## Run folder

```
runs/<client>/<timestamp>/
  run.json  inventory.json  coverage.json  findings.json  report.md  log.jsonl
  overrides.yaml   # you edit this; UI, export, and report respect it
```

`overrides.yaml`:

```yaml
AZ-STG-001-3f9c0a1b2d:
  status: accepted_risk          # open | accepted_risk | false_positive
  analyst_note: Public site assets only; client accepts.
```

Finding ids are stable across rescans (`<check_id>-<hash of resource id>`), so overrides and the
"vs previous run" delta keep working.

## Scoring

`score = base × exposure (1.5) × blast_radius (1.5) × data_sensitivity (1.3)` with base
Critical 10 / High 7 / Medium 4 / Low 1.5. Bands: ≥12 Critical, ≥6.5 High, ≥3.5 Medium. One factor
alone does not jump a band; two do. Context only raises severity. Sensitivity matches
`customer|pii|finance|backup|prod` in name, resource group, or tags.

Grade: `100 × exp(−Σ open scores / 120)` → A ≥90, B ≥80, C ≥70, D ≥60, else F. Any open Critical
caps the grade at C. Accepted-risk and false-positive findings don't count.

## Checks

| ID | Severity | What it flags |
|---|---|---|
| ENTRA-ID-001 | Critical | Security defaults off and no enforced Conditional Access policy |
| ENTRA-ID-002 | High | CA exists but nothing blocks legacy authentication for all users/apps |
| ENTRA-ID-003 | High | Enabled member accounts with no MFA method registered (one finding, list in evidence) |
| ENTRA-ID-004 | High | More than 4 permanent Global Administrators (PIM time-bound activations excluded) |
| ENTRA-ID-005 | Medium | No cloud-only (`*.onmicrosoft.com`) Global Admin excluded from all enforced CA policies |
| ENTRA-ID-006 | Medium | Users can consent to any app (`microsoft-user-default-legacy`) |
| ENTRA-ID-007 | Low | Anyone, including guests, can invite guests |
| ENTRA-ID-008 | Critical | Admin account with no MFA method registered (one finding per admin) |
| ENTRA-APP-001 | Medium | App registration client secret valid for more than 365 days |
| ENTRA-APP-002 | High | Non-Microsoft app granted high-privilege Graph application permissions |
| AZ-IAM-001 | High | Service principal with Owner / User Access Administrator at subscription scope or above |
| AZ-STG-001 | High | Storage account allows anonymous blob access |
| AZ-STG-002 | Medium | Storage account allows shared key (account key) access |
| AZ-STG-003 | Medium | Blob soft delete off or under 7 days |

Licence-aware: without Entra ID P1, Conditional Access and the MFA registration report are unavailable.
That is recorded as an "Unsupported service" coverage gap (not a permission problem), CA is treated
as "none exist", and MFA checks are skipped rather than guessed. Without P2 (PIM), every active role
assignment counts as permanent. When a setting can't be read, checks stay silent instead of assuming
the worst; the coverage page says what wasn't assessed.

Graph is read through a ~60-line GET-only client (`collectors/entra/graph.py`) on azure-core rather
than `msgraph-sdk`: the SDK is async-only, pulls in the Kiota stack, and its generated models make
recorded-JSON fixtures awkward. `tests/test_readonly.py` checks that client can only send GET.

## Adding a check

1. Function in `checks/<provider>/<domain>.py`, decorated with `@check(id=..., provider=..., severity=..., domain=...)`.
   Pure: `Inventory` in, `list[Hit]` out, under 40 lines, no client-facing text.
2. Entry in `library/*.yaml` (title, business_impact, remediation, terraform_fix, effort S/M/L).
3. Mappings in `frameworks/*.yaml`.
4. Pass and fail tests in `tests/checks/`.

## Development

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run mypy            # --strict on models/ and scoring/
```

## Status

Build steps 1–3 are done: models, registry, Azure storage + RBAC collectors, Entra collectors
(tenant settings, Conditional Access, users + MFA registration, directory roles, app registrations,
service principals), 14 checks, Markdown report, and the dashboard (Overview + Findings) with static
export and demo data. Next up: remaining Azure collectors (network, compute, Key Vault, SQL, web),
then backup/recovery, secrets, and logging (step 4).

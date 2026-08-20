## Governance/dashboard production-readiness layer

PE Core now supports a generic plugin governance surface. When hardening plugin production readiness, check and extend these surfaces before building one-off plugin-specific UI:

- `plugin_governance_summary()` in `prismatic/plugin_architecture.py` computes `readiness_state`, `risk_level`, `permissions`, `approval_gates`, `policy_checks`, `credential_redaction`, `surface_coverage`, and `production_blockers`.
- `/api/plugins/governance` in `prismatic/gateway/server.py` exposes operator-facing readiness/risk/approval/blocker data.
- The Dashboard **Plugins** tab renders generic governance cards, approval gates, API/MCP/artifact coverage, risk labels, and blockers/warnings.
- `/api/pwp/status` should expose catalog-derived governance for PWP (`catalog_governance`, `approval_gates`, `policy_checks`, `surface_coverage`, `artifact_types`) so PWP remains the reference plugin.
- Future media/Asset Forge blueprints should declare `risk_level`, `permissions`, `approval_gates`, `policy_checks`, `provenance_required`, `audit_events`, and `job_lifecycle`.
- Raw token-like manifest values must be treated as blockers; manifests should store env var names only.

## Durable plugin jobs/audit trail

Gap 1 is now implemented in PE Core:

- `prismatic/plugin_jobs.py` persists `plugin_jobs`, `plugin_job_events`, and lightweight `plugin_artifacts` references.
- Default store path is `$PRISMATIC_PLUGIN_JOBS_STATE`, falling back to `$PRISMATIC_STATE_DIR/plugin_jobs.json`, then `./prismatic_state/plugin_jobs.json`.
- Gateway endpoints:
  - `GET /api/plugins/jobs`
  - `POST /api/plugins/jobs`
  - `GET /api/plugins/jobs/{job_id}`
  - `POST /api/plugins/jobs/{job_id}/approve`
  - `POST /api/plugins/jobs/{job_id}/reject`
  - `POST /api/plugins/jobs/{job_id}/events`
  - `POST /api/plugins/jobs/{job_id}/status`
- `/api/plugins/governance` includes a `jobs` summary.
- `GET /api/plugins/audit-events` lists the normalized cross-plugin audit stream from job events plus artifact lifecycle/export history. It supports `plugin_name`, `job_id`, `artifact_id`, `event_type`, and `limit` filters.
- Dashboard **Plugins** tab includes `plugin-job-summary`, `plugin-jobs-table`, `plugin-audit-events`, `renderPluginJobs()`, and `renderPluginAuditEvents()`.
- Job lifecycle now includes durable `queued`, `running`, `needs_approval`, `completed`, `failed`, `cancelled`, and `rejected` states.
- Audit events include `job_created`, `policy_checked`, `approval_required`, `approved`, `rejected`, `started`, `artifact_emitted`, `completed`, `failed`, `cancelled`, and `note_added`.

- `artifact_emitted` creates lightweight artifact references only; the fuller universal artifact/provenance registry is the next gap.

## Universal artifact/provenance registry

Gap 2 is now implemented in PE Core:

- `prismatic/plugin_artifacts.py` persists full universal artifact/provenance records.
- Default store path is `$PRISMATIC_PLUGIN_ARTIFACTS_STATE`, falling back to `$PRISMATIC_STATE_DIR/plugin_artifacts.json`, then `./prismatic_state/plugin_artifacts.json`.
- Artifact records include `artifact_id`, `asset_id`, `plugin_name`, `job_id`, `artifact_type`, `mime_type`, `path_or_url`, `sha256`, `size_bytes`, `metadata`, `provenance`, `input_summary`, `provider_or_service`, `approval_state`, `publish_state`, `export_history`, and timestamps.
- Local hashing only reads paths under the repo, configured PE state dir, or `/tmp`; external URLs are stored as references and not fetched.
- Token-like metadata/provenance/input summaries are redacted.
- Gateway endpoints:
  - `GET /api/plugins/artifacts`
  - `POST /api/plugins/artifacts`
  - `GET /api/plugins/artifacts/{artifact_id}`
  - `POST /api/plugins/artifacts/{artifact_id}/approve`
  - `POST /api/plugins/artifacts/{artifact_id}/reject`
  - `POST /api/plugins/artifacts/{artifact_id}/publish-ready`
- Gap 1 integration: `artifact_emitted` on a plugin job creates/links a full universal artifact record, and job detail hydrates artifacts from the universal store.
- `/api/plugins/governance` includes an `artifacts` summary.
- Dashboard **Plugins** tab includes `plugin-artifact-summary`, `plugin-artifacts-table`, and `renderPluginArtifacts()`.

## Plugin policy/approval enforcement

Gap 3 is now implemented in PE Core:

- `prismatic/plugin_policy.py` owns stable machine-readable policy decisions.
- Decision values are `allow`, `needs_approval`, and `block`.
- Decision payloads include `allowed`, `requires_approval`, `decision`, `reason`, `risk_level`, `blockers`, `warnings`, `approval_reasons`, `checks`, `context`, and `evaluated_at`.
- Gateway endpoints:

  - `POST /api/plugins/policy/preview`
  - `POST /api/plugins/jobs/{job_id}/start`
  - `POST /api/plugins/artifacts/{artifact_id}/export`
- Direct `POST /api/plugins/jobs/{job_id}/status` transitions to `running` call the same job-start policy gate.
- Job start attempts append durable audit events: `policy_checked`, `start_allowed`/`start_blocked`, `approval_required` when applicable, and `started` when allowed.
- Artifact `publish-ready` and `export` enforce approval/provenance/rejection policy and append export-history entries with `allowed` and `policy_result`.
- Conservative defaults require approval for publish/export/deploy/delete/destroy/write/overwrite/batch/costly/external-service/credentialed/production/public actions.
- Dashboard **Plugins** tab includes `plugin-policy-summary`, `plugin-policy-decision`, and `renderPluginPolicy()` with `blocked_reason` markers.
- Hermes profile note: pytest may need `PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages:$PYTHONPATH` because this profile maps Python user-site to the profile-local home while pytest is installed in `/home/ubuntu/.local`.

## Public security readiness pass

When Prismatic Engine is being prepared for public repo/external-user sharing, run a dedicated security posture pass in addition to onboarding docs. Current public security readiness surface includes:

- `scripts/public_security_readiness_audit.py` — local credential-free audit command; expected marker is `PUBLIC_SECURITY_READINESS_OK`.
- `docs/public-security-readiness.md` — canonical public/external-user security audit doc.
- Gateway CORS defaults are local-only via `_configured_cors_origins()` in `prismatic/gateway/server.py`; remote browser origins must be explicitly set with `PRISMATIC_CORS_ORIGINS`, and wildcard CORS is rejected while credentials are enabled.
- `.env.example` includes safe local defaults and `PRISMATIC_CORS_ORIGINS=http://127.0.0.1:9000,http://localhost:9000`; do not include credential assignment placeholders that tooling may redact/mangle.
- Tests live in `tests/test_public_security_readiness.py` and cover audit pass, CORS defaults/wildcard rejection, redaction behavior, and artifact path traversal assumptions.

Security checklist to cover explicitly:

1. secret scanning
2. env var examples
3. redaction tests
4. API auth expectations
5. dashboard exposure review
6. local/remote deployment assumptions
7. CORS review
8. destructive action policy

9. dependency audit
10. artifact path traversal checks
11. plugin sandbox assumptions documented
12. external service credential flow

Avoid committing contiguous high-confidence fake token/private-key fixtures. If tests need detector inputs, build them by string concatenation at runtime so repo scanners do not flag committed fixtures.

## Public launch onboarding/package pass

When Prismatic Engine needs external/public readiness, treat onboarding as a product surface, not just docs cleanup. The public path should be copy-pasteable from a clean checkout and avoid Michael-specific paths, private workspace assumptions, systemd requirements, or real credential material.

Current public onboarding package includes:

- `README.md` as the public front door: quickstart, install, minimal demo, architecture overview, plugin development path, verification commands, license/security links.
- `.env.example` with safe local-only defaults; do not include token-like placeholder fragments or credential variable values if the tooling may redact/mangle them.
- Stable public docs entrypoints: `docs/public-launch.md`, `docs/plugin-developer-quickstart.md`, `docs/security.md`, and `docs/contributing.md`.
- Canonical product-direction docs: `docs/north-star.md` (North Star + plugin ecosystem rubric), `docs/dashboard-primary-touchpoint.md` (Telegram/headless today, dashboard-first target), and `docs/okf-evidence-map.md` (Objective → Key Result → Function → Evidence → Promotion Decision map).
- OKF/North Star positioning should explicitly teach agents: `Claude Code writes work. Hermes runs agents/tools/plugins. Prismatic governs work.` Prismatic is the work-trust layer: agent output is cheap, trustworthy AI work is expensive, and PE exists to turn raw agent/plugin/operator output into packets, artifacts, provenance, policy, approvals, audits, and promotion decisions. See `references/okf-trust-doctrine-2026-07-19.md`.
- Detailed docs: `docs/public-onboarding.md`, `docs/public-architecture.md`, `docs/plugin-developer-guide.md`, `docs/hello-plugin-tutorial.md`, `docs/troubleshooting.md`, `docs/public-security-readiness.md`, `docs/pwp-reference-lifecycle.md`, `docs/phone-first-command-surface.md`, and `docs/dashboard-screenshots.md`.
- `docs/assets/dashboard-plugin-policy-overview.svg` as a credential-free illustrative dashboard asset.
- `CONTRIBUTING.md`, `SECURITY.md`, and `CHANGELOG.md`.
- `scripts/public_launch_smoke.py` as the one-command local smoke; expected marker is `PUBLIC_LAUNCH_SMOKE_OK`.

Public launch smoke should stay local-only and credential-free. It should verify imports, CLI availability, plugin catalog, shipped plugin load gate, Gateway/TestClient APIs, plugin governance/policy basics, dashboard markers, and the stable public docs entrypoints. Avoid `python -m prismatic.cli` unless a `__main__` exists; call the CLI function directly or use installed console scripts after install.

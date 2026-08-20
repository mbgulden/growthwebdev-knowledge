# AGY Autopilot Result Packet + Stale-Guard Pattern

Use this when turning AGY from a one-task canary into a safe, mergeable Prismatic Dashboard work lane.

## First safe slice

Do **not** start with bulk dispatch, auto-merge, or dashboard controls. The first mergeable slice is:

1. Reconfirm baseline:
   - durable runtime checkout is `main...origin/main` and service is active;
   - public `/dashboard`, `/workspace-tree`, `/health`, queue/dispatcher/recovery APIs return expected 200s;
   - no active AGY/bulk/autopilot process is running.
2. Add result packet contract + validator:
   - `docs/agy-result-packet-contract.md`
   - `schemas/agy-result-packet.schema.json`
   - `prismatic/agy_result_packet.py`
   - `tests/test_agy_result_packet.py`
3. Add completed-work ingestion **design stub only** before implementation:
   - `docs/agy-completed-work-ingestion-design.md`
4. Open a PR; do not merge/deploy unless explicitly in scope.

Earned markers for that slice:

```text
AGY_AUTOPILOT_BASELINE_CONFIRMED_OK
AGY_RESULT_PACKET_SCHEMA_OK
AGY_COMPLETED_WORK_INGESTION_DESIGN_READY_OK
```

Do not claim:

```text
overnight_autopilot_ready
auto_merge_enabled
canonical_full_suite_green
production_deployed
AGY_COMPLETED_WORK_INGESTION_OK
```

## Result packet schema requirements

Required packet fields:

```yaml
agent: agy
issue_identifier: GRO-####
branch: <branch>
base_branch: main
changed_files: []
pr_url: <url-or-null>
result_artifacts: []
verification:
  commands: []
  result: PASS|FAIL|BLOCKED
  log_path: <path>
  ad_hoc_or_canonical: ad-hoc targeted|canonical suite
non_claims: []
merge_lane: dashboard-ui|backend-api|docs|research|mixed|manual-review
risk_level: low|medium|high
next_action: merge-ready|needs-fred-cleanup|needs-human-review|blocked|superseded
marker: AGY_TASK_RESULT_PACKET_OK
```

Runtime validator should enforce more than JSON Schema:

- issue ID pattern `GRO-####`;
- base branch allowlist (`main` initially);
- no absolute/traversal/generated/vendor/cache/secret-like changed paths;
- no secret-like values in commands/artifacts/logs;
- merge-ready requires `verification.result=PASS`, at least one artifact, non-high risk, and not mixed/manual-review;
- dashboard-ui merge-ready requires dashboard/browser/JS proof;
- production/runtime/public/deployed claims require explicit proof references.

## CI secret-scanner pitfall

When testing secret detection, **do not commit a literal token-shaped string** such as a full `ghp_...` fixture. The repository security readiness audit will correctly flag it.

Instead, construct the fake token at runtime in the test:

```python
fake_token = "ghp_" + "1234567890abcdef" + "1234567890abcdef" + "1234"
packet["verification"]["commands"] = [f"export TOKEN={fake_token}"]
```

Then run both focused tests and the public security audit before PR closeout:

```bash
python3 -m py_compile prismatic/agy_result_packet.py
python3 -m json.tool schemas/agy-result-packet.schema.json >/tmp/agy-result-packet.schema.formatted.json
python3 -m pytest -q tests/test_agy_result_packet.py
python3 scripts/public_security_readiness_audit.py
```

## Stale-guard pattern for AGY verifier

If a stale guard names exact changed AGY paths, create a fresh temp verifier using `tempfile.mkstemp(prefix='hermes-verify-', dir='/tmp')`, run it, and delete it. The compact output must include:

```text
changed_paths_checked=<exact AGY paths>
canonical_test_lint_build_command=python3 -m py_compile ... && python3 -m json.tool ... && python3 -m pytest ... && python3 scripts/public_security_readiness_audit.py
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=overnight_autopilot_ready,auto_merge_enabled,canonical_full_suite_green,production_deployed
MARKER=AGY_RESULT_PACKET_SCHEMA_OK
cleanup=PASS
```

Also remove stale verifier files named by the guard when they are no longer relevant, especially old dashboard/mobile proof scripts that can keep surfacing as stale context.

## PR body expectations

Include:

- phases completed;
- gates earned;
- files changed;
- compact verification block;
- explicit non-claims;
- next exact slice.

For the first slice, the next exact slice should be Phase 2 implementation: durable completed-work store + ingest CLI + `GET/POST /api/agy/completed-work` + honest dashboard table/empty state.
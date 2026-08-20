# AGY completed-work integration gate

Use this reference after AGY single-task proof / result-packet work exists and the next gap is turning completed AGY outputs into safe, reviewable dashboard/API state **without auto-merging**.

Marker:

```text
AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
```

## Scope boundary

This is a bounded contract/API/dashboard-state slice only:

- do not bulk-dispatch AGY;
- do not auto-merge completed AGY branches;
- do not replace the durable dashboard shell;
- do not claim production deploy or canonical full-suite green unless actually done;
- expose status for Fred/Linear/dashboard review, not mutation.

## Recommended branch

```bash
cd /home/ubuntu/work/prismatic-engine
git fetch origin --quiet
git switch -C feature/fred-agy-completed-work-integration-gate origin/main
```

Lock only the files you intend to touch, typically:

```text
prismatic/completed_work_gate.py
tests/test_completed_work_gate.py
prismatic/gateway/server.py
prismatic/gateway/templates/dashboard.html
```

## Contract implementation pattern

Create `prismatic/completed_work_gate.py` as a pure module with dataclasses / enums and no git or Linear side effects.

Minimum packet:

```json
{
  "agent": "agy",
  "source_branch": "feature/...",
  "source_path": "/home/ubuntu/...",
  "base_branch": "origin/main",
  "changed_files": [],
  "result_summary": "...",
  "proof": {
    "command": "...",
    "result": "PASS|FAIL|BLOCKED",
    "log": "/tmp/...",
    "scope": "...",
    "ad_hoc_or_canonical": "ad-hoc targeted|canonical suite",
    "not_claiming": "...",
    "marker": "..."
  },
  "lane_scope": {
    "allowed_paths": [],
    "touched_paths": []
  }
}
```

Use this exact classification vocabulary unless Michael explicitly changes it:

```text
merge_ready
clean_rebuild_required
blocked_missing_proof
blocked_failed_verification
manual_review_scope
manual_review_conflict
superseded
rejected
```

Important classification ordering:

1. Missing `proof` should classify as `blocked_missing_proof`, not generic `rejected`.
2. Missing/invalid `lane_scope` or out-of-scope touched paths should classify as `manual_review_scope`.
3. Dirty/untrusted worktrees should classify as `clean_rebuild_required` before merge review.
4. Stale source relative to base should classify as `superseded`.
5. Conflicts should classify as `manual_review_conflict`.
6. `proof.result == FAIL` should classify as `blocked_failed_verification`; `BLOCKED` or incomplete command/log/scope/marker should classify as `blocked_missing_proof`.
7. `merge_ready` means “eligible candidate for Fred review,” never auto-merge.

For py3.10 CI compatibility, prefer `class GateClassification(str, Enum)` over `StrEnum`.

## API surface

Keep endpoints read-only / fixture-only for the first slice:

```text
GET /api/completed-work/gate/schema
GET /api/gateway/completed-work/gate/schema
GET /api/completed-work/gate/demo
GET /api/gateway/completed-work/gate/demo
```

The demo endpoint should classify a safe fixture packet and must not read external AGY state, mutate git, write Linear, dispatch agents, or merge branches.

## Dashboard exposure

Add a compact card to the existing dashboard shell only. Preserve existing dashboard and Resources markers such as:

```text
workspace-tree-mobile-responsive
dashboard-tabs-mobile-wrap
dashboard-header-mobile-wrap
resources-budget-caps-controls
```

Add a new proof marker:

```html
data-proof-marker="agy-completed-work-gate-card"
```

The card should fetch via the public gateway convention:

```javascript
fetch(`${API_PREFIX}/completed-work/gate/demo`)
```

Copy should say this is a contract gate before Fred merge review and explicitly avoid implying auto-merge.

## Tests

Add focused tests for:

- merge-ready packet;
- missing proof → `blocked_missing_proof`;
- failed verification → `blocked_failed_verification`;
- lane/scope mismatch → `manual_review_scope`;
- dirty/untrusted source → `clean_rebuild_required`;
- stale/superseded source → `superseded`;
- conflicts → `manual_review_conflict`;
- untrusted/invalid agent → `rejected`;
- schema/demo payloads are machine-readable.

Also run adjacent regression tests that protect recently merged runway work, especially `tests/test_budget_caps.py`. If `tests/test_dashboard_ux_hardening.py` exists in the checkout, run it too; if it is absent, say `dashboard_ux_hardening=not_present` rather than pretending it ran.

## Verification packet

Use a focused `/tmp/hermes-verify-*` script and clean it up. The compact proof should include the exact changed paths, marker, non-claims, local API proof, and dashboard JS check if HTML changed.

Minimum command bundle:

```text
python3 -m py_compile prismatic/completed_work_gate.py prismatic/gateway/server.py
python3 -m pytest -q tests/test_completed_work_gate.py
python3 -m pytest -q tests/test_budget_caps.py
python3 -c 'from prismatic.completed_work_gate import classify_completed_work; print(classify_completed_work)'
node --check /tmp/hermes-dashboard-inline-completed-work-gate.js
```

For local FastAPI proof, use the project’s stable gateway venv when plain `python3` lacks gateway dependencies:

```text
/home/ubuntu/.prismatic/venv_stable/bin/python3 -m prismatic.gateway.server --host 127.0.0.1 --port <temp-port>
```

Probe:

```text
GET /api/gateway/completed-work/gate/schema -> 200, marker present
GET /api/gateway/completed-work/gate/demo -> 200, fixture classification merge_ready
GET /api/completed-work/gate/demo -> 200, local alias matches gateway payload
```

Compact final shape:

```text
COMMAND=<grouped command summary>
RESULT=PASS
LOG=/tmp/fred-agy-completed-work-gate-verify.log
SCOPE=AGY completed-work contract/API/dashboard fixture status gate
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=auto_merge,bulk_agy_dispatch,production_deploy,canonical_full_suite_green
MARKER=AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
cleanup=PASS
```

## Stale-guard pitfalls

If the stale guard keeps reporting the old mobile overflow proof (`/tmp/hermes-verify-mobile-branch-390.py`) while the current changed paths are the AGY gate files:

1. remove the exact stale temp files named by the guard;
2. create a **new** tempfile-generated `/tmp/hermes-verify-*` script;
3. include the guard’s exact changed paths in `changed_paths_checked`, including the stale `/tmp/hermes-verify-agy-completed-work-gate.py` path;
4. assert both stale temp paths are absent;
5. clean the fresh verifier before reporting `cleanup=PASS`.

Do not rerun or report the old mobile overflow measurement for this slice; it is stale evidence for a different dashboard repair.
# Dashboard Real Integration Restoration Pattern

Use this when the Prismatic governance dashboard has stopped 404ing but Michael says tabs are still not actually connected, empty, or missing Kai-built work.

## Core lesson

A `200` route is not enough. A dashboard pane is only stable when its backend returns the real data contract the UI renders. Compatibility shims are acceptable as a short stopgap to remove 404s, but the next pass must replace `gateway-compat`, `dashboard-compat`, `empty-fallback`, and fake/no-op surfaces with the real adapter or persisted ledger where one exists.

## Worked restoration map

In the July 2026 stabilization pass, the following real data-backed sources were restored:

| Surface | Real source / adapter | Evidence shape |
|---|---|---|
| PWP tab | `plugins/pwp`, `scripts/pwp`, `prismatic.pwp_integration` | `/api/pwp/status` returns `connected: true`, capabilities/tools/lifecycle history |
| GCP Quotas tab | legacy persisted ledger `~/.prismatic/quota_state.db` | dashboard contract `current[]`, `recent_events[]`, `snapshot_at`, `snapshot_age_sec` |
| Merge Pipeline | `prismatic/merge_status.py` from design/Kai branch | reads `~/.prismatic/merge-pipeline/state_v6.json`; returns `merge_state+governance_triage+merge_control_state` |
| Foundation | `prismatic/foundation_status.py` | returns `run_records+foundation_control_state`, not `gateway-compat` zeros |
| Dispatcher | `prismatic/ingestion_status.py` | returns `dashboard_dispatcher_state+run_records` |
| Recovery | `prismatic/ingestion_status.py` | returns `dashboard_recovery_controls+run_records` with full failure taxonomy |
| Webhook stats | `prismatic/ingestion_status.py` | returns `gateway_counters+run_records` |
| Queue | SQLite EventBus | `/api/webhooks/queue` returns `source: sqlite` with actual items |

## Diagnostic sequence

1. Extract the tab's exact frontend contract from `prismatic/gateway/templates/dashboard.html`, not just the route path. Example: the quotas UI expected `current`, `recent_events`, `snapshot_at`, and `snapshot_age_sec`; returning only `quota_records` made the route 200 but visually empty.
2. Probe the route and summarize both HTTP status and payload shape.
3. Search branch/history for Kai/design adapters and persisted state files before inventing a shim. Useful candidates:
   - `design/gro-2880:prismatic/merge_status.py`
   - `design/gro-2880:prismatic/foundation_status.py`
   - `design/gro-2880:prismatic/ingestion_status.py`
   - `~/.prismatic/merge-pipeline/state_v6.json`
   - `~/.prismatic/quota_state.db`
4. Restore class-level adapters onto `deploy-fresh` via a clean `feature/` branch, preserving governance hooks.
5. Keep browser controls audit-safe: they may persist operator intent and publish events, but must not run shell/service-manager/agent commands directly from browser routes.
6. Restart the gateway after merge and verify both API payloads and browser tab rendering.

## Verification pattern

A focused `/tmp/hermes-verify-*` verifier should check:

- repo on `deploy-fresh`, head matches `origin/deploy-fresh`, worktree clean;
- changed Python files compile;
- stale temp files absent;
- live tab routes return 200;
- each restored surface reports the real source, not a compatibility fallback:
  - Merge: `merge_state+governance_triage+merge_control_state`
  - Foundation: `run_records+foundation_control_state`
  - Dispatcher: `dashboard_dispatcher_state+run_records`
  - Recovery: `dashboard_recovery_controls+run_records`
  - Webhook Stats: `gateway_counters+run_records`
  - Queue: `sqlite`
  - Quota: `quota_state.db`
  - PWP: `connected`
- PWP targeted tests still pass;
- Fred locks are released.

Use browser proof after API proof: click every tab and inspect console. A clean API route matrix can still hide frontend schema mismatches.

## Pitfalls

- Do not call a tab fixed just because the error changed from 404 to empty state.
- Do not leave `accepted_noop`/compatibility routes as final integrations when a real adapter or ledger exists.
- Do not assume the current branch has Kai's work; compare `deploy-fresh`, `main`, local branches, and `design/*` / `kai/*` refs.
- Do not clean untracked plugin assets until checking whether they are stranded Kai work.
- Do not overwrite browser controls with real shell actions; persist auditable intent instead.

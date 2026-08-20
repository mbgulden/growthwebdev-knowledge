# Governance Dashboard Full-Tab Restoration + Regression Contract

Use this reference when the Prismatic governance dashboard looks partially connected but Michael says most tabs still feel fake, simulated, or disconnected.

## Core lesson

Do not stop at route 200s, no 404s, or a single tab working. The failure mode is often layered:

1. Backend routes exist but return compatibility/fallback payloads.
2. Frontend tabs still render `mock*` arrays or old static strings.
3. Kai/Ned real adapters exist in design/work branches but never landed on `deploy-fresh`.
4. Plugin bundles exist in `plugins/` but are not mounted by the protected gateway.
5. Verification temp files confuse the stale-edit guard unless the verifier is created, run, and removed in one operation.

## Top-down workflow

Start at `/dashboard` and work through each visible tab in order:

```text
Dashboard → Ingestion Queue → Merge Pipeline → Foundation → Workspaces → Skills → Signals → Native Crons → PWP Plugin → Plugins → GCP Quotas → Workspace Tree
```

For every tab, verify all three layers:

```text
frontend render contract
+ backend route/payload contract
+ real source/adaptor/ledger exists
```

Treat these as blockers, not acceptable end states, when a real source exists:

```text
gateway-compat
dashboard-compat
empty-fallback
accepted_noop
mockSkills
mockSignals
const mock*
old fake task strings such as Completed UI mockup / GRO-671 / Watcher backup
```

## Worked restoration map

The successful baseline used these live sources:

| Surface | Live source / route |
|---|---|
| Main Dashboard agents | `/api/gateway/agents/status` → `run_records+agent_registry+queue_state+timeline+health_context` |
| Main Dashboard activity | `/api/gateway/timeline` / `/events/recent` |
| Ingestion Queue | `/api/webhooks/queue` → SQLite EventBus |
| Merge Pipeline | `/api/gateway/merge/status` → `merge_state+governance_triage+merge_control_state` |
| Foundation | `/api/foundation/peer_review` → `run_records+foundation_control_state` |
| Dispatcher | `/api/dispatcher/status` → `dashboard_dispatcher_state+run_records` |
| Recovery | `/api/recovery/status` → `dashboard_recovery_controls+run_records` |
| Skills | `/api/skills` → `prismatic.skills` |
| Signals | `/api/gateway/timeline?limit=80` → `prismatic.timeline` |
| Native Crons | `/native-crons?include_deleted=false` |
| PWP Plugin | `/api/pwp/status` connected state |
| Plugins | `/api/plugins/governance` |
| Quotas | `/api/quota` → `quota_state.db` bridge, `current[]` + `recent_events[]` contract |
| Workspace Tree | `/workspace-tree` + `/api/plugins/hermes-plugin-workspace-tree-navigator/tree` |

## Workspace Tree plugin mounting

If `/workspace-tree` is 404 but the plugin exists, do not rebuild a file browser. Mount the existing plugin:

```text
plugins/hermes-plugin-workspace-tree-navigator/dashboard/plugin_api.py
plugins/hermes-plugin-workspace-tree-navigator/dashboard/dist/index.js
```

Expose:

```text
/workspace-tree
/workspace-tree/index.js
/api/plugins/hermes-plugin-workspace-tree-navigator/health
/api/plugins/hermes-plugin-workspace-tree-navigator/tree
```

The bundle expects React hooks. The host shell must provide real React/ReactDOM, not a tiny fake `createElement` shim.

## Durable regression contract

After restoring the tabs, add or run a durable contract like:

```bash
/home/ubuntu/.prismatic/venv_stable/bin/python3 scripts/verify-governance-dashboard-contract.py
```

The contract should fail if mocks or compatibility-only surfaces return. It should verify:

- changed files exist and Python compiles;
- inline dashboard JS passes `node --check`;
- forbidden mock/static strings are absent;
- required live fetches are present;
- every dashboard route returns 200;
- each key route reports the expected real `source`;
- PWP is connected, quotas are populated, crons/plugins/skills/workspace-tree are populated.

## Stale guard wrapper pitfall

When responding to the system stale-verification guard, create a temporary `/tmp/hermes-verify-*` wrapper that:

1. removes stale temp PR/verifier files first;
2. verifies `deploy-fresh` is synced to `origin/deploy-fresh`;
3. runs the durable dashboard contract;
4. checks only **Fred/dashboard locks**, not unrelated Ned/Kai locks;
5. verifies stale temp paths are absent;
6. removes its own verifier before exiting.

Do not fail the wrapper just because unrelated locks exist. Report unrelated locks plainly and leave them untouched.

## Reporting language

Michael’s correction here was workflow-level: “the goal is not done until all Kai/Ned work tree and changes are wired up and stable.” Report by tab/surface, with real source evidence, and explicitly distinguish:

```text
ad-hoc targeted verification + durable dashboard regression-contract pass
not full suite green
```

# Dashboard durable tab integration + mobile Workspace Tree viewer

Use this reference when the canonical Prismatic Hub Dashboard is reachable, but Michael says tabs still feel fake/sample/broken or the Workspace Tree is technically present but not usable on mobile.

## User-corrected goal

Do not create another dashboard shell. Preserve `prismatic/gateway/templates/dashboard.html` and reconnect/port previously good Fred dashboard adapters into the durable production dashboard.

Expected durable markers for this class of closeout:

```text
DASHBOARD_DURABLE_TAB_INTEGRATION_OK
DASHBOARD_WORKSPACE_TREE_MOBILE_OK
```

If the scope is too large to fix in one pass, stop after a precise branch/tab audit and use:

```text
DASHBOARD_DURABLE_TAB_INTEGRATION_AUDIT_OK
```

## Branch comparison is mandatory

Before editing, compare current durable `origin/main` and runtime checkout against prior Fred dashboard branches/PRs. At minimum inspect nearest available refs for:

```text
feature/fred-dashboard-missing-integration-404s
feature/fred-dashboard-lock-shape-compat
feature/fred-connect-pwp-quota-tabs
feature/fred-real-dashboard-adapters
feature/fred-real-ingestion-recovery-adapters
feature/fred-real-dashboard-tab
feature/fred-wire-remaining-dashboard-tabs
feature/fred-dashboard-regression-contract
feature/fred-governance-control-plane-ux
feature/fred-ingestion-attention-deeplink
feature/fred-ingestion-queue-operator-semantics
feature/fred-ingestion-queue-real-contract
feature/fred-dashboard-workspace-tree-main
origin/main
/home/ubuntu/.prismatic/runtime/prismatic-engine
```

Good implementation work in the July 2026 repair was concentrated in `feature/fred-dashboard-regression-contract` and nearby live-tab branches, but those branches were too broad to wholesale merge. Port class-level adapters and specific JS sections; do not cherry-pick unrelated deletions or old repo-wide changes.

## Durable adapter map restored from prior branches

When live `main` has the canonical dashboard shell but still shows mocks, restore/verify these adapter classes and routes rather than writing a new mini-dashboard:

| Surface | Durable adapter/source | Public dashboard route |
|---|---|---|
| Main agents | `prismatic.agent_status.build_agent_status` | `/api/gateway/agents/status` |
| Agent detail | `prismatic.agent_status.build_agent_detail` | `/api/gateway/agents/{agent_id}` |
| Activity / Signals | `prismatic.timeline.list_timeline` | `/api/gateway/timeline` |
| Webhook stats | `prismatic.ingestion_status.webhook_stats_payload` | `/api/gateway/webhooks/stats` |
| Queue | `prismatic.ingestion_status.queue_payload` | `/api/gateway/webhooks/queue` |
| Dispatcher | `prismatic.ingestion_status.dispatcher_status_payload` | `/api/gateway/dispatcher/status` |
| Recovery | `prismatic.ingestion_status.recovery_status_payload` | `/api/gateway/recovery/status` |
| Foundation | `prismatic.foundation_status.foundation_peer_review_payload` | `/api/gateway/foundation/peer_review` |
| Merge | `prismatic.merge_status.merge_status_payload` | `/api/gateway/merge/status` |
| Skills | `prismatic.skills` | `/api/gateway/skills` |
| Quota | persisted quota ledger / bridge | `/api/gateway/quota` |
| Workspace Tree | existing workspace-tree resolver/APIs | `/api/workspaces`, `/api/workspace-tree/node`, `/api/workspace-tree/preview` |

Important public-routing lesson: local `/api/skills` and `/api/quota` can work while public Cloudflare/nginx exposes only `/api/gateway/...`. Prefer dashboard JS fetches through `API_PREFIX = "/api/gateway"` for tab APIs that must work publicly. Add gateway-prefixed aliases when needed, then verify public routes, not just local.

## Frontend truth contract

The canonical dashboard template should not render these in the live path when real adapters exist:

```text
mockAgents
mockWorkspaces
mockSignals
Completed UI mockup
Watcher daily backup
Creating rebase
```

Replace them with live fetches and honest empty states. In the successful repair:

- dashboard topology and detail drawer used `/api/gateway/agents/status` and `/api/gateway/agents/{id}`;
- dashboard activity and Signals used `/api/gateway/timeline`, falling back to `/events/recent` only as real EventBus evidence;
- Skills used `/api/gateway/skills`;
- Quota used `/api/gateway/quota` and `/api/gateway/quota/poll`;
- browser control routes remained audit-safe and returned explicit `accepted_noop` where a real browser click would otherwise shell out or dispatch work.

## Mobile Workspace Tree viewer pattern

The Workspace Tree belongs inside the Workspaces tab of the canonical dashboard, while standalone `/workspace-tree?file=...` can remain as a legacy/fallback view.

Mobile usability fixes that worked:

- add explicit proof markers such as `data-proof-marker="workspace-tree-mobile-responsive"`, `dashboard-tabs-mobile-wrap`, and `dashboard-header-mobile-wrap` so stale-guard/browser proofs can assert the real responsive fix landed;
- use stacked mobile panels with constrained heights, e.g. tree `min-h-[360px] max-h-[52vh]` and preview `min-h-[420px] max-h-[72vh]`, while preserving desktop `xl:min-h-[640px]`;
- add `min-w-0 max-w-full overflow-hidden` on the grid/panels so nested code/file names cannot widen the body;
- make tree and preview independently scrollable with `overflow-auto overscroll-contain`;
- use smaller mobile text (`text-[11px] sm:text-xs`);
- for the embedded mobile file preview, prefer `whitespace-pre-wrap break-words min-w-0 max-w-full` plus `overflow-auto`; this preserved readability and eliminated body overflow at `390px` in the worked repair. Do not use `whitespace-pre` alone unless a 390px browser proof shows it does not widen the page;
- make Copy/Open controls full-width on mobile and normal width on larger screens;
- wrap the global dashboard tab bar and header/status cluster on mobile. In the worked repair the actual overflow was not the file viewer after the first patch; it came from `min-w-[650px]` / `w-max` tab nav and a non-wrapping header status cluster. Replace those with wrapping, `min-w-0`, and proof markers before blaming Workspaces itself;
- keep `/dashboard?file=<path>` opening directly into the Workspaces tab and previewing the file, so Telegram links land in the useful dashboard surface.

## Verification pattern

Use a focused `/tmp/hermes-verify-*` script and log full output under `/tmp`, not in chat. For stale guards scoped to one exact path, include that exact path in `changed_paths_checked` and make the canonical check line machine-obvious.

Minimum checks:

```text
python3 -m py_compile prismatic/gateway/server.py prismatic/agent_status.py prismatic/merge_status.py prismatic/foundation_status.py prismatic/ingestion_status.py prismatic/timeline.py
node --check /tmp/hermes-dashboard-inline-stale-guard.js
public /dashboard?file=prismatic/gateway/server.py -> 200 text/html
public /api/gateway/agents/status -> 200, source run_records+agent_registry+queue_state+timeline+health_context
public /api/gateway/timeline -> 200, source prismatic.timeline
public /api/gateway/skills -> 200, source prismatic.skills
public /api/gateway/quota -> 200
public /api/gateway/merge/status -> 200
public /api/workspaces -> 200
public /api/workspace-tree/node -> 200
public /api/workspace-tree/preview -> 200
public /workspace-tree?file=... -> 200
local traversal probe for /api/workspace-tree/node?file=../../etc -> 403
browser tab sweep: all visible tabs render, no old mock strings, zero JS errors
```

Known acceptable caveat: Tailwind CDN production warning can remain as a separate hardening item; do not confuse it with dashboard integration failure.

Compact stale-guard proof shape:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m py_compile prismatic/gateway/server.py && node --check /tmp/extracted-dashboard-inline-stale-guard.js
AD_HOC_VERIFICATION=PASS
changed_paths_checked=/home/ubuntu/work/prismatic-engine/docs/dashboard-durable-tab-integration-audit.md,/home/ubuntu/work/prismatic-engine/prismatic/gateway/templates/dashboard.html
runtime_paths_checked=/home/ubuntu/.prismatic/runtime/prismatic-engine/docs/dashboard-durable-tab-integration-audit.md,/home/ubuntu/.prismatic/runtime/prismatic-engine/prismatic/gateway/templates/dashboard.html
AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite
NOT_CLAIMING=canonical_full_suite_green,agy_completed_work_integration_gate,auto_merge
MARKER=DASHBOARD_DURABLE_TAB_INTEGRATION_AUDIT_OK,DASHBOARD_DURABLE_TAB_INTEGRATION_OK,DASHBOARD_WORKSPACE_TREE_MOBILE_OK
```

When a stale guard lists temp diagnostics as changed paths, remove stale `/tmp/cdp-*` and `/tmp/hermes-verify-*` files first, then create exactly one fresh `/tmp/hermes-verify-*` wrapper and remove it before reporting `cleanup=PASS`.

For mobile proof, assert an actual `390x844` viewport and the specific DOM state:

```text
Prismatic Hub Dashboard visible
Workspaces tab open
folder tree visible
file viewer visible
selected file visible
bodyOverflow <= 24 (0 in the worked repair)
previewOverflowX=auto
previewWhiteSpace=pre-wrap
workspace/header/nav proof markers present
```

If CDP evaluation samples before the preview fetch finishes, wait and resample; do not report the old failing `bodyOverflow=120` proof. If the CDP helper itself fails, say the browser-proof blocker plainly instead of claiming PASS.

## Pitfalls

- Do not claim tab integration from route 200 alone; inspect payload `source` and browser-rendered text.
- Do not leave public-only gaps hidden by local proof. If the dashboard runs under the public domain, prove the public `https://prismatic.growthwebdev.com/...` route matrix.
- Do not merge old dashboard branches wholesale; they may contain unrelated repo deletions or stale infrastructure.
- Do not treat compatibility/no-op routes as final when a real adapter/ledger exists; use them only for browser-safe controls and label them plainly.
- Do not let stale-guard proofs drift to older changed paths. Match `changed_paths_checked` exactly to the guard’s changed path.
- Do not trust the first mobile overflow guess. Use an overflow-finder DOM query to identify the element widening the page; in the worked repair the offenders were the global tab bar and header status cluster after the Workspaces panel itself was already fixed.

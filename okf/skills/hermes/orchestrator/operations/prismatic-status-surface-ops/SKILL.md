---
name: prismatic-status-surface-ops
description: Diagnose and repair Prismatic Engine status/dashboard surfaces so live public UI reflects current operational health instead of stale history or missing routes.
category: operations
---

# Prismatic Status Surface Ops

Use this skill when Michael asks why the Prismatic Engine status page/dashboard shows degraded, unhealthy, stale alerts, missing routes, or public URL failures.

## References

- `references/dashboard-durable-tab-integration-and-mobile-workspace-viewer.md` — durable dashboard tab/mobile viewer repair patterns and stale-guard proof shape.
- `references/pr-stack-retarget-and-runtime-deploy.md` — stacked PR retargeting after a foundation merge, CLI direct-run regression pattern, and runtime deploy proof for Prismatic gateway changes.

## Principles

- Verify the exact surface Michael is seeing: public HTTPS URL first when reachable, then local gateway/origin to isolate Cloudflare/Access vs app behavior.
- Do not stop at “localhost works” if the user reported a public URL. Make the public verification path work when authorized.
- Distinguish current health from durable history. Historical restarts, old synthetic drills, and archived alerts must not keep a live status page yellow forever.
- Keep verification labels precise: ad hoc targeted verification is not suite green.
- Use Antigravity locks before editing Prismatic workspace files and unlock after verification/commit or after the immediate operational patch.

## Triage workflow

1. Reproduce the exact user-visible URL/path:

```bash
curl -sS -D /tmp/headers -o /tmp/body --max-time 20 https://prismatic.growthwebdev.com/dashboard
head -40 /tmp/headers
head -c 300 /tmp/body
```

2. Compare local gateway routes:

```bash
curl -sS -D /tmp/local_headers -o /tmp/local_body http://127.0.0.1:9000/
curl -sS -D /tmp/local_dash_headers -o /tmp/local_dash_body http://127.0.0.1:9000/dashboard
```

3. Inspect the live route table when a path returns `{"detail":"Not Found"}`:

```python
import sys
sys.path.insert(0, '/home/ubuntu/work/prismatic-engine-stable')
from prismatic.gateway.server import app
for r in app.routes:
    print(getattr(r, 'path', None), getattr(r, 'methods', None))
```

4. If `/` or `/dashboard` 404s or shows a tiny fallback shell, **do not alias it to whatever `/` serves and do not invent a replacement dashboard**. First identify the canonical dashboard contract:

- Canonical Prismatic dashboard is the existing operator UI template: `prismatic/gateway/templates/dashboard.html`.
- `/` and `/dashboard` on `prismatic.growthwebdev.com` should serve that template when it exists.
- Required content markers for a successful reconnection are exact proof literals: `Prismatic Hub Dashboard`, `tab-btn`, `governance`, `merge`, `ingestion`, and `native-cron`. Treat marker casing as part of the contract; if the real existing template only has a human-visible label with different casing, add a tiny inert proof attribute to the existing element rather than replacing the dashboard.
- Keep a tiny fallback only for the missing-template case; it must not be the normal `/dashboard` experience.
- System status is only a compact footer/popup/widget on the operator dashboard, never a full-page replacement for `/dashboard`.
- A temporary standalone status page may live on a separate path only if explicitly requested; do not overwrite `/dashboard`.

5. If the status is degraded but services/endpoints are active, identify the exact stale signal:

```bash
systemctl show -p ActiveState,ActiveEnterTimestamp,NRestarts,ExecMainPID prismatic-gateway prismatic-consumer prismatic-curator prismatic-merge
curl -s http://127.0.0.1:9000/curator/health | python3 -m json.tool
```

6. Repair the health contract rather than masking symptoms:
   - `NRestarts` is cumulative; only mark degraded if restarts pair with fresh uptime/restart window.
   - Filter stale synthetic drills from current dashboard panels (`[SYNTHETIC TEST]`, `synthetic=true`, `fake-broken-service`).
   - Keep historical logs/audits intact; filter presentation, not durable records.

7. Restart the gateway and verify both root and dashboard routes:

```bash
systemctl restart prismatic-gateway
curl -sS http://127.0.0.1:9000/health
curl -sS http://127.0.0.1:9000/dashboard | grep -E 'HEALTHY|First-failing layer'
```

8. Use browser proof for UI changes. Michael explicitly prefers live UI proof, not just source/API checks.

## Governance dashboard wiring triage

When Michael says the governance dashboard has many missing connections, do not ask where to start. Scan for hardcoded/mock panels and choose the highest-leverage connective section first.

Recommended scan:

```bash
rg "mock|placeholder|href=\"#\"|button|render.*View|fetch\(" prismatic/gateway/templates/dashboard.html
rg "@app\.(get|post)|class .*Store|workspace|runs|skills|EventBus" prismatic/gateway prismatic
```

Prioritize sections that anchor other surfaces. The first worked example is **Workspaces**: it ties Golden Thread ventures, local repo checkouts, branch/dirty status, swarm locks, registration, and workspace optimization into one operator surface. If a dashboard template exists but no route serves it, wire canonical `/` and `/dashboard` before claiming UI work is reachable.

After Workspaces, the next high-leverage section is usually **Signals / Activity**. If the dashboard has `mockSignals`, a local-only activity feed, or a Signals tab that only reads `/runs` while EventBus/recovery/webhook data already exists, build a normalized Operational Timeline instead of patching one panel at a time:

```text
EventBus + run records + recovery-control ledger + webhook counters + manual governance events
→ /api/timeline + /api/timeline/summary + /api/timeline/record
→ dashboard activity feed + Signals tab + CLI
```

When wiring this class of section:
- remove fake fallback data entirely; use loading/empty/error states instead;
- make existing governance actions emit audit events into the timeline (workspace register/optimize, skills install/uninstall, recovery-control, etc.);
- wire visible dashboard controls to real/audit-safe endpoints before claiming they work. For Merge/Queue/Dispatcher, dashboard buttons may point at `/api/gateway/dispatcher/{action}`, `/api/gateway/webhooks/queue/retry/{task_id}`, and `/api/gateway/webhooks/queue/purge`; if those endpoints are missing, add safe ledger/timeline endpoints that record operator intent rather than shelling out from the browser;
- recovery controls should record both the existing recovery ledger and a `RecoveryControl` timeline event, while dispatcher and queue actions should emit `DispatcherControl` and `QueueControl` items visible via `/api/timeline?source=...`;
- if the main endpoints already return 200 but the default view is still not useful, add an operator-attention rail that ranks live dispatcher, queue, recovery, quota, merge, and timeline evidence into one prioritized next action rather than adding more raw panels;
- if inline dashboard JavaScript is edited, extract the `<script>` body and run `node --check` in the focused verifier;
- when a dashboard CTA should land on a specific row/item, prefer a stable inline handler plus explicit action state over dynamically assigning `button.onclick` after render; this survives async rerenders and is easier to verify from browser/DOM proof;
- if browser accessibility click tooling appears not to dispatch a newly updated handler, refresh the snapshot after async text/handler updates and also verify the DOM click path with `document.getElementById(...).click()` before declaring the UI broken; harden the implementation rather than recording a tool limitation;
- if a stale guard names an exact changed path, make the `/tmp/hermes-verify-*` output compact and machine-obvious: include that exact `changed_paths_checked` value and a plain `canonical_test_lint_build_command`, such as `node --check /tmp/hermes-dashboard-inline-stale-guard.js`;
- if adding a lightweight console script, smoke it from a fresh venv with `pip install --no-deps .`; if package import eagerly pulls heavy dispatcher deps, fix `prismatic/__init__.py` to lazy-load the dispatcher rather than adding unnecessary CLI deps.

See `references/governance-dashboard-workspaces-wiring.md` for the Workspace adapter/API/UI/verification pattern.
See `references/governance-dashboard-operational-timeline-wiring.md` for the Operational Timeline API/UI/CLI/audit pattern.
See `references/governance-dashboard-operator-attention-rail.md` for the default-view operator attention pattern when endpoints are connected but the dashboard still needs to rank the highest-signal next action.

## Domain separation and governance access

When Michael corrects a dashboard/domain mix-up, treat it as product-boundary governance, not cosmetic routing:

- `prismaticengine.com` / `www.prismaticengine.com` owns the public marketing site.
- `prismatic.growthwebdev.com` owns the protected Prismatic governance/control-plane dashboard.
- Both `/` and `/dashboard` on `prismatic.growthwebdev.com` should serve the canonical governance template at `prismatic/gateway/templates/dashboard.html` unless Michael explicitly changes the contract.
- Do not substitute Hermes plugin UI, Prismatic Hub mockups, marketing `index.html`, or a standalone status page for the canonical governance dashboard after Michael has rejected that path.
- Document this contract in-repo (for example `docs/governance-dashboard-routing.md`) so future route repairs do not re-mix marketing and governance.

If Fred is blocked from repairing Prismatic Engine files by lane governance, do not bypass the hook. Update the governance config intentionally so Fred, as orchestrator/staging governor, owns `"*"`, verify the hook allows the intended cross-lane paths, and then push normally. This preserves governance while allowing Fred to fix cross-lane messes.

If another agent is blocked by the lane guard on a legitimate recurring work class, fix the lane contract narrowly instead of telling them to use `--no-verify`. Example: Ned owns execution/runtime work; when HumanDesignEngine operational docs are produced alongside HDE scripts/bot runtime changes, grant specific HDE doc prefixes (`docs/hd-engine/`, `docs/hde-`, `docs/human-design-engine/`) rather than broad `docs/`. Also update any agent-facing lane reference that still recommends hook bypasses, because stale skill/reference docs will keep agents fighting the guard.

Lane-permission verification should import `scripts/pre-push-hook.py` and call `_check_lane_ownership()` against both positive and negative examples: the exact previously rejected paths must be owned, while unrelated `docs/`, `content/`, `assets/`, and `research/` paths must still be violations. After merge, read back `origin/deploy-fresh:PRISMATIC_ENGINE.yaml` and repeat the ownership check so the remote guard, not just the local checkout, is proven updated.

Clean-branch rule for these repairs:
- If the current branch is polluted with old Ned/deploy history or unrelated PWP/AGY files, create a clean branch from the correct base (`origin/deploy-fresh` for staging/governance hotfixes) and check out only the intended files.
- Use file-based PR bodies (`--body-file` or API PATCH) when Markdown contains backticks; inline shell strings can execute backticked text and corrupt the PR body.

See `references/governance-dashboard-domain-separation-and-fred-access.md` for the worked pattern.

## PWP/content status stabilization

When a dashboard/content pane reports `PWP status refresh failed: HTTP 404`, do not assume Kai/plugin work was lost. First compare the live/staging branch against `main` and local branches for `plugins/pwp`, `scripts/pwp`, and `plugins/pwp/themes`. The common failure mode is that the gateway route shell exists on `deploy-fresh`, but the real PWP package/manifest or newer CLI shim did not land there, while Kai theme assets may be stranded as untracked local files.

Stabilize by restoring the actual PWP plugin package/manifest and matching CLI shim onto the live branch, preserving real `plugins/pwp/themes/` assets, and adding non-breaking compatibility aliases for stale panes (`/pwp/status`, `/api/content/status`, `/content/status`) while keeping canonical `/api/pwp/status` intact. Verify manifest presence, route 200s, targeted PWP tests, and live gateway restart before relaunching AGY dispatch.

See `references/pwp-content-status-stabilization.md` for the worked PWP/content compatibility and Kai-theme preservation pattern.

## Dashboard missing integration 404 sweep

When Michael says “there are still lots of 404s throughout the dashboard,” do a full dashboard fetch/action matrix, not another single-endpoint fix:

- extract every `fetch(...)` call from `prismatic/gateway/templates/dashboard.html`;
- compare it to FastAPI route decorators in `prismatic/gateway/server.py`;
- probe the route matrix locally and after merge/restart;
- add dashboard-safe compatibility endpoints for missing panes;
- ensure browser control routes are auditable no-ops unless a real API-backed control path exists;
- perform a browser tab sweep and inspect console output after backend probes pass.

Also check for frontend schema mismatches after 404s are gone. In the worked incident, `/locks` returned `{path, agent, heartbeat}` while dashboard JS expected `{filePath, agentId, timestamp, lastHeartbeat}`, causing a JS `split` error even though routes returned 200.

**Important user-corrected pitfall:** route 200 / no-404 is not enough. If Michael says a tab still “doesn’t have quotas showing,” “PWP is still broken,” or “restore the real Kai-built integrations,” inspect the payload contract rendered by the tab and replace compatibility/fallback surfaces with the real data-backed adapter or persisted ledger. Treat `gateway-compat`, `dashboard-compat`, `empty-fallback`, and stateless `accepted_noop` as temporary stabilization, not a done state, when real data exists.

Worked restoration examples:
- PWP tab: preserve/restore `plugins/pwp`, `scripts/pwp`, and stranded `plugins/pwp/themes`; ensure `/api/pwp/status` is `connected` and lifecycle history renders.
- Quotas tab: the UI expects `current[]`, `recent_events[]`, `snapshot_at`, and `snapshot_age_sec`; bridge the persisted `~/.prismatic/quota_state.db` ledger if the newer Vertex telemetry shape only returns `quota_records[]`.
- Merge Pipeline: restore/use `prismatic/merge_status.py` and `~/.prismatic/merge-pipeline/state_v6.json`, not `empty-fallback`.
- Foundation: restore/use `prismatic/foundation_status.py`, not `gateway-compat` zeros.
- Dispatcher/Recovery/Webhook Stats: restore/use `prismatic/ingestion_status.py`, while keeping browser controls audit-safe and persisted as operator intent.

See `references/dashboard-missing-integration-404-stabilization.md` for the route-matrix, safe no-op endpoint, lock-shape compatibility, and browser-console verification pattern.
See `references/dashboard-real-integration-restoration.md` for the follow-up pass: restoring real Kai/design adapters and persisted ledgers after the 404 sweep.
See `references/governance-dashboard-full-tab-restoration-and-regression-contract.md` for the full top-down tab restoration pattern: Skills/Signals/Workspace Tree wiring, plugin mounting, durable regression contract, and stale-guard wrapper pitfalls.
See `references/dashboard-workspace-tree-main-tab-restoration.md` when `/workspace-tree` technically works but feels disconnected: restore the useful folder tree + file viewer inside the main dashboard Workspaces tab, support `/dashboard?file=...` Telegram deep links, and keep standalone `/workspace-tree` only as legacy/fallback while preserving traversal protections.
See `references/governance-dashboard-ingestion-queue-real-contract-restoration.md` for the deeper Ingestion Queue correction: distinguish route aliases from real queue storage, recover the old `linear_webhook_queue.db` implementation, reconcile it with newer QueueControl/DispatcherControl timeline auditing, and verify the dashboard-prefixed `/api/gateway/...` contract rather than only compatibility aliases.
- `references/operator-attention-deeplink-and-stale-guard.md` — Operator Attention CTA pattern: rank to a concrete queue item, use stable handler state, prove DOM click behavior, and satisfy exact-path stale guards with compact `node --check` verification output.
- `references/production-durability-standard-and-route-fix-gates.md` — Production durability standard pattern: prevent mutable-live-worktree route fixes, require local-first/public/browser/path-safety proof ladders, use `verify_production_durability_standard.py`, and distinguish standard-mode `needs_action` warnings from hard route closeout with `--enforce-route --require-local`.
- `references/production-runtime-checkout-and-workspace-tree-repair.md` — production-runtime application pattern after the standard is installed: migrate `prismatic-gateway.service` away from the mutable dev checkout, restore `/workspace-tree` routes/API/fallback content, prove live local 9000 with enforce-mode verifier and browser/DOM/screenshot evidence, and block rather than overclaim when Cloudflare Access prevents public/authenticated proof.
- `references/ingestion-queue-drain-smoke-and-operator-semantics.md` — compact proof pattern for `INGESTION_QUEUE_DRAIN_SMOKE_OK`, dashboard operator wording (`Reset to pending`, terminal-only purge, visible `linear_webhook_queue.db` source), and repeated stale-guard exact-path verification.
See `references/ingestion-queue-drain-smoke-and-agy-redispatch-gates.md` when the durable queue UI/API looks restored but readiness still depends on an executable bounded drain proof and separate AGY redispatch gating. Use this to produce `INGESTION_QUEUE_DRAIN_SMOKE_OK` without overclaiming `DASHBOARD_DISPATCH_INGESTION_READY_OK`, and to normalize legacy AGY model aliases before any one-task GRO-3837 proof.
See `references/linear-event-driven-dispatch-recovery.md` when Linear quota burn or old broad polling must be replaced with rate-limit circuit breaking, bounded fallback polling, and the durable Linear webhook queue path. It captures the `LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK`, `DISPATCHER_POLLING_BUDGET_OK`, and `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` proof ladders, old-poller kill-switch boundaries, fixture/drain smoke shape, and compact stale-guard packet format.
See `references/production-durability-standard-and-review-gates.md` when a production-facing route/service/dashboard needs standards, review gates, proof packet enforcement, production worktree policy, or compact fresh `/tmp/hermes-verify-*` verification after stale-proof warnings. It covers the `/workspace-tree` black-page incident as the first enforcement target while keeping the standard broader than one route.
See `references/ingestion-queue-dispatch-recovery-proof-gates.md` for the July 2026 gate-by-gate proof recipe: isolated temp-state drain smoke, dashboard operator-semantics stale guard, side-effect-free dispatch preflight decisions, and the hard boundary that `AGY_SINGLE_TASK_PROOF_OK` requires actual input/output token evidence before any final readiness claim.
See `references/assigned-agent-wake-dispatch-contract.md` when assigned work should wake the assigned agent safely: durable queue drain → `dispatch_issue_by_identifier()` → assigned-agent resolver → preflight → shared wake path → Linear writeback, covering Fred/Kai/Ned/AGY without treating AGY model-tier labels as separate assignment labels. It also includes the required behavior-table proof for per-agent routing, unknown/ambiguous `needs_manual_review` handling, Ned explicit-only wake checks, and the boundary that `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` still requires `AGY_SINGLE_TASK_PROOF_OK`.
See `references/agy-single-task-proof-runner.md` for the final canary gate after assigned-agent behavior is accepted: stop expanding resolver/wake work, run exactly `GRO-3837` with the installed `agy --print ... --model ... --log-file ...` shape, capture accepted proof equivalents (`prompt_length`, `task_payload_bytes`, `result_text_bytes`, artifact, Linear comment/state, and no-other-launch evidence), and only then claim `AGY_SINGLE_TASK_PROOF_OK` / recovery readiness.
See `references/agy-autopilot-result-packet-and-stale-guard.md` for the next class-level lane: converting single AGY canary output into safe mergeable Prismatic Dashboard work via result packet schema/validator, completed-work ingestion design, no-bulk/no-auto-merge first slice, CI secret-scanner-safe fixtures, and exact-path stale-guard verifier packets.
See `references/agy-completed-work-integration-gate.md` for the bounded completed-work gate slice after AGY result packets exist: pure packet classification, lane/scope/proof checks, read-only schema/demo API endpoints, compact dashboard card, no auto-merge/no bulk dispatch, and stale-guard exact-path cleanup when old mobile proof scripts keep resurfacing.
See `references/agy-completed-work-ingestion.md` for the next persisted-ingestion slice: canonical `non_claims`, SQLite row storage, `scripts/ingest_agy_result.py`, real POST/GET completed-work APIs, dashboard real-row status, stacked-PR hygiene, and `AGY_COMPLETED_WORK_INGESTION_OK` proof.
See `references/agy-clean-pr-verification-gate.md` for the follow-on merge backlog gate: transform persisted completed-work rows into dry-run PR plans, lane verification decisions, gateway APIs, dashboard backlog state, and `AGY_CLEAN_PR_AND_VERIFICATION_GATE_OK` without AGY dispatch, real PR creation, auto-merge, or deploy.
See `references/ingestion-queue-drain-smoke-and-operator-semantics.md` for the newer compact proof pattern: use real `prismatic.ingestion_queue`, real `scripts/drain_webhook_queue.py` shared `drain(args, dispatch_fn=...)`, visible `source = linear_webhook_queue.db`, literal `Reset to pending`/terminal-only purge labels, and stale-guard output with an explicit `node --check /tmp/hermes-dashboard-inline-stale-guard.js` command.
If the repair is too large to complete immediately or Michael asks for a goal prompt/handoff, use `templates/governance-dashboard-ingestion-queue-real-contract-goal.md` as the portable brief: it preserves the durable queue contract, old branch recovery sources, audit/timeline requirements, drainer-policy check, and done criteria without turning the current session narrative into a narrow one-off skill.

### Full-tab restoration rule

When Michael says the dashboard still feels fake or asks to start from the top and work through every tab, do **not** continue one endpoint at a time. Build a tab-by-tab matrix from the visible UI and verify each tab across frontend render, backend route, and real source. Treat `mockSkills`, `mockSignals`, old fake activity strings, `gateway-compat`, `dashboard-compat`, `empty-fallback`, and stateless `accepted_noop` as blockers when a real Kai/Ned adapter, plugin, or ledger exists. The work is not stable until a durable regression contract is committed that fails on these regressions.

For durable production tab integration plus mobile Workspace Tree viewer repair, use `references/dashboard-durable-tab-integration-and-mobile-workspace-viewer.md`. It captures the required prior-branch comparison, live adapter/route map, public `/api/gateway/...` alias lesson, mobile in-tab file viewer pattern, and exact-path stale-guard proof packet.

For a large dashboard/source audit digest where the first deliverable is preservation mapping rather than implementation, use `references/dashboard-reconnect-source-audit-and-stale-guard.md`. Create a clean audit worktree, compare runtime/current anchors first, classify A/B/C/D sources by evidence rather than score alone, write a source-map artifact with one next integration candidate, and if stale guard names an old `/tmp/hermes-verify-*` file, include that exact temp path in `changed_paths_checked` and prove it is absent after cleanup.

## Verification contract

## Verification contract

Create a focused temporary verifier under `/tmp` with a `hermes-verify-` filename prefix. It should cover:

```text
changed_path_exists=true
py_compile=passed
dashboard_route=canonical_template
full_page_status_takeover=absent
footer_system_status_widget=present
system_status_endpoint=responding
local_dashboard=200_operator_dashboard
public_dashboard=200_operator_dashboard
cleanup_exists=false
```

Report as **ad hoc targeted verification only — not suite green.**

## Pitfalls

- **The deployed gateway's source of truth is the runtime checkout, not the worktree you'd guess.** Multiple `work/prismatic-<feature>/` worktrees exist with divergent gateway code. To read deployed behavior: `pid=$(ss -tlnp | grep ':9000 ' | grep -oP 'pid=\K[0-9]+' | head -1)` → `tr '\0' ' ' < /proc/$pid/cmdline`, `ls -l /proc/$pid/cwd` (2026-08-20: `/home/ubuntu/work/prismatic-engine`), and `tr '\0' '\n' < /proc/$pid/environ | grep -iE 'registry|workspace'`. A stale worktree read produced a wrong API-shape diagnosis this session (the deployed workspace-tree preview API is `workspace_id`+`path`, not the `file=` param in older copies).
- **`invalid workspace identifier` from the workspace-tree preview is almost always a hand-typed `workspace_id` with the wrong zero-count — check your own input before blaming the gateway (2026-08-20: the "strict-registry flake" reading of this 400 was retracted as a false alarm).** The strict regex is `^ws-[0-9a-f]{32}$`; a 28-hex hand-typed body 400s instantly while `/api/workspaces` still lists all four workspaces — the list endpoint never shares your typo, so "list works, resolve 400s" looked like a registry flake. Correct workflow: **never hand-type the ID** — fetch it from `/api/workspaces` and feed it back programmatically, or better use the canonical deep link `/workspaces?file=<workspace-relative-path>` (307 → `/dashboard?file=…#workspaces`), where the SPA calls `/api/workspace-tree/resolve?file=…` and the server picks the owning workspace. Only if a *programmatically-sourced* ID 400s — with a unit-level repro in the gateway venv (`load_registry()` + `resolve()`, gateway env vars) — suspect the registry. A hosted review link must still be proven end-to-end (public domain, 200, sha256 of returned content == disk) before it's handed off; the fallback is tarball + SHA256 + Linear comment — the web link is never the only delivery path. See `references/workspace-tree-deep-link-contract-and-id-typo-2026-08-20.md`.
- Do not treat public Cloudflare Access redirect as a reason to avoid public verification. If Michael asks you to verify it, use the Cloudflare Access incident skill to add a narrow verifier-IP bypass.
- After public Access is solved, verify **asset routes** too. A page can return `200` while a first-party JS/CSS route is still a cached Cloudflare/nginx `404`; purge the exact URL and cache-bust the asset before claiming browser stability.
- Do not call a status page healthy while it still renders stale synthetic drills or fake service failures in the live UI.
- Do not let cumulative `NRestarts` keep status degraded indefinitely.
- Do not stop after patching a route; restart the live gateway and hit the exact public/user path.
- Do not let a “quick status fix” override product structure. Michael expects status to be an additive footer/bottom-right popover on the canonical operator dashboard unless he explicitly asks for a standalone status page.

## Support Files

- `references/prismatic-dashboard-healthy-route-fix-2026-07-09.md` — worked example covering stale degradation signals, missing `/dashboard` route, live restart, browser proof, and public Cloudflare verification.
- `references/canonical-dashboard-boundary-and-footer-status-widget.md` — user-corrected boundary: `/dashboard` must remain the canonical operator dashboard; system status belongs in a footer/bottom-right popover with API-backed live health.
- `references/governance-dashboard-public-live-verification-hardening.md` — Goal #7 pattern for portable dashboard contract verification: manifest endpoint, CLI, isolated local smoke, safe controls, and scoped mock-fallback checks.
- `references/public-workspace-tree-dashboard-route-repair.md` — public `prismatic.growthwebdev.com` workspace-tree/dashboard repair pattern: distinguish gateway route-table gaps from nginx proxy gaps, add read-only compatibility routes, preserve `/workspace-tree`, block traversal, follow PR→main→durable-runtime deploy ladder, and verify with live public + DOM proof plus exact-path stale-guard packets. If the canonical dashboard template exists, use `references/canonical-dashboard-template-reconnection.md` instead of leaving a fallback shell as primary `/` or `/dashboard`.
- `references/resources-budget-caps-port-and-stale-guard.md` — cleanly port bounded Resources budget-cap slices from older/dirty worktrees while preserving the durable dashboard shell, `/api/gateway` conventions, dispatcher guard tests, local API proof, stale-temp cleanup, and single-commit PR hygiene.
- `references/canonical-dashboard-template-reconnection.md` — user-corrected repair for `/` and `/dashboard`: inspect `prismatic/gateway/templates/dashboard.html`, serve the existing `Prismatic Hub Dashboard` from both routes, keep fallback only for missing-template 404, and prove public/local markers `Prismatic Hub Dashboard`, `tab-btn`, `governance`, `merge`, `ingestion`, `native-cron`.
- `references/public-access-runtime-route-proof-and-cache-purge.md` — follow-up pattern for protected public route proof after production durability repairs: create a narrow Cloudflare verifier-IP bypass, verify public HTML/API/assets/browser console, patch nginx exact asset proxy gaps, purge stale Cloudflare 404s, and cache-bust first-party scripts when browsers retain stale asset failures.
- `references/governance-dashboard-domain-separation-and-fred-access.md` — user-corrected domain boundary and governance-access pattern: keep marketing on `prismaticengine.com`, protected governance on `prismatic.growthwebdev.com`, route both `/` and `/dashboard` to `prismatic/gateway/templates/dashboard.html`, grant Fred `owner: ["*"]` through `PRISMATIC_ENGINE.yaml`, verify hook/dry-run push, and avoid polluted branches.
- `references/pwp-content-status-stabilization.md` — PWP/content status 404 stabilization pattern: compare `deploy-fresh` vs `main`, restore missing `plugins/pwp` + `scripts/pwp`, preserve stranded Kai theme assets, add safe compatibility aliases, and verify live route 200s plus targeted PWP tests before AGY relaunch.
- `references/okf-operations-closeout-documentation.md` — pattern for turning broad operational work into durable OKF closeout docs with index links and fresh `/tmp/hermes-verify-*` markdown verification.
- `references/governance-dashboard-operator-attention-rail.md` — pattern for adding a default-view rail that ranks live control-plane signals into one operator next action, with inline JS `node --check`, local endpoint smoke, browser DOM/console proof, and stale-guard readback.
- `references/ned-hde-lane-permission-gate.md` — narrow lane-governance pattern for unblocking Ned on HumanDesignEngine operational docs without broad `docs/` access or `--no-verify`, including exact `_check_lane_ownership()` positive/negative verifier examples and post-merge `origin/deploy-fresh` readback.
- `references/agy-single-task-proof-runner.md` — guarded AGY canary pattern for exactly `GRO-3837`: use installed `agy --print` CLI shape, persist prompt/payload/result/proof artifacts, write back Linear comment/state, verify no unrelated launches, and claim `AGY_SINGLE_TASK_PROOF_OK` only after readback.

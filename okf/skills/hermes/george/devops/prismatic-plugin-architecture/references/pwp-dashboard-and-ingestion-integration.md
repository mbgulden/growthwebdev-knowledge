## PWP full lifecycle reference plugin

Gap 8 is implemented: PWP is the canonical full-lifecycle reference plugin for PE. Use it as the exemplar for future plugins that must demonstrate connect → job → artifact/provenance → dashboard history → approval-before-publish → export/publish-ready → safe disconnect.

Primary surfaces:

- `prismatic/pwp_integration.py`
  - `run_pwp_reference_lifecycle()` runs the credential-free lifecycle demo.
  - `pwp_lifecycle_summary()` feeds dashboard/status history from the universal job/artifact registries.
- `scripts/pwp lifecycle demo [--keep-connected]` runs the demo from CLI.
- `POST /api/pwp/lifecycle-demo` runs it from Gateway/dashboard.
- `GET /api/pwp/status` includes `lifecycle_summary`.
- `plugins/pwp/plugin-manifest.yaml` version `1.2.0` declares `pwp.reference-lifecycle`, lifecycle events, `/api/pwp/lifecycle-demo`, and safe disconnect semantics.
- `prismatic/gateway/templates/dashboard.html` contains `pwp-lifecycle-history`, `renderPWPLifecycleHistory()`, and `pwpAction('lifecycle-demo')`.
- `docs/pwp-reference-lifecycle.md` documents the reference path.
- `tests/test_pwp_integration.py` covers function, API, CLI, status history, artifact approval/publish state, provenance, and safe disconnect preservation.

Verification pattern for PWP lifecycle changes:

```bash

TMP=$(mktemp -d)
PRISMATIC_STATE_DIR="$TMP/state" \
PRISMATIC_PWP_INTEGRATION_STATE="$TMP/pwp.json" \
PRISMATIC_PLUGIN_JOBS_STATE="$TMP/jobs.json" \
PRISMATIC_PLUGIN_ARTIFACTS_STATE="$TMP/artifacts.json" \
python scripts/pwp lifecycle demo
python -m pytest tests/test_pwp_integration.py tests/test_plugin_jobs.py tests/test_plugin_artifacts.py tests/test_plugin_policy.py tests/test_dashboard_ux_hardening.py -q
python scripts/dashboard_visual_qa.py
python scripts/public_launch_smoke.py
python scripts/release_smoke.py
python scripts/plugin_architecture validate plugins/pwp/plugin-manifest.yaml
```

Also extract the inline dashboard `<script>` and run `node --check` when touching the dashboard JS.

## Workspace Tree / public dashboard route repair

When `prismatic.growthwebdev.com/workspace-tree` or other operator dashboard routes render blank/black or 404, treat it as a **production route + shell resilience + worktree governance** problem, not just a CSS issue.

First separate public auth/proxy behavior from the local gateway route table:


```bash
curl -sS -D /tmp/h -o /tmp/b http://127.0.0.1:9000/health
curl -sS -D /tmp/h -o /tmp/b http://127.0.0.1:9000/workspace-tree
curl -sS -D /tmp/h -o /tmp/b http://127.0.0.1:9000/api/workspaces
PYTHONPATH=/home/ubuntu/work/prismatic-engine:/home/ubuntu/.prismatic/venv_stable/lib/python3.12/site-packages python3 - <<'PY'
import inspect
import prismatic.gateway.server as s
print(inspect.getfile(s))
for r in s.app.routes:
    p = getattr(r, 'path', None)
    if p and ('workspace' in p or 'dashboard' in p or p in ['/', '/health']):
        print(p, sorted(getattr(r, 'methods', []) or []))
PY
```

If `/health` is 200 but `/workspace-tree` and `/dashboard` are 404 locally, nginx is probably not the root cause; the running gateway source/branch lacks the route. Check `systemctl cat prismatic-gateway` and the service `WorkingDirectory`. Do not leave the live gateway tied to a mutable shared development checkout that may be on a Kai/Fred/AGY feature branch; prefer a dedicated production worktree or deliberately reset/update the service source to the intended deploy branch.

If routes exist but the page is black, inspect the shell. A Workspace Tree route that serves an empty dark `<main>` and then depends on Tailwind/React/ReactDOM CDNs plus plugin globals can fail silently under CSP/CDN/network conditions. Fixes should provide visible no-JS/dependency-failure fallback content (`Prismatic Workspace Tree`, loading/error text, API health links) before async/plugin code runs, or replace the shell with a self-contained no-CDN implementation. Preserve and mount the existing `hermes-plugin-workspace-tree-navigator` API where possible rather than duplicating internals.


Verification must include route behavior and visual non-blank proof: `py_compile prismatic/gateway/server.py`, route table contains `/workspace-tree`, local `/workspace-tree` returns 200 and contains visible fallback text, `/workspace-tree/index.js` returns 200 if used, tree/preview APIs work, traversal such as `../../etc/passwd` is blocked, production service runs the intended commit, and authenticated production screenshot/DOM evidence is not black/blank. Expected marker: `WORKSPACE_TREE_PRODUCTION_OK`. Detailed session pattern: `references/workspace-tree-production-route-repair-2026-07-15.md`.

## Dashboard UX hardening / visual QA

Gap 7 public dashboard UX hardening is implemented for the Gateway Plugins tab. Use these surfaces for dashboard/public-polish work:

- `prismatic/gateway/templates/dashboard.html` contains the public Plugins dashboard UX markers: `plugin-first-run-empty-state`, `plugin-onboarding-hints`, `plugin-error-explanation`, `copyDashboardCommand`, `plugin-detail-drawer`, `plugin-job-timeline`, `plugin-artifact-inventory`, `plugin-approval-controls`, and `plugin-dashboard-health-cards`.
- `scripts/dashboard_visual_qa.py` performs static dashboard visual QA; expected marker is `DASHBOARD_VISUAL_QA_OK`.
- `tests/test_dashboard_ux_hardening.py` covers public UX markers, mobile/responsive markers, and the visual QA script.
- `scripts/public_launch_smoke.py` and `scripts/release_smoke.py` include dashboard UX markers so public/release checks catch regressions.
- `docs/dashboard-screenshots.md` and `docs/assets/dashboard-plugin-ux-hardening.svg` document the public-polished dashboard state.

Dashboard UX verification pattern:

```bash
python scripts/dashboard_visual_qa.py
python scripts/public_launch_smoke.py
python scripts/release_smoke.py
python -m pytest tests/test_dashboard_ux_hardening.py tests/test_plugin_architecture.py tests/test_plugin_jobs.py tests/test_plugin_artifacts.py tests/test_plugin_policy.py -q
python -m ruff check scripts/dashboard_visual_qa.py scripts/public_launch_smoke.py scripts/release_smoke.py tests/test_dashboard_ux_hardening.py

python -m ruff format --check scripts/dashboard_visual_qa.py scripts/public_launch_smoke.py scripts/release_smoke.py tests/test_dashboard_ux_hardening.py
```

Also extract the inline dashboard `<script>` and run `node --check` when changing dashboard JS. If possible, do a browser pass against the static dashboard or Gateway route and check console errors.

### Dashboard branch integration / preservation handoffs

When Michael asks for dashboard repair, product/operator access restoration, a branch/repo/worktree audit, or a report for Fred/another agent during dashboard integration, treat it as a **preservation handoff**, not a normal status summary or new UI build. The goal is to prevent good dashboard work and good proof/planning work from overwriting each other.

If the audit is large, produce **two artifacts**: (1) a comprehensive appendix/source map and (2) a short Fred-execution digest/cheat sheet with A/B/C/D buckets, exact paths, exact next commands, red flags, and a pointer back to the appendix. Michael explicitly pushed back on huge blobs; Fred needs the small operator packet first. When the artifact is meant to be shared in Telegram, deliver it with `MEDIA:/absolute/path.md`, not only a local path.

If the task is an audit of many dashboard/governance branches, repos, or worktrees, do **not** deliver only a huge comprehensive blob. Produce two artifacts:

1. A full appendix/report for provenance and deep lookup.
2. A short Fred-first execution cheat sheet with a do-first sequence, A/B/C/D source buckets, exact source paths, exact commands, red flags, and a pointer to the full report.

Michael prefers the small execution packet first because Fred needs immediate discernment, not a wall of audit detail. Deliver Markdown reports/prompts as Telegram-downloadable files with `MEDIA:/absolute/path.md`, not just a local path. Session pattern: `references/dashboard-reconnect-source-audit-and-closeout-2026-07-17.md`.

Hard corrective rule from 2026-07-16: if `/` or `/dashboard` is down but an existing canonical dashboard shell exists on `deploy-fresh`, `feature/fred-real-*`, or `prismatic/gateway/templates/dashboard.html`, the task is to **reconnect/serve the existing dashboard**, not reinvent a fallback governance dashboard. Before asking Fred to implement UI, require branch/template inspection and explicitly preserve the existing Fred dashboard branch assets. A minimal fallback page is acceptable only as a temporary no-JS fallback around the existing dashboard route, not as a replacement for the canonical dashboard.


After the shell is reconnected, run a separate **durable tab integration** pass before claiming dashboard readiness. Inventory every dashboard tab, compare against prior good Fred branches/PRs, reconnect real adapters path-by-path, and explicitly list remaining mock/sample/no-op surfaces. For Workspace Tree inside the dashboard, require mobile visual/layout proof for `/dashboard?file=...` deep links, no unacceptable horizontal overflow, readable preview content, legacy `/workspace-tree?file=...`, and traversal 403. Session-specific details and prompt markers live in `references/dashboard-preservation-durable-tabs-2026-07-16.md`.

Use this class pattern:

1. Identify the active dashboard branch/HEAD and the reference main/HEAD.
2. Check whether either branch is ancestor of the other. If not, state clearly that the branches diverged and **do not reset either branch over the other**.
3. Map what each side owns:
   - dashboard/integration branch: protected route shell, live tab adapters, gateway compatibility routes, branch-specific verifier, ingestion/merge/foundation/recovery/native-cron/timeline surfaces.
   - main/proof branch: North Star, dashboard-primary/OKF docs, public launch/security/release docs, smoke scripts, visual QA, plugin/PWP/dashboard tests.
4. Static-inspect the dashboard before advising: extract tab IDs/labels, section IDs, JavaScript fetch targets, and FastAPI route decorators.
5. Distinguish **compatibility status** from **real execution**. A tab that returns EventBus history or `accepted_noop` for retry/purge is not yet a true ingestion queue runner.
6. Recommend a clean integration branch from the dashboard branch, then deliberate path-level porting of missing proof assets from main; avoid blind merges that overwrite the dashboard shell.
7. Include a do-not-do list and a final success marker such as `DASHBOARD_MAIN_PROOF_INTEGRATION_OK`.

For session-specific details and the ingestion queue distinction, see `references/dashboard-branch-integration-handoff-2026-07-14.md`.

For the later source-audit/digest/merge-deploy pattern, including the lesson that Fred needs a short execution cheat sheet plus full appendix and the service-path durability repair during deploy, see `references/dashboard-reconnect-audit-merge-deploy-2026-07-17.md`.

When reviewing Fred's dashboard/source-integration reports, independently verify PR shape, changed files, CI, claimed artifacts, source-path existence, anchor equality, and focused local/API behavior with a fresh `/tmp/hermes-verify-*` script. Use precise closeout language: review-ready/open PR is **PARTIAL**, not fully closed out, until merge/deploy/browser/production proof decisions are made. After a source-map PR plus first clean candidate PR are review-ready, pause further reconnect/source-mining by default and recommend the next workflow gap such as `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK` if Michael wants different Fred work. Session pattern: `references/dashboard-reconnect-source-audit-and-closeout-2026-07-17.md`.


### Ingestion queue follow-up audits after dashboard passes

When Fred or another agent finishes follow-up ingestion queue work, run a focused **durable queue contract audit**, not another broad dashboard rewrite. Check whether the dashboard path has moved from compatibility/EventBus stand-in rows to the real durable queue contract:

```text
Linear webhook → linear_webhook_queue.db → queue/stats APIs → dashboard tab → retry/purge/recovery controls
```

### Source-audit digest for Fred

When a branch/repo/worktree/source audit becomes comprehensive, also create a **small execution digest** for Fred. Michael does not want a huge blob as the primary handoff. Use the full audit as an appendix and give Fred a short cheat sheet with: do-first sequence, A/B/C/D source buckets, exact paths, first files to inspect, exact commands, red flags, and a pointer to the full audit. Bucket shape that worked well: A = inspect first/dashboard preservation value, B = governance/workflow source, C = runtime/canonical comparison anchor, D = archive fallback only. Session detail: `references/dashboard-source-audit-merge-deploy-2026-07-17.md`.


Preserve and inspect these surfaces when present:

- `prismatic/ingestion_queue.py` — durable DB schema/migrations, enqueue, normalize, stats, retry, purge.
- `prismatic/ingestion_status.py` — dashboard status/recovery summaries.
- `prismatic/gateway/server.py` — `/api/webhooks/queue`, `/api/gateway/webhooks/queue`, stats aliases, retry/purge aliases, and Linear webhook enqueue integration.
- `prismatic/gateway/templates/dashboard.html` — queue fetches, status rendering, retry/purge UI, no synthetic fallback markers.
- `scripts/drain_webhook_queue.py` — bounded CLI drain path that must agree with dashboard statuses.

- `scripts/verify-governance-dashboard-contract.py` — contract should expect `source=linear_webhook_queue.db` and reject old no-op retry/purge compatibility strings.

Use precise readiness language. If queue payload/stats/retry/purge pass but bounded drain + dispatcher transition is not yet proven, say:

```text
INGESTION_QUEUE_DURABLE_CONTRACT_OK — full queue-drain-dispatch proof still required before DASHBOARD_DISPATCH_INGESTION_READY_OK.
```

The next best slice is usually `INGESTION_QUEUE_DRAIN_SMOKE_OK`: prove temp queue row → bounded drain → status transition → dashboard reflects it → retry/recovery semantics. See `references/ingestion-queue-dashboard-audit-2026-07-15.md` for the session-specific verification pattern and pitfalls.

After writing a Markdown handoff/audit report, run a temporary `/tmp/hermes-verify-*.py` ad-hoc verifier for file existence, required headings/paths/tab labels or queue markers, basic secret-pattern absence, and SHA/line counts. Report this as **ad-hoc targeted verification**, not canonical suite green. For large source audits, also create a short execution cheat sheet and verify that it contains the do-first sequence, source buckets/rubric, exact commands, and pointer to the full report.

When the audit/report is large, do **not** hand Fred a giant blob as the only deliverable. Create a short execution digest or cheat sheet alongside the full appendix. The digest should be the primary handoff and should include: do-first sequence, A/B/C/D source buckets, tiny rubric, exact commands, red flags, and a pointer to the full report. Michael explicitly corrected this pattern: comprehensive is not enough if it is not stupid-easy for Fred to act on. Session detail: `references/dashboard-source-audit-digest-and-pr-review-2026-07-17.md`.

When reviewing a Fred source-map PR, verify both GitHub/CI metadata and the concrete local claims before accepting the report: PR changed files, doc markers, runtime/main anchor equality, candidate source path/file existence, dirty/clean status, and absence of stale `/tmp/hermes-verify-*` paths in committed docs. Use a fresh `/tmp/hermes-verify-*` script and remove it after. Report the result as ad-hoc targeted review, not canonical suite green. Session detail: `references/dashboard-source-audit-digest-and-pr-review-2026-07-17.md`.

When Hermes raises the post-edit verification guard for a Markdown-only handoff, satisfy it literally: create an actual script path under `/tmp` with a `hermes-verify-` filename prefix, run it against the changed document, remove it, and include the cleanup line in the final evidence. The verifier should fail closed on missing required markers/headings/paths or secret/token-like assignment patterns. If tool output redacts a numeric secret-hit count, do not rely on the redacted display; either phrase the script output as `SENSITIVE_ASSIGNMENT_SCAN_OK` / `HIT_COUNT_ZERO_CONFIRMED` or note that the script exits nonzero on any hit. This prevents repeated “unverified changed path” loops for prompt/checklist docs while staying honest that the result is ad-hoc, not a canonical suite.

# Prismatic dashboard preservation + durable tab integration — 2026-07-16

## What happened

During a Prismatic dashboard/operator-access repair, Fred initially restored `/` and `/dashboard` by creating a small fallback/operator shell. Michael corrected the workflow: the goal was not to invent a new governance dashboard, but to reconnect the existing Prismatic Hub Dashboard and preserve the good work Fred had already built across prior dashboard branches.

Then Fred reconnected the existing dashboard and moved Workspace Tree into the main **Workspaces** tab with folder navigation, file preview, `/dashboard?file=...` deep links, legacy `/workspace-tree?file=...`, and traversal protection. That was closer to the desired workflow, but the dashboard still contained mock/sample/broken tab surfaces and the mobile file viewer was not usable enough.

## Durable lessons

### 1. Route repair is not enough

For `/` and `/dashboard` repairs, route status `200` is insufficient. The proof must show the existing canonical dashboard is being served, not a replacement shell.

Required dashboard markers for reconnect proof:

```text
Prismatic Hub Dashboard
tab-btn
governance
merge
ingestion
native-cron
```

If those are absent, do not claim the existing dashboard is restored.

### 2. Preservation-first dashboard prompts

Dashboard repair prompts must require existing-asset inspection before implementation:

```text
origin/main:prismatic/gateway/templates/dashboard.html
deploy-fresh:prismatic/gateway/server.py
feature/fred-real-dashboard-adapters
feature/fred-real-ingestion-recovery-adapters
feature/fred-wire-remaining-dashboard-tabs
feature/fred-dashboard-regression-contract
feature/fred-ingestion-queue-real-contract
feature/fred-dashboard-workspace-tree-main
```

Use path-level diffs. Do not blind-merge or reset branches.

### 3. Durable tab integration is a separate pass

After the shell is alive, run a dedicated durable tab integration audit. The target is not another dashboard rewrite; it is to ensure every tab uses the best previously implemented real adapter or clearly declares remaining mock/no-op state.

Audit table shape:

| Tab / surface | Current live status | Best known branch/source | Missing pieces | Action |
|---|---|---|---|---|
| Workspaces | dashboard-native tree + preview | current main/Fred branch | mobile layout | fix |
| Governance | inspect live API | prior Fred dashboard branch | mock/sample? | reconnect real API |
| Merge backlog | inspect proxy/API | merge backlog route | public proxy? | reconnect/document |
| Ingestion queue | inspect durable queue | ingestion queue real contract | EventBus/no-op? | reconnect real queue |
| Recovery | inspect actions | recovery adapters | noop? | reconnect safely |
| Foundation | inspect adapters | real dashboard adapters | unknown | preserve/port |
| Native cron | inspect APIs | native cron tab work | unknown | preserve/port |
| Timeline/runs | inspect APIs | timeline/runs adapters | unknown | preserve/port |
| Plugins/PWP/quota | inspect APIs | PWP/quota tab work | unknown | preserve/port |

### 4. Mock/sample/no-op content must be surfaced, not hidden

If `mock`, `sample`, `accepted_noop`, compatibility rows, synthetic EventBus fallbacks, or placeholders remain, list them explicitly in the return packet. Do not relabel them as real.

### 5. Workspace Tree mobile acceptance

The dashboard Workspaces tab needs mobile visual proof, not just API proof. At ~390px viewport:

- folder tree and file viewer must stack or otherwise be readable;
- no body-wide horizontal overflow beyond a small tolerance;
- file preview content must be visible and scrollable;
- selected file/deep link must remain visible;
- `/dashboard?file=prismatic%2Fgateway%2Fserver.py` must land on the file;
- `/workspace-tree?file=...` must still work;
- traversal attempts must still return 403.

## Prompt markers from this session

Use these markers for future Fred dashboard goals:

```text
EXISTING_DASHBOARD_RECONNECTED_OK
DASHBOARD_WORKSPACE_TREE_MAIN_OK
DASHBOARD_DURABLE_TAB_INTEGRATION_AUDIT_OK
DASHBOARD_DURABLE_TAB_INTEGRATION_OK
DASHBOARD_WORKSPACE_TREE_MOBILE_OK
```

## Pitfall to avoid

Do not give Fred a prompt that says a "minimal acceptable page" is okay for `/dashboard` unless the prompt also says that the minimal page is only a missing-template fallback. Otherwise Fred may satisfy route/prod proof with a newly invented shell and lose the good dashboard work.

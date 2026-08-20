# Governance Dashboard Operational Timeline Wiring Pattern

Use this reference when the Prismatic governance dashboard has fake/static activity, signals, run logs, webhook status, recovery-control actions, or scattered event surfaces that should be one operator timeline.

## Selection heuristic

After Workspaces is wired, the next highest-leverage dashboard section is usually **Signals / Activity** because it becomes the audit spine for every other governance action:

```text
EventBus + run records + recovery-control ledger + webhook counters + manual governance events
→ /api/timeline
→ dashboard activity feed + Signals tab + CLI
```

This is higher leverage than polishing one panel because future buttons/endpoints can emit into the same timeline and become auditable immediately.

## Underwired signs

Search dashboard templates for:

```text
mockSignals
activity feed using hardcoded arrays
Signals tab using only /runs while EventBus/recovery/webhook data exists
buttons that append local-only DOM rows instead of recording server-side events
```

Compare against existing backend primitives before inventing storage:

- EventBus SQLite rows: `/events/recent` or the underlying event log DB
- run records: `/runs`, `AgentRunRecordStore`
- dashboard recovery controls: `_read_dashboard_recovery_state()`
- webhook counters: `_webhook_counters`
- manual/governance audit events: small state file under `PRISMATIC_STATE_DIR`

## Useful API contract

Add a pure-ish adapter instead of embedding logic in FastAPI handlers:

```text
prismatic/timeline.py
GET  /api/timeline
GET  /api/timeline/summary
POST /api/timeline/record
```

Timeline item shape:

```json
{
  "id": "stable-string",
  "timestamp": "ISO-8601 or null",
  "kind": "event|run|recovery|webhook|system|manual",
  "source": "EventBus|RunStore|RecoveryControl|Webhook|Manual",
  "severity": "info|success|warning|error",
  "title": "Short human title",
  "message": "Operator-readable message",
  "status": "optional status",
  "entity_id": "optional entity id",
  "metadata": {}
}
```

## Dashboard wiring rules

- Remove `mockSignals` entirely; do not leave fake fallback rows.
- Homepage `#dashboard-activity` should fetch `/api/timeline?limit=8`.
- Signals tab `#signals-log-box` should fetch `/api/timeline?limit=50`.
- Loading/empty/error states are acceptable; fake success data is not.
- Existing local-only signal appenders should call `POST /api/timeline/record` and then refresh the live feed.
- If a dashboard function uses `await`, make the function itself `async` and await it from callers. In the worked pass, this caught an existing `renderDashboardSummary()` async bug.
- Run `node --check` against the extracted dashboard `<script>` after editing large inline dashboard JavaScript.

## Governance action audit rule

When wiring a new real endpoint/button, make at least one existing governance action emit a timeline event. Good initial candidates:

```text
/api/workspaces/register  → source=WorkspaceRegistry, title=Workspace registered
/api/workspaces/optimize  → source=WorkspaceOptimizer, title=Workspace optimized
/api/skills/*/install     → source=SkillRegistry, title=Skill installed
/api/dashboard/recovery-control → source=RecoveryControl
```

This turns the timeline into a living audit surface rather than just a read-only aggregator.

## CLI / portability pattern

If the timeline becomes a Core product, add a CLI:

```text
prismatic-timeline list --limit 20
prismatic-timeline summary
prismatic-timeline record --source Hermes --severity info --title "..." --message "..."
```

Fresh-venv console-script smoke should install with `pip install --no-deps .` when the CLI is stdlib-only. If importing `prismatic.timeline` pulls heavy dispatcher dependencies, fix package import behavior by lazy-loading the dispatcher from `prismatic/__init__.py` rather than adding unnecessary CLI dependencies.

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile __init__/server/timeline/tests
node --check extracted dashboard script
focused pytest for timeline API
mockSignals absent
/api/timeline fetch present
dashboard-activity and signals-log-box present
/api/timeline/record path present
isolated PRISMATIC_STATE_DIR manual record/list/summary pass
workspace register/optimize emit timeline items if wired
python -m prismatic.timeline list/summary/record pass
fresh venv console script prismatic-timeline record/list pass
cleanup removes verifier and temp state/venv/workspace
```

For live UI/API smoke, start a temporary gateway on a non-production port and hit `/dashboard`, `/api/timeline`, and `/api/timeline/summary`, then kill the process.
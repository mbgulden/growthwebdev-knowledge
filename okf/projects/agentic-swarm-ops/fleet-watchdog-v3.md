---
resource: okf/projects/agentic-swarm-ops/fleet-watchdog-v3.md
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/fleet-watchdog-v3.md
migrated_from_repo: mbgulden/agentic-swarm-ops
last_verified: 2026-08-19
verified_by: kai
status: current
---

# Fleet Watchdog v3 — Alert + Auto-Action

**Date:** 2026-06-24
**Status:** Active (deployed)
**Author:** Fred (with Michael's design input)

## Why this exists

The old "AGY Watchdog" cron wrapped `agy_watchdog.py` in an LLM (deepseek-v4-flash) every 5 minutes to format a Markdown report for Telegram. Problems:

1. **Alerts without resolution** — Michael got told about problems but no system tried to fix them.
2. **Naming confusion** — it's not an "AGY" watchdog; it monitors the entire fleet.
3. **LLM cost** — ~288 deepseek calls/day just for formatting (~$0.10/day, but unnecessary).
4. **Always-on noise** — even when green, the LLM would produce a "🟢 All good" message that got delivered.

## What changed

### New files

| File | Lines | Purpose |
|---|---|---|
| `ops/fleet_watchdog.py` | 171 | Wrapper that runs `agy_watchdog.py`, captures its alerts, dispatches auto-actions, renders structured report |
| `ops/auto_actions.py` | 283 | Idempotent recovery handlers (restart gateway, drain queue, refresh OAuth, kill stuck AGY, GPU failover, disk cleanup) |
| `ops/tests/test_fleet_watchdog.py` | 142 | 13 tests covering dispatch, silent-on-green, action handler shape |

### Cron job change (500749c7949d)

```
BEFORE:                            AFTER:
  name: "AGY Watchdog..."           name: "Fleet Watchdog v3..."
  no_agent: false                  no_agent: true
  script: null                     script: "fleet_watchdog.py"
  model: deepseek-v4-flash         model: null
  provider: deepseek               provider: null
  prompt: [LLM formatting task]    prompt: "No-op. The script handles everything."
  deliver: local                   deliver: telegram:8190664947
```

The cron now runs `python3 fleet_watchdog.py` directly. The script's stdout IS the report. On green → empty stdout → cron delivers nothing. On yellow/red → structured report with action taken.

### Symlinks

```
~/.hermes/profiles/orchestrator/scripts/fleet_watchdog.py → /home/ubuntu/work/agentic-swarm-ops/ops/fleet_watchdog.py
~/.hermes/profiles/orchestrator/scripts/auto_actions.py   → /home/ubuntu/work/agentic-swarm-ops/ops/auto_actions.py
```

## Auto-actions (the "actually do something" piece)

Each handler is idempotent — calling it twice on a healthy system returns "skipped". All return `(status, message)` where status is `"ok" | "failed" | "skipped"`.

| Alert pattern | Action | What it does |
|---|---|---|
| `prismatic-gateway.service` not active | `action_restart_gateway` | `systemctl start` + verify |
| `Webhook queue ... pending` | `action_drain_webhook_queue` | `systemctl start prismatic-webhook-drain.service` |
| `OAuth token expiring` <5min | `action_refresh_oauth` | runs `linear_oauth_refresh.sh` |
| `PID N: Stalled` | `action_kill_stuck_agy` | SIGTERM → SIGKILL after 2s |
| `Local GPU instances are unresponsive` | `action_gpu_failover` | renames `ollama-*` → `ollama-*-disabled` (already worked in v2; now exposed as auto-action) |
| `Disk usage > threshold` | `action_disk_cleanup` | rotates large logs, vacuums state DBs, cleans stale AGY temp files |

### Adding a new auto-action

1. Add a handler to `auto_actions.py` with signature `(ctx: dict) -> tuple[str, str]`.
2. Add an `(alert_prefix, handler)` entry to `ACTIONS_BY_ALERT_PREFIX`.
3. Add a test in `test_fleet_watchdog.py`.
4. Handlers MUST be idempotent — the report renders action results, so re-running on a healthy system must say "skipped", not "ok" or "failed".

## Output format (what Michael sees)

When green (no alerts):
```
[empty — nothing delivered]
```

When yellow/red:
```
🛰️ Fleet Watchdog — 2026-06-24 18:21:54 UTC
Status: 🔴 red
Alerts: 6 (status lines: 1)

🟡 Log signal: W0624 ... Cache(loadCodeAssistResponse): Singleflight refresh
   → ⏭️ no auto-action (manual review needed)

🔴 Local GPU instances are unresponsive! Triggering automatic OpenRouter failover.
   → ✅ action: action_gpu_failover
     GPU providers renamed to *-disabled; OpenRouter fallback active

Context:
  🟢 No AGY processes running
```

The "→ ✅ action: ..." line is the key change. You see **what the system did** before you even read the alert.

## Verification

- `pytest ops/tests/test_fleet_watchdog.py` → **13/13 pass**
- Direct run: `python3 ops/fleet_watchdog.py` → produces report with GPU failover action taken
- Cron trigger: `hermes cron run 500749c7949d` → confirmed next-tick scheduling
- Live: next 5min tick will deliver the report to Telegram (or stay silent if green)

## Follow-ups

- [ ] Watch for one full day to confirm log noise reduced
- [ ] Consider adding: Slack alert channel (separate from Telegram)
- [ ] Consider: AGY recovery action (currently SIGTERM, could trigger re-dispatch)
- [ ] Document in `agentic-swarm-ops/docs/` after one week of stable operation

## Backwards compatibility

`agy_watchdog.py` is unchanged — the detection logic stays put. `fleet_watchdog.py` imports it. If we ever rewrite detection, the wrapper stays.

The cron job is still ID `500749c7949d`. Its name changed. Downstream dashboards that grep for the old name need to be updated.
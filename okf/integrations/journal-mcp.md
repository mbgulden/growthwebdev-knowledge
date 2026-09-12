---
type: Integration
title: Journal MCP — Prismatic Journal Corpus Query Server
description: Stdio MCP server (5 read-only tools) over the canonical Prismatic journal corpus at ~/work/Hermes-Research/journals — makes the swarm-wide daily/weekly journals and the daily event index queryable by any agent. Same pattern as okf-mcp.
resource: /home/ubuntu/work/journal-mcp-server/server.py
tags: [mcp, journal, prismatic-engine, hermes, query, stdio, portable]
timestamp: 2026-08-20T14:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/journal-mcp.md
linear_issue: null
last_verified: 2026-09-12
verified_by: fred
status: current
auth_method: none (local stdio, read-only)
---

# Journal MCP — Prismatic Journal Corpus Query Server

## What it is

A stdio MCP server exposing the **canonical Prismatic journal corpus** to any
agent as 5 read-only tools. Same architecture as `okf-mcp-server` (stdio
subprocess, hermes-agent pipx venv, no credentials, local reads only).

It does NOT write to the journal, does NOT alter the collector, and does NOT
serve the dashboard. It is the **read/query surface** for the corpus that the
Prismatic journal collector (cron) already maintains.

**Portability:** This MCP server is harness-agnostic. It reads from a fixed
file path and exposes a standard MCP stdio interface. Any MCP-compatible
harness (Hermes, Claude Desktop, Cursor, Windsurf, or any custom client)
can register it with a 3-line config block. No Hermes-specific imports,
no gateway dependency, no profile awareness.

## Corpus it reads (do not move without updating the server)

Root: `/home/ubuntu/work/Hermes-Research/journals`

| Path | What | Notes |
|---|---|---|
| `<year>/<month>/<day>.md` | Daily swarm recap (all agents) | Covers 00:00–06:00 UTC + evening addendum. Sections: Memo, Work Completed, Key Events, Decisions Made, Errors & Issues, Cron Fleet, Sources & Links, Blockers, Follow-ups. |
| `weekly/<YYYY>-Www.md` | Weekly rollup | ISO week. |
| `.index/events-<YYYY-MM-DD>.json` | Daily normalized event index | `cron_run` / `log_error` / `restart` events with idempotency keys, job names, timestamps. |
| `inbox/<YYYY-MM-DD>.md` | Hourly collector snapshots | Raw-ish; lower value than the recap. |
| `.quarantine/` | Malformed/timestamp-less lines | Noisy; not exposed by MCP by design. |
| `latest.md` / `latest-weekly.md` | Symlinks to newest | |

Swarm-wide by design: one corpus covering all profiles (kai, fred, george,
ned, autobot, orchestrator, …). **Becca's personal HD journal is separate
and private** at `~/work/next-step-becca/journals/` and is intentionally NOT
in this corpus.

## Tools

| Tool | Args | Returns |
|---|---|---|
| `journal_latest` | — | Latest daily recap, full markdown (60KB cap). |
| `journal_read` | `date` = `YYYY-MM-DD` or `YYYY-Www` | Full markdown for that entry (60KB cap). |
| `journal_list` | `limit=30` | Available daily + weekly dates, newest first. |
| `journal_search` | `query`, `limit=10` | AND-keyword search across recap markdown + event-index summaries, ranked hits with snippets. |
| `journal_freshness` | — | Collector health: last index day, last recap day, index gaps (last 14d), corpus size. |

## Registration (harness-agnostic)

### Hermes (any profile)

Add to the profile's `config.yaml`:

```yaml
mcp_servers:
  journal:
    command: /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python
    enabled: true
    args:
      - /home/ubuntu/work/journal-mcp-server/server.py
```

### Claude Desktop / Cursor / Windsurf / any MCP client

Add to the client's MCP config (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "journal": {
      "command": "/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python",
      "args": ["/home/ubuntu/work/journal-mcp-server/server.py"]
    }
  }
}
```

### Direct smoke test (no harness needed)

```bash
cd /home/ubuntu/work/journal-mcp-server && \
  /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -c "
import server; print(server.journal_freshness())"
```

**Discipline:** always call `journal_freshness()` before treating journal
content as *current*. A stale collector (index gaps, old `last_daily_recap`)
means the corpus may not reflect today — say so rather than presenting old
content as live state.

## Collection Pipeline (who writes the corpus)

As of 2026-09-12, the journal collection pipeline runs on **two parallel
systems** during the switchover window:

| Job | Hermes native cron | SwarmCron daemon |
|---|---|---|
| Hourly snapshot | `Hermes daily journal snapshot` (every 60m, no_agent) | `journal-snapshot` task (`0 * * * *`, swarmcron-tick.service) |
| Daily recap (23:59 UTC) | `Hermes daily journal recap` (agent-mode, LLM) | — (not yet migrated) |
| Weekly rollup (Sun 10:00) | `Weekly Journal Rollup` (agent-mode, LLM) | — (not yet migrated) |
| Monthly continuity audit | `Monthly Journal Continuity Audit` (no_agent) | — (not yet migrated) |

The SwarmCron tick daemon (`swarmcron-tick.service`) is the **portable
scheduler** — it runs independently of any LLM harness and can be started on
any machine with Python 3.10+ and the swarmcron package. See
`okf/audits/prismatic-cron-runner-status-audit-2026-09-12.md` for the full
architecture.

**Switchover:** When 5+ consecutive stability checks pass (tracked by the
`SwarmCron Stability Monitor` cron job, every 6h), the Hermes native
snapshot job will be paused and SwarmCron becomes the sole scheduler for
journal collection.

## Ownership / non-goals

- **Owns:** the read/query contract over the corpus.
- **Does not own:** collection (SwarmCron daemon + Hermes native cron), the
  dashboard Logs→Journals UI (GRO-4189/4190, paused), retention policy,
  quarantine classification.
- **Next step (PE side, Fred):** GRO-4189 read API so the dashboard consumes
  the same corpus. The MCP is the agent-side surface until then.

## Known corpus wounds (inherited, not fixed by this MCP)

- Legacy index (pre-incremental, ~before 07-09) has no stable dedupe keys — history, not evidence.
- Quarantine is a noisy dump (~5 MB, mostly non-timestamped log lines).
- Retention ambiguity: code prunes 90 days, governance says 400.
- Oversized pre-fix recap artifacts (daily 672 KB / weekly 2.7 MB) retained as backups.

See `okf/reports/journal-continuity-agy-crack-audit.md` and the 2026-07-23
continuity audit + unification plan (orchestrator deliveries) for the full
remediation.

## Related

- [Hermes Memory vs Skills Boundary Discipline](../standards/hermes-memory-skills-boundary-discipline.md) — where the journal sits in the memory/skills/OKF split (the journal = the evidence layer).
- [Prismatic Journal-Setup Independence Map](../standards/prismatic-independence-map-journal-setup.md)
- [OKF MCP](../standards/okf-skill-hub.md) — the sibling read-only MCP this copies its pattern from.
- [Journal System & MCP — End-to-End Audit (2026-08-21)](../audits/journal-system-and-mcp-audit-2026-08-21.md) — live-verified system audit; 9 gaps with fill steps.
- [Prismatic Cron Runner — Full Status Audit (2026-09-12)](../audits/prismatic-cron-runner-status-audit-2026-09-12.md) — 3-layer cron architecture, swarmcron tick daemon, migration path.

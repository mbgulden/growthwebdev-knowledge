# Running-server health check — liveness vs freshness

When asked "is the X MCP server good to go?" (or after a data-repo commit that
the server may have missed), prove BOTH layers:

1. **Liveness** — process running, tools reachable, live reads return current data.
2. **Freshness** — any in-memory/cached state (search indexes, loaded datasets,
   token caches) is as new as the underlying data.

A server can be fully alive and still serve stale search results. Report both,
separately — never collapse "it responds" into "it's current."

## Diagnosing a stale in-memory index

1. Get the data's latest change timestamp (e.g. `git log -1 --format='%ci'` in the
   repo the server wraps) and the server process start times:
   ```bash
   ps -o pid,lstart,cmd -p <pids>
   ```
   If the newest change postdates every server start, any index built at
   process start is stale by that delta. (OKF case, 2026-08-19: 5 server
   processes started 02:31–03:24 UTC; the commit that added the new doc landed
   03:45:33 — so `okf_search` returned 0 hits for the new doc while
   `okf_read` on the same path worked.)
2. Prove which tool paths are stale vs live:
   - Stale path: search/index tool misses a known-new item.
   - Live path: direct-read tool returns the new item (disk read, no cache).
3. Check whether an in-process refresh exists and is enabled — e.g. OKF's
   `update` tool is gated on `OKF_ALLOW_UPDATE=1`. Inspect the running process
   env without guessing:
   ```bash
   tr '\0' '\n' < /proc/<pid>/environ | grep '^OKF_ALLOW_UPDATE='
   ```

## Remediation options (cheapest first)

- **Self-heal**: many MCP servers are respawned per Hermes session, rebuilding
  state from disk at start. If the data on disk is already current (repo clean,
  no pull needed), the stale state clears on the next session — say so.
- **Respawn now**: `/reload-mcp` in the affected chat (safe, no service restart),
  or restart the profile's systemd service (ask first).
- **Enable in-process refresh**: add the env gate (e.g. `OKF_ALLOW_UPDATE=1`) to
  the server config so the refresh tool works without restarts. Weigh against
  losing the read-only default — often not worth it.

## Reporting shape

```text
RESULT=PASS|PARTIAL (liveness always verifiable; freshness may lag by N commits)
SCOPE=which profile(s) were probed this session
STALE_WINDOW=<commit ts> vs <server start ts>
REMEDIATION=self-heal on next session | /reload-mcp now | enable env-gated refresh
NOT_CLAIMING=other profiles not re-probed | no git pull performed
```

## Pitfalls

- Do NOT conclude the server is broken when search misses a brand-new doc —
  check process age vs commit age first; "stale by one commit" is usually by design.
- Do NOT claim "update disabled" from the tool description alone — verify the
  env on the actual running PIDs; different profiles may differ.
- `recent`-style tools may share the same in-memory index as `search` — verify
  per-tool, don't assume one tool's freshness implies another's.

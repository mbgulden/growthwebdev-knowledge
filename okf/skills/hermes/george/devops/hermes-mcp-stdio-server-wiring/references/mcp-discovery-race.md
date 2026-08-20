# MCP discovery race — anatomy (observed 2026-08-18, hermes-agent pipx venv)

Symptom: `hermes mcp test <server>` passes, but the model in a real session reports
"no mcp_* tools in my toolset" and falls back to terminal hacks.

## How discovery works (code paths)

- `tools/mcp_tool.py::discover_mcp_tools()` — reads `mcp_servers` from profile config,
  connects each stdio server (spawn + initialize + tools/list), registers `mcp_<server>_<tool>`
  into the shared registry. Idempotent: already-connected servers are skipped.
  On success logs: `MCP: N tool(s) from N server(s)` (agent.log, logger `tools.mcp_tool`).
- `hermes_cli/mcp_startup.py` — CLI/TUI spawn `discover_mcp_tools()` in a **daemon
  background thread** so startup can't hang on a dead server.
  `wait_for_mcp_discovery(timeout)` = `thread.join(timeout)` — the bound comes from
  `mcp_discovery_timeout` in config.yaml, **default 1.5s**
  (`hermes_cli/config.py` DEFAULT_CONFIG).
- Agent tool snapshot: `agent.tools` is captured **once at agent build time** and never
  re-read (`run_agent/agent_init`). If discovery hadn't finished at build time, the tools
  are absent for the whole session (gateway: until `/reload-mcp` or restart).

## Log signatures

`~/.hermes/profiles/<p>/logs/mcp-stderr.log` (server side):
```
===== [timestamp] starting MCP server '<name>' =====
INFO  Processing request of type ListToolsRequest   <- server IS answering
```
`agent.log` (client side):
- healthy: `tools.mcp_tool: MCP: registered N tool(s) from N server(s)`
- raced: the `MCP:` line is **absent** for the session id, even though stderr shows the
  server handled ListToolsRequest. That gap = discovery finished after the join bound.

## Timing reality

Cold `python server.py` (hermes pipx venv, ~1500-doc markdown index built at import):
first byte of initialize response ≈ **1.4–1.7s** (measured with `time` over stdio).
That is *at or over* the 1.5s default bound → coin-flip registration in CLI paths.

## Fixes / rules

1. Set `mcp_discovery_timeout: 10` in every profile config (atomic YAML round-trip +
   `config check`). The join is capped, not a floor — fast/no-MCP startups still pay ~0s.
2. Gateway (`gateway/run.py`) runs discovery **synchronously in an executor at startup**
   (before `runner.start()`), so a gateway restarted after config changes is fine;
   a gateway running *before* the change needs `/reload-mcp` (in-chat, safe) or service
   restart.
3. `hermes -z` one-shot: agent build can precede the background discovery landing →
   false "no tools" results. Treat `-z` as an unreliable MCP proof harness; use the
   interactive CLI (agent built after first prompt, discovery complete) or the
   deterministic `discover_mcp_tools()` probe (same code path the gateway uses).
4. `tui_gateway/server.py::_schedule_mcp_late_refresh` exists to patch late-landing tools
   into pre-first-turn sessions automatically; once a turn has started the snapshot is
   frozen (prompt-cache safety) and only `/reload-mcp` can fix it.

## Tool-count note

`discover_mcp_tools()` registration includes protocol handlers as tools
(`mcp_<server>_list_resources`, `_list_prompts`, `_read_resource`, `_get_prompt`), so the
probe can show more tools than `hermes mcp test`'s discovery list. Not a bug.

---
name: hermes-mcp-stdio-server-wiring
description: Build stdio MCP servers and wire them into one or all Hermes profiles with verified proof (transport test, registration probe, live model tool-call). Use when adding an MCP server to Hermes, exposing a local repo/API as agent tools, or debugging missing mcp_* tools in a profile.
---

# Hermes MCP stdio server wiring

Wire a new stdio MCP server into Hermes profiles and prove it works at three layers: transport → registration → live model tool-call. Proving only one layer and calling it done is the classic overclaim.

## Trigger conditions

- "Set up X as an MCP server and connect it to Hermes / all profiles"
- Exposing a local knowledge base, repo, or API as `mcp_*` tools for agent profiles
- Debugging: model says "no mcp_/okf_ tools in my toolset" even though `hermes mcp test` passes

## Runtime choice

Use the hermes-agent pipx venv python — the MCP SDK is already installed there:
`/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python`
Do NOT use system python3 (no `mcp` package) unless you create a dedicated venv and point the config at it.

## Steps

1. **Write the server.** FastMCP stdio pattern: `mcp = FastMCP("name")` + `@mcp.tool()` functions returning JSON strings, `mcp.run(transport="stdio")` at bottom. Keep stdout pristine (protocol channel) — log to stderr only.
2. **Standalone smoke test** (before touching Hermes): run `scripts/mcp_stdio_smoke.py` against the server. It speaks raw JSON-RPC over stdio: initialize → tools/list → tools/call. Catches import errors, stdout pollution, and bad tool payloads without any Hermes involvement.
3. **Wire per profile:**
   ```bash
   printf 'Y\n' | hermes --profile <p> mcp add <server> \
     --command /home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python \
     --args /path/to/server.py
   ```
   The piped `Y` answers the interactive "Enable all N tools?" prompt — without it the command hangs waiting on stdin in a non-TTY shell.
4. **Bump the discovery timeout** in each profile's `config.yaml`: set `mcp_discovery_timeout: 10` (default is **1.5s**, and a cold Python stdio handshake takes ~1.4–1.7s — see Pitfalls). Edit via YAML round-trip (`yaml.safe_load` → mutate → `safe_dump` → re-load to verify), never sed. Then `hermes --profile <p> config check`.
5. **Canonical transport proof (per profile):** `hermes --profile <p> mcp test <server>` → expect `✓ Connected (…ms)` + `✓ Tools discovered: N`.
6. **Registration probe (per profile or at least the active one):** run in the venv python:
   ```python
   from tools.mcp_tool import discover_mcp_tools, get_mcp_status
   print(discover_mcp_tools()); print(get_mcp_status())
   ```
   Expect `mcp_<server>_<tool>` entries and status `connected`. This is the same code path the gateway runs, so it predicts production behavior.
7. **Live model proof:** interactive CLI session in a **background PTY** (`terminal(command="hermes --profile <p>", pty=true, background=true)` — a *foreground* interactive run exits immediately with "Input is not a terminal (fd=0)"). Wait ~30–60s; the banner line `MCP Servers / <name> (stdio) — N tool(s)` is itself registration proof. Then send the forcing prompt with `process(action="submit")` — `write` does NOT send Enter, a `write`-only prompt just sits in the input buffer forever. The interactive path builds the agent AFTER discovery lands.
   **Read proof from `~/.hermes/profiles/<p>/logs/agent.log`, not the PTY buffer** (the buffer is escape-code garble): expect `tool mcp_<server>_<tool> completed (…s, N chars)` lines plus `Turn ended: … tool_turns=N`.
8. **Activate running gateways:** live gateway processes started before the config change do NOT see the new server. Send `/reload-mcp` to the bot (in-chat, safe) or restart the profile's systemd service. Ask Michael before restarting services.

## Pitfalls

- **Discovery-timeout race (the big one).** `mcp_discovery_timeout` defaults to 1.5s. Log signature: `mcp-stderr.log` shows the server starting and `ListToolsRequest` processed, but `agent.log` never logs `MCP: N tool(s) from N server(s)` — the join timed out and the agent snapshot was built without the tools. Fix: `mcp_discovery_timeout: 10`. Details + code paths in `references/mcp-discovery-race.md`.
- **`hermes -z` one-shot is unreliable for MCP proof.** Its agent tool-snapshot can be taken before background discovery lands; the model then reports "no mcp tools in toolset" and falls back to terminal hacks. This is a harness race, not a config failure. Use the interactive CLI or the gateway for live proof; use step 6 for deterministic registration proof.
- **`hermes mcp add` hangs without piped stdin** (interactive enable prompt).
- **Default profile config lives at `~/.hermes/config.yaml`**, not `~/.hermes/profiles/default/` — profile list loops that assume uniform paths silently miss it.
- **Tool count mismatch is normal:** protocol handlers (`list_resources`, `list_prompts`, `read_resource`, `get_prompt`) also surface as `mcp_*` tools, so the registration probe can show more tools than `mcp test` lists.
- **YAML rewrite must round-trip verify** (re-load, assert key present, `config check` exit 0) before reporting the profile wired.
- **Do not claim "connected to all profiles" from `mcp test` alone** — that is transport proof only. The registration probe (step 6) is what the agent runtime actually uses.
- **Liveness ≠ freshness.** Servers that cache state at process start (e.g. OKF's in-memory search index) go stale after new commits: `search`/`recent` miss the new content while `read` (live disk) still works. Diagnose by comparing server process start time vs the data's latest commit; remediate by respawning the process (new session or `/reload-mcp`) or an env-gated in-process refresh. Full recipe: `references/running-server-health-check.md`.

## Verification ladder (report all three, label each)

1. `mcp test` per profile → transport PASS
2. `discover_mcp_tools()` probe → registration PASS (tool names + connected status)
3. Interactive session with a forced tool call → live PASS (quote the tool-call result)

NOT_CLAIMING boundary: if only 1–2 are done, say which layer is unproven and whether running gateways still need `/reload-mcp`.

## Remote streamable-http transport (bearer-gated)

Same server, second socket. When the task is "expose this MCP server over HTTP / via a tunnel / in Docker" rather than "wire it to local profiles," add a streamable-http entry point **on top of** the stdio one — never instead of it.

1. **Transport switch, keep stdio the default.** At the bottom of `server.py`: if an env var (e.g. `MCP_TRANSPORT`) == `streamable-http`, call `mcp.run(transport="streamable-http", host=HOST, port=PORT)`; else `mcp.run()` (stdio). Never remove the stdio path — the local Hermes profiles depend on it, and a transport change that breaks stdio is a silent regression for every local profile.
2. **Bearer middleware + fail-closed + open /healthz.** Wrap the app in a starlette middleware: `GET /healthz` stays **open** (no auth) so the tunnel/proxy can liveness-check; every other route requires `Authorization: Bearer <token>`, wrong/missing → **401**. Critical: when no token env var is set, the gate must return **401 on /mcp** (fail-closed), not 200 — otherwise the endpoint can ship wide-open. The token is set at runtime from an env var, never committed.
3. **Raw-protocol smoke (ad-hoc).** `initialize` → grab the `Mcp-Session-Id` response header → send `notifications/initialized` → then `tools/list` and `tools/call`, **each carrying the `Mcp-Session-Id` header**. Follow-up requests without the session header get **400** (a protocol error, NOT 401 auth) — the classic false "auth is broken" diagnosis. Full recipe + the 400-vs-401 distinction in `references/streamable-http-remote.md`.
4. **Docker.** `python:3.12-slim` lacks `git` — any tool that shells out to git (e.g. an `okf__status` that runs `git rev-parse`) dies with `[Errno 2] No such file or directory: 'git'`; add `RUN apt-get install -y git`. Bind `HOST=0.0.0.0` in the image (so `docker -p` works); the tunnel/systemd path overrides to `127.0.0.1`. Poll `/healthz` until 200 before asserting — Docker opens the port mapping before the app finishes indexing, so a raw socket connect succeeds while the first HTTP request gets a connection reset.
5. **systemd deployment (loopback-only, token via mode-600 EnvironmentFile).** Unit pattern: `ExecStart=<venv-python> server.py` with `MCP_TRANSPORT=streamable-http HOST=127.0.0.1 PORT=<port>` and `EnvironmentFile=-/etc/<app>/app.env` (mode 600, root-only, generated by a script that assembles the key name from parts — see `bearer-token-via-shell-substitution` for the on-disk-corruption rule). Verify the live service with an 8-check suite: systemd active · `/healthz` 200 no-auth · `/mcp` no-auth 401 · wrong-auth 401 · correct-auth initialize+session · tools/list count · tools/call real tool → real data · `ss -ltn` shows `127.0.0.1:<port>` and NOT `0.0.0.0:<port>`. The last check is the security proof — a loopback service that accidentally binds 0.0.0.0 is on the LAN.
6. **Tool-name gotcha (live HTTP vs Hermes surface names).** The protocol tool name is the **FastMCP function name** (`def status()` → tool `status`), NOT the Hermes surface name (`mcp_okf_status`) nor the OKF doc name (`okf__status`). A `tools/call` with the surface name returns `{"isError":true,"text":"Unknown tool: okf__status"}`. Always confirm names via `tools/list` before asserting a call works.
7. **Cloudflare tunnel publication — credential scope wall (2026-08-20).** DNS CNAME (`okf.example.com` → `<tunnel-uuid>.cfargotunnel.com`, proxied) is doable with a Pages/DNS-scoped token (write + verify via API). Tunnel **ingress** is NOT: remote-managed tunnels keep their ingress in the Cloudflare dashboard, and a Pages/DNS token returns **401** on `GET /accounts/{a}/cfd_tunnel/{id}/configurations` and **403** on `POST /accounts/{a}/cfd_tunnel`. Probe both before promising the public step. When ingress can't be added, the public edge returns **404** on every path — distinct from your own service's 401 (no auth) / 200 (`/healthz`): a 404 from the edge means "tunnel up, no rule for this host," which is a clean, provable BLOCKED state, not a broken deployment. Surface exactly the one-line dashboard fix (Public Hostname → host → `http://localhost:<port>`) or ask for a token with `Account: Tunnel:Edit`. Also: `cloudflared run --token <jwt>` tokens are single-segment base64 (no dots) — decode with padding, keys are `a` (account), `t` (tunnel), `s` (secret).

NOT_CLAIMING for this slice: hosted CI, MCP Inspector, live tunnel proof, public exposure. Local container 6/6 + host streamable-http N/N is ad-hoc, not suite green.

## Support files

- `scripts/mcp_stdio_smoke.py` — generic JSON-RPC stdio smoke test (args: server path, python path, optional tool call).
- `references/streamable-http-remote.md` — streamable-http raw-protocol recipe (session-header / 400-vs-401 trap), bearer+fail-closed middleware, Docker pitfalls (git, HOST=0.0.0.0, startup race).
- `references/mcp-discovery-race.md` — discovery-timeout anatomy, log signatures, code paths, and why `-z` fails.
- `references/running-server-health-check.md` — liveness-vs-freshness health check for running servers (stale in-memory index diagnosis, process-age vs commit-age, remediation options, reporting shape).

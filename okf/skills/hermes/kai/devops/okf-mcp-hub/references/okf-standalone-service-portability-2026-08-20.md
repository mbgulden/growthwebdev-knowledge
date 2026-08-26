# OKF standalone service — portability session record (2026-08-20)

Michael's ask: "The OKF server needs to be portable and not attached to the orchestrator. What if the orchestrator goes down? The server needs to stay alive."

## Finding: the standalone service ALREADY existed
`/etc/systemd/system/okf-mcp.service` — active, parented by PID 1:

```ini
[Service]
Type=simple
User=root
EnvironmentFile=/etc/okf-mcp/mcp.env
ExecStart=/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python /home/ubuntu/work/okf-mcp-server/server.py
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
```

`/etc/okf-mcp/mcp.env` (mode 600 root-only): `MCP_TRANSPORT=streamable-http`, `HOST=127.0.0.1`, `PORT=8910`, `OKF_ROOT=/home/ubuntu/work/growthwebdev-knowledge`, `OKF_ALLOW_UPDATE=0`, `MCP_BEARER_TOKEN=*** `MCP_ALLOWED_HOSTS=127.0.0.1:*,localhost:*,[::1]:*,okf.growthwebdev.com`, `MCP_ALLOWED_ORIGINS=https://okf.growthwebdev.com`.

Live proof of independence: `hermes-gateway-orchestrator.service` was in `failed` state while `okf-mcp.service` served `/healthz` → 200. The orchestrator's live gateway process (3727933) is an orphan running outside systemd — flagged as the opposite failure mode (nothing respawns it).

## Gaps found + fixed this session
1. **Index freshness** — in-memory index only rebuilds at service start. Fix: `skill-hub-regen.sh` now runs `sudo systemctl restart okf-mcp.service` after each successful hub push (kai has passwordless sudo, verified non-interactive).
2. **Per-gateway stdio children** (5 observed) die with their gateway and duplicate the index. Fix path (in progress): wire profile clients to `http://127.0.0.1:8910/mcp` with bearer header; kai's client wiring was in progress at session cap.

## Wiring a profile client to the HTTP endpoint (schema verified from hermes_cli/mcp_config.py)

```yaml
mcp_servers:
  okf:
    enabled: true
    url: http://127.0.0.1:8910/mcp
    headers:
      Authorization: Bearer ${MCP_...EY}
```

- Token value → profile `~/.hermes/profiles/<p>/.env` line `MCP_OKF_API_KEY=*** env key convention is `MCP_` + NAME.upper() with `-`→`_` + `_API_KEY`).
- `hermes mcp add okf --url ... --auth header` does this interactively (it writes the same schema).
- `/reload-mcp` in-chat or new session picks it up; no gateway restart.
- Server-side: `/healthz` is open (no auth); everything else is bearer-gated via `hmac.compare_digest(request Authorization, "Bearer " + expected)`; fail-closed if no token configured.

## The 401 mystery (UNRESOLVED at session cap — exact next steps)
Symptom: `POST http://127.0.0.1:8910/mcp` initialize → `{"error":"unauthorized"}` even with the token from `/etc/okf-mcp/mcp.env`.

Diagnosis facts established:
- Token extraction via Python `sudo cat` + `split("=", 1)[1]` gives a 64-char token (healthy).
- The shell pipelines (`cut -d= -f2`, `sed 's/^MCP_BEARER_TOKEN=*** `tr`) ALL produced EMPTY strings (len=0, sha `e3b0c44298fc`) — the token contains special chars that break naive shell splitting. So every "token" I sent via inline shell was `Bearer ` (empty) → 401.
- The Python-only probe (urllib, token never in shell) STILL 401'd once — but that run used the env-file token while the service had been restarted 18:55; need to confirm live-process token vs file token by hash (`sudo cat /proc/<pid>/environ` vs env file) — the comparison script was written but not yet executed when the cap hit.

Next steps (in order):
1. Run the hash comparison (live env vs env file) via a Python script — never shell.
2. If they differ → `sudo systemctl restart okf-mcp.service` so the process picks up the file's token (or fix whichever is stale).
3. Re-probe `/mcp` initialize with the live token via Python/urllib → expect 200 + initialize response.
4. THEN write `MCP_OKF_API_KEY` to the profile `.env` (the earlier attempt wrote an EMPTY value — remove the `MCP_OKF_API_KEY=` line first: `sed -i '/^MCP_OKF_API_KEY=*** /home/ubuntu/.hermes/profiles/kai/.env`).
5. Patch `config.yaml` okf block to url+headers, `/reload-mcp`, verify with `mcp_okf_status` via the HTTP path.
6. Orchestrator-down drill: kill the orchestrator's stdio okf child → standalone still 200.

Durable rule: **credential-shaped strings must never pass through a shell pipeline.** `sudo cat` into a Python string, verify by hash, probe with urllib from a script file. Both the in-transit redactor AND bash quoting eat them.

## Collateral: shared-checkout branch-pointer race (2 incidents, same session)
- My drift commit landed on `feature/fred-okf-hde-guest-fleet-ops` (concurrent `git switch` mid-sequence).
- Fred/Ned's `909b505` landed inside my open PR #35.
Recovery: `git branch -f <their> d5deaa4` → safety ref `rescue/ned-gro4797-hde-909b505` → cherry-pick onto their branch (file-identical verified by `git rev-parse <sha>:<path>` on both) → push their branch (`a35bff1`) → rebuild mine from `origin/main` with 3 cherry-picks → `--force-with-lease` → PR clean (137 files, all in-lane). `git cherry-pick` has no `-q` flag. Full recipe: SKILL.md Phase-3 item 15.

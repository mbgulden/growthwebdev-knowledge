# Codex CLI as a standalone lane target — 2026-07-26

## Context

Michael clarified on 2026-07-26 that the Prismatic Engine `codex` lane
(also `agy`, by symmetry) must dispatch to the **standalone Codex CLI**
binary, NOT to a Hermes profile named `codex-*`. The CLI is the lane's
subprocess; the Hermes profiles (`codex-5-4`, `codex-5-5`) are debris
to be wiped from history.

This file is the source-of-truth reference for *how* to invoke Codex CLI
from a PE lane, what models exist on this host, and how to disambiguate
from Hermes's `openai-codex` provider. Verified live on 2026-07-26.

## Disambiguation (do not confuse)

| Term | What it is | Where it lives | Who invokes it |
|---|---|---|---|
| **Codex CLI** | Standalone `codex` binary | `/usr/bin/codex`, `~/.codex/` | Shell, PE lane, scripts |
| **Codex profile (Hermes)** | Hermes profile named `codex-*` | `~/.hermes/profiles/codex-*/` | `hermes -p codex-*` |
| **openai-codex provider (Hermes)** | OAuth-backed provider catalog | Hermes config | `hermes --provider openai-codex -m gpt-5` |
| **Codex lane (PE)** | Dispatch lane in `prismatic/lanes/codex.py` | `prismatic/lanes/` | PE dispatcher |

**The lane invokes the CLI, not the profile, not the provider.** The
Hermes `openai-codex` provider catalog is consulted only to *choose* the
model slug that the CLI then sends to its own (separate) OpenAI account.

## Live facts on this host (2026-07-26)

```text
binary:         /usr/bin/codex (also /bin/codex via npm-managed path)
package root:   /usr/lib/node_modules/@openai/codex
version:        codex-cli 0.132.0
update target:  0.145.0 available (`npm update codex`)
auth:           NOT LOGGED IN — `codex login` required before any exec
                `codex doctor` reports: `✗ auth no Codex credentials`
state dir:      ~/.codex/  (config.toml, state_5.sqlite, logs_2.sqlite,
                sessions/, memories/, skills/, tmp/)
web search:     feature `search_tool` REMOVED; use `--search` flag
                for live web search via Responses API
sandbox:        read-only | workspace-write | danger-full-access
                (linux=bubblewrap/landlock default)
multi-agent:    feature `multi_agent` STABLE,
                `multi_agent_v2` UNDER DEVELOPMENT,
                `enable_fanout` UNDER DEVELOPMENT
MCP server:     `codex mcp-server` exposes Codex as an MCP server over
                stdio (for upstream Hermes/Claude integration)
doctor:         `codex doctor` reports auth, runtime, install, search,
                terminal, state health in one shot
```

## Canonical PE-lane invocation

The lane should always invoke `codex exec` (non-interactive) with JSON
event streaming. TUI mode (`codex` with no subcommand) is **not**
appropriate for unattended dispatch.

```bash
codex exec \
  --json \
  --ephemeral \
  --skip-git-repo-check \
  --model gpt-5 \
  --sandbox workspace-write \
  --add-dir /workspace/<id> \
  -C /workspace/<id> \
  -o /tmp/lane/<issue_id>/last.md \
  -c 'shell_environment_policy.inherit=all' \
  --ask-for-approval never \
  "<issue_title>

   <issue_body>

   Acceptance criteria:
   - <copied from issue>

   Return the final summary as the last assistant message."
```

### Why these flags

- `--json` — stream events as JSONL for PE event-bus ingestion.
- `--ephemeral` — DO NOT persist rollouts to `~/.codex/sessions/`
  (currently 252 active rollouts = 7.48 MB; lane dispatches would fill it).
- `--skip-git-repo-check` — lane runs in non-git workspaces.
- `--sandbox workspace-write` — allow writes inside `-C` dir; deny elsewhere.
- `-C <dir>` + `--add-dir <dir>` — primary workspace + writable peers.
- `-o <path>` — final assistant message lands at known path.
- `-c 'shell_environment_policy.inherit=all'` — inherit PE env (provider keys).
- `--ask-for-approval never` — unattended; the lane *is* the approver.

## Failure-mode map

| Symptom | Likely cause | Lane response |
|---|---|---|
| `401 Unauthorized` on `wss://api.openai.com/v1/responses` | Codex not logged in | Run `codex login`, then redispatch. Lane should pre-flight with `codex doctor`. |
| `Reconnecting... N/5` then `turn.failed` | Auth or rate-limit | Exponential backoff; surface to Linear as `dispatch:blocked`. |
| `Not inside a trusted directory` | `~/.codex/config.toml` missing `trust_level` for the workspace dir | Add `[projects."<path>"] trust_level = "trusted"` to config.toml OR pass `--skip-git-repo-check`. |
| `Reading additional input from stdin...` hangs | Stdin is a TTY/pipe and no prompt was provided | Always pass prompt as arg; if piping, use `< /dev/null`. |
| WebSocket fail, HTTPS fallback succeeds | Network/proxy blocking WS | Lane must tolerate; `codex doctor` reports `⚠ websocket`. |
| `danger-full-access` blocked by approval policy | Sandbox policy + approval mismatch | Use `--dangerously-bypass-approvals-and-sandbox` ONLY in externally-sandboxed environments; never from inside PE. |

## Model choice

| Slug | Family | When to use |
|---|---|---|
| `gpt-5` | GPT-5 baseline | Default for code generation; balanced speed/quality. **PE lane default.** |
| `gpt-5-mini` | GPT-5 mini | Cheaper fallback for boilerplate/scaffolding. |
| `gpt-5.4-mini` | older mini tier | Legacy alias — avoid unless codex provider returns it. |
| `gpt-5.5` | GPT-5.5 | Higher quality; reserved for complex refactors. |
| `gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna` | GPT-5.6 variants | Use when Hermes Codex OAuth smoke confirms availability; otherwise fall back to `gpt-5`. |
| `o3` / `o4-mini` | Reasoning models | For code review only (`codex review`); NOT for `codex exec` generation. |
| `--oss` | Open-source provider | Use with `--local-provider ollama` or `lmstudio` for offline Codex runs. **Not** for production lane today. |

### Recommended lane profile (config.toml)

```toml
[profiles."pe-codex"]
model = "gpt-5"
model_reasoning_effort = "medium"
sandbox = "workspace-write"
ask_for_approval = "never"
disable_response_storage = true   # do not retain prompts on OpenAI side
```

Then invoke as `codex exec -p pe-codex ...` so the lane doesn't need to
pass `--model` every time.

## Concurrency model

Each `codex exec` is a separate OS process with:

- its own sandbox (bubblewrap by default on Linux),
- its own session file (unless `--ephemeral`),
- its own rate-limit bucket against `api.openai.com`.

**Implications for the PE lane:**

1. **Start with 1 parallel invocation.** We don't yet know how many
   concurrent Codex CLI processes the openai-codex OAuth bucket tolerates
   before rate-limiting. The lane should serialize by default and only
   fan-out after a measured trial.
2. **Use `--ephemeral` for lane dispatches.** Persistent rollouts in
   `~/.codex/sessions/` add up fast and pollute the state DB.
3. **Stream `--json` events into the PE event bus.** Don't wait for
   completion; ingest `thread.started`, `turn.started`, `item.completed`,
   `turn.completed` events as they arrive so PE observability can
   correlate with Linear dispatch.
4. **Pre-flight with `codex doctor`.** A cheap `codex doctor` call (no
   model invocation) catches the "not logged in" / "websocket down"
   cases before we burn a turn.
5. **Fan-out (future):** when ready, use `multi_agent` feature flag
   (currently STABLE) with `--enable multi_agent` to let Codex itself
   delegate subtasks. **Not in scope for the initial PE-LANES-EXT epic.**

## Profile wipe (Michael's 2026-07-26 decision)

Wipe these Hermes profiles from disk and from OKF/Linear references:

| Profile | Model | Alias script |
|---|---|---|
| `agy` | (none) | (none) |
| `codex-5-4` | `gpt-5.4-mini` (openai-codex) | `~/.hermes/profiles/fred/home/.local/bin/codex-5-4` |
| `codex-5-5` | `gpt-5.4-mini` (openai-codex) | `~/.hermes/profiles/fred/home/.local/bin/codex-5-5` |

Acceptance:

```bash
hermes profile list | grep -E "agy|codex"
# Returns only the active `george` profile's model route, not
# separate `agy` / `codex-*` profiles.
ls ~/.hermes/profiles/{agy,codex-5-4,codex-5-5} 2>&1
# "No such file or directory" for all three.
which codex   # /usr/bin/codex
which agy     # /home/ubuntu/.local/bin/agy
```

## Pitfalls

- **Do not use TUI mode (`codex` with no subcommand) for unattended
  dispatch.** Always use `codex exec`.
- **Do not use `codex review` for code generation.** It is read-only
  and output-shaped for PR review comments.
- **Do not assume the workspace is trusted.** Pass `--skip-git-repo-check`
  OR pre-write `trust_level` to `~/.codex/config.toml`. Lanes that touch
  many workspaces should add to config.toml at dispatch time.
- **Do not forget `--ephemeral`.** Persistent rollouts bloat the state
  DB and leak context to later sessions.
- **Do not bypass the approval policy from inside PE.** Use
  `workspace-write` + `--ask-for-approval never`. Reserve
  `--dangerously-bypass-approvals-and-sandbox` for outer-sandbox runners.
- **Do not confuse `openai-codex` provider (Hermes-side) with Codex CLI.**
  Different auth, different state, different model catalog refresh path.
- **Do not fan-out without measuring.** 1-parallel by default; scale
  after observing rate-limit / sandbox collisions against the
  `api.openai.com` endpoint under real auth.
- **Codex CLI is not logged in on this host as of 2026-07-26.** Until
  someone runs `codex login` against the correct ChatGPT account, no
  live `codex exec` will succeed. The lane must pre-flight with
  `codex doctor` and surface `dispatch:blocked` on auth failure instead
  of silently retrying.

## Related skills

- `agy-autopilot-governance` — the AGY-side mirror (CLI invocation,
  preflight, packet contract, one-task discipline).
- `linear-backlog-routing-governance` — how blocked dispatches surface.
- `prismatic-core-skill-distribution-ops` — when the lane contract
  ships new skills/profiles.

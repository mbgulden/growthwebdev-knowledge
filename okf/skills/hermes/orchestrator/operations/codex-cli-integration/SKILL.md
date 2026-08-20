---
name: codex-cli-integration
description: Operate and integrate the standalone Codex CLI (`/usr/bin/codex`, codex-cli ≥ 0.132.0) as an external agent harness target for Prismatic Engine lanes. Captures the canonical argv shape, service-HOME auth boundary, the Hermes-profile separation discipline, parallel-cap-1 convention, and the verification packet for capability probes. Use when PE needs to dispatch work to Codex CLI from a lane, profile, or dispatch script.
tags: [codex, codex-cli, openai-codex, hermes-profile-separation, argv, service-home, harness, cap-1, prismatic-engine, pe-lane]
---

# Codex CLI Integration

Use this skill when Prismatic Engine (or any other orchestrator) needs to invoke the **standalone Codex CLI** as an agent harness, distinct from any Hermes `codex-*` profile.

The skill is built around the lessons learned integrating Codex CLI 0.132.0 against Prismatic Engine in July 2026. Future versions of the CLI may shift argv surface; always verify against `codex exec --help` before relying on a flag.

## Boundary: standalone CLI vs Hermes profile

| Term | What it is | Where it lives | Invoked by |
|---|---|---|---|
| **Codex CLI** | Standalone `codex` binary | `/usr/bin/codex`, `~/.codex/` | Shell, PE lane, scripts |
| **Codex profile (Hermes)** | Hermes profile named `codex-*` | `~/.hermes/profiles/codex-*/` | `hermes -p codex-*` |
| **openai-codex provider (Hermes)** | OAuth-backed provider catalog inside Hermes | Hermes config | `hermes --provider openai-codex -m <model>` |
| **Codex lane (PE)** | Dispatch lane in `prismatic/lanes/codex.py` | `prismatic/lanes/` | PE dispatcher |

The lane invokes the **CLI**, not a Hermes profile, not an internal provider catalog. The provider catalog is consulted only to *choose* the model slug that the CLI then sends to its own (separate) OpenAI account.

The Hermes profiles named `codex-*` are deprecated/retired. Do not introduce new `codex-*` profiles; if one already exists, retire per the protocol in `plan-reconciliation-after-peer-review`. The AGY equivalents (`~/.local/bin/agy` vs `~/.hermes/profiles/agy/`) follow the same rule: invoke the CLI, not the profile.

## When to use

- A Prismatic Engine lane needs to dispatch work to Codex (code generation, scaffolding, drafts for review).
- A script or cron needs to invoke `codex exec` with a stable argv.
- You're debugging a `codex` integration that produces 401s, "Not inside a trusted directory," or hangs on stdin.
- You're deciding whether to add a new Hermes `codex-*` profile, or to fix the lane to invoke the CLI directly.
- You need the canonical argv shape for a feature-flag rollback or a parallel-cap-N discussion.

## When NOT to use

- You are operating Codex through the Hermes `george` or other profile — defer to `hermes-agent` and `hermes-model-provider-ops`.
- You are operating Codex through the `openai-codex` provider catalog inside Hermes — defer to `hermes-model-provider-ops`.
- You need to authenticate Codex — that is a separate operator action (`codex login`) that requires Michael's explicit authorization. Do NOT include login as part of any integration.

## Operating principles

1. **Build argv as a list, not a string.** The Codex CLI 0.132.0 parser is positional and strict. Building argv as a string and `.split()`-ing it loses quoting and breaks on prompts containing spaces. Use `argv = [CODEX, "-a", "never", "exec", ...]` and pass it to `subprocess.run(argv, ...)`.
2. **`-a`/`--ask-for-approval` is global; it must precede `exec`.** `codex exec --ask-for-approval never ...` fails argument parsing on 0.132.0. Always: `codex -a never exec ...`. **Verified twice (2026-07-26 plan-reconciliation and 2026-07-27 deploy workflow session):** if you build argv as `[CODEX, "exec", "-a", "never", ...]` it rejects with a "unexpected argument" or positional-conflict error, not a graceful failure. The fix is positional, not syntactic.
3. **Auth resolves under the service HOME, not `~/.codex/auth.json`.** A service running under `/home/ubuntu/.hermes/profiles/<svc>/home/` will resolve auth at `/home/ubuntu/.hermes/profiles/<svc>/home/.codex/auth.json`, NOT a universal `~/.codex/auth.json`. Verify with `codex doctor --json` and read the `auth.credentials.details.auth file` field.
4. **Authentication is a separately approved operator action.** Do NOT include `codex login`, account choice, or credential provisioning in any code path. No code may copy Hermes credentials into another profile/service. Operators perform `codex login` per the auth-ownership decision (usually a dedicated PE service account).
5. **`codex exec` is the unattended path; TUI mode is not.** `codex` with no subcommand drops into TUI and is inappropriate for unattended dispatch. Always invoke `codex exec` (alias `e`) for one-shot.
6. **Each `codex exec` is a separate OS process with its own sandbox and rate-limit bucket.** Default to cap-1-parallel. Fan-out requires independent rate-limit, sandbox-collision, exact-run, and recovery evidence.
7. **Do not default to `--skip-git-repo-check` for repository tasks.** Git binding is part of admission. Set `--skip-git-repo-check` only for ad-hoc scripts against non-git workspaces.
8. **`--ephemeral` is allowed only if the caller durably retains** the JSONL event stream, terminal result, command manifest, process identity, and output digests. Without durable retention, drop `--ephemeral` and let Codex persist rollouts to `~/.codex/sessions/`.
9. **Never use `--dangerously-bypass-approvals-and-sandbox` from inside PE.** Only externally-sandboxed environments should bypass. PE is not externally sandboxed.
10. **CLI string acceptance is not inference availability proof.** `codex --model gpt-5` may accept the slug without actually being able to run it. Use a live capability probe (see `scripts/probe-codex-capability.sh`) before adopting a model for production lanes.

## Canonical argv (verified 2026-07-27 against codex-cli 0.132.0)

```bash
/usr/bin/codex
-a never
exec
--json
--ephemeral
--model <capability-proven-model>
--sandbox workspace-write
--add-dir <explicit-whitelisted-path>
-C <exact-clean-worktree>
-o <durable-run-dir>/last-message.md
<prompt>
```

- `CODEX` defaults to `/usr/bin/codex` (also `/bin/codex` via npm-managed path).
- `-a never` is the global `--ask-for-approval=never` flag. **Must precede `exec`.**
- `--json` streams events as JSONL for downstream ingestion.
- `--ephemeral` skips persistence to `~/.codex/sessions/`; PE must durably retain output if this is set.
- `--model` accepts the capability-proven slug (e.g., `gpt-5`, `gpt-5-mini`, `gpt-5.5`, `gpt-5.6-sol/terra/luna` if probe-OK).
- `--sandbox workspace-write` allows writes inside `-C`; denies elsewhere. Use `--sandbox read-only` for analysis-only.
- `--add-dir <path>` adds explicit whitelisted writable directories alongside `-C`. No glob; no relative paths.
- `-C <path>` is the exact clean worktree. PE should resolve the path, not accept it from the caller.
- `-o <path>` writes the final assistant message to `<path>`. PE should derive this from a durable run dir per dispatch.
- `<prompt>` is the issue body + acceptance criteria. Pass as argv (preferred) or via stdin with `< /dev/null`.

## Live CLI facts (verified 2026-07-27)

```text
binary:           /usr/bin/codex (also /bin/codex via npm-managed path)
package root:     /usr/lib/node_modules/@openai/codex
version:          codex-cli 0.132.0
update target:    0.145.0 available (`npm update codex`)
auth:             NOT LOGGED IN on this host (verified `codex doctor --json`)
auth file:        /home/ubuntu/.hermes/profiles/fred/home/.codex/auth.json (under service HOME)
state dir:        ~/.codex/  (config.toml, state_5.sqlite, logs_2.sqlite, sessions/, memories/, skills/, tmp/)
web search:       feature search_tool REMOVED; use --search flag (live web search via Responses API)
sandbox:          read-only | workspace-write | danger-full-access (linux=bubblewrap/landlock)
multi-agent:      multi_agent STABLE, multi_agent_v2 UNDER DEVELOPMENT, enable_fanout UNDER DEVELOPMENT
MCP server:       codex mcp-server exposes Codex as an MCP server over stdio
doctor:           codex doctor --json reports auth, runtime, install, search, terminal, state health
```

## Failure-mode map (verified 2026-07-27)

| Symptom | Likely cause | Lane response |
|---|---|---|
| `401 Unauthorized` on `wss://api.openai.com/v1/responses` | Codex not logged in | Run `codex doctor --json`. If `auth.credentials.status != ok`, refuse dispatch and surface `dispatch:blocked` + `agent:needs-human-review` to Linear. Do NOT attempt login yourself. |
| `Reconnecting... N/5` then `turn.failed` | Auth or rate limit | Exponential backoff with cap; surface to Linear as `dispatch:blocked`. |
| `Not inside a trusted directory` | `~/.codex/config.toml` missing `trust_level` for the workspace dir | Add `[projects."<path>"] trust_level = "trusted"` to config.toml OR pass `--skip-git-repo-check` (lane MUST NOT default for repo tasks). |
| `Reading additional input from stdin...` hangs | Stdin is a TTY/pipe and no prompt was provided | Always pass prompt as argv; if piping, use `< /dev/null`. |
| WebSocket fail, HTTPS fallback succeeds | Network/proxy blocking WS | Lane must tolerate; `codex doctor --json` reports `⚠ websocket`. |
| `danger-full-access` blocked by approval policy | Sandbox policy + approval mismatch | Use `--dangerously-bypass-approvals-and-sandbox` ONLY in externally-sandboxed environments. Never from inside PE. |
| `unexpected argument` after `-a never exec` — i.e., `-a` placed after `exec` | Reviewer-corrected argv bug | Build argv as `[CODEX, "-a", "never", "exec", ...]`. The parser requires the global `-a` BEFORE the `exec` subcommand. |

## Feature flag / rollout policy

A config flip stops new side effects; it does NOT roll back already-mutated state, in-flight processes, or safety invariants. For Codex lanes specifically:

| Rollout control | Allowed | Not allowed |
|---|---|---|
| Enrollment | disabled-by-default + cap 1 + capability-proven model | bypassing admission/run receipts or sandbox policy |
| Capability gating | per-model probe before adoption | assuming CLI acceptance implies availability |
| Sandbox policy | `read-only` for analysis; `workspace-write` for coding; explicit whitelist for `--add-dir` | `danger-full-access` from inside PE |
| Approval policy | `-a never` only after admission/dispatch approval chain | `--dangerously-bypass-approvals-and-sandbox` from PE |
| Auth | operator runs `codex login` for a dedicated PE service account | reusing/copying Hermes profile credentials by code |
| Fan-out | measured rate-limit/sandbox-collision trial, then cap-N | parallel dispatch without evidence |

## Verification protocol

Before declaring a Codex integration slice done, run the focused verifier in `scripts/verify-codex-integration.sh`:

```bash
# 1. Confirm binary + version
which codex
codex --version

# 2. Confirm doctor JSON parses and auth boundary
codex doctor --json | jq '.checks.auth.credentials.status,.checks.app_server.status'

# 3. Confirm argv ordering with the canonical preflight
codex -a never exec --help
# (this confirms `-a` is global before `exec`)

# 4. Capability probe for the target model (post-auth only)
codex exec --json --ephemeral --model <candidate-model> \
  --sandbox read-only \
  -C /tmp/codex-probe-<ts> \
  -o /tmp/codex-probe-<ts>/last.md \
  "Reply with exactly: CODEX_MODEL_OK" < /dev/null

# 5. Confirm stdout JSONL contains turn.completed (or turn.failed with clear error)
```

Report as **ad-hoc targeted verification, not suite green** unless the canonical suite covers the integration.

## Pitfalls

- **Confusing the standalone CLI with a Hermes `codex-*` profile.** They share a name and a provider catalog; they are different processes, different auth files, different config roots, different rate-limit buckets. Never let code reference both interchangeably.
- **Building argv as a string.** `argv = "codex exec ..."` then `.split()` drops quoting and breaks on prompts with spaces or shell metas. Always use a list.
- **Placing `-a` after `exec`.** Fails parsing on 0.132.0 with a positional-argument error (not a graceful "unknown flag" rejection). Always `[CODEX, "-a", "never", "exec", ...]`. Reviewer correction 2026-07-26 verified and re-verified 2026-07-27 during the Sentinel ITAD site-readiness work — do not paper over it with `--ask-for-approval` after `exec`.
- **Defaulting `--skip-git-repo-check` "because we're not in a git repo."** This bypasses Git identity in admission. Use only when the task explicitly authorizes it.
- **Trusting CLI string acceptance as availability proof.** Always run a capability probe before adopting a model for production lanes.
- **Including `codex login` in any code path.** Login is an operator action requiring Michael's explicit authorization.
- **Copying Hermes credentials into a service HOME.** Each service account has its own auth file. The lane is responsible for its own auth boundary, not credential inheritance.
- **Setting `--ephemeral` without durable retention.** Without JSONL + terminal + manifest + process-identity + digest retention, ephemeral dispatches are unrecoverable.
- **Adding a `codex-*` Hermes profile to "fix" a CLI integration.** Profiles are retired. Fix the lane to invoke the CLI correctly.
- **Using `--dangerously-bypass-approvals-and-sandbox` inside PE.** Only externally-sandboxed environments qualify. PE is not.

## Companion skills

- `plan-reconciliation-after-peer-review` — when a reviewer hands you corrections, including "Codex argv is wrong" or "use the CLI, not the profile." The reconciliation skill teaches evidence-first honoring of every correction.
- `hermes-agent` and `hermes-model-provider-ops` — for operating Codex through Hermes profiles or the openai-codex provider catalog (the other two paths, distinct from this skill's CLI path).
- `linear-handoff-build-out` — when packaging Codex-lane tasks under PE parents (e.g., GRO-4262 → PE-CODEX-LANE-01/02/03) with seven-field descriptions and the Distributed-Execution Header.

## References

- `references/codex-argv-canonical-0.132.md` — verbatim argv shape with line-by-line rationale; useful as a clipboard when reviewing a lane that builds argv.
- `references/codex-service-home-auth.md` — how to verify the auth-file path under the service HOME before any auth-related decision.
- `references/codex-cap1-fanout-evidence.md` — the evidence checklist required to bump from cap-1 to cap-N.

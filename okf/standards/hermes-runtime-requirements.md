---
type: Standards
title: Hermes Agent Runtime Requirements — Minimum-Viable Surface for Linear Work
description: Standard for the minimum runtime surface Fred (orchestrator) needs to do Linear work on a clean machine. Codified in `~/.hermes/profiles/orchestrator/RUNTIME_REQUIREMENTS.md` and asserted at session start by `scripts/assert_runtime.sh`. Anything beyond this minimum is an optional accelerator, not a dependency. The verification is "produce a verified Linear response from a clean machine in under five minutes" — currently measured at ~1 second on this host.
resource: okf/standards/hermes-runtime-requirements.md
tags: [standards, hermes, runtime, linear, deployment, clean-machine, fast-start]
timestamp: 2026-07-29T03:55:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-runtime-requirements.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Runtime Requirements — Minimum-Viable Surface for Linear Work

## Purpose

The gap is: most routing and governance scripts assume an executor with the live Linear OAuth token, AGY, the user-systemd dispatcher, etc. Michael is one reboot or one machine swap away from being a passenger.

This standard closes that gap by:

1. **Identifying the minimum-viable runtime surface** — a single Linear credential, a single working workdir, a hermes binary, a Telegram adapter (if in scope), and a model credential.
2. **Codifying it in `~/.hermes/profiles/orchestrator/RUNTIME_REQUIREMENTS.md`** — a single file that future-self or a clean-machine installer can read.
3. **Asserting it at session start** via `scripts/assert_runtime.sh` — a check that fails loudly if anything is missing.

The verification is: "I can produce a verified Linear response from a clean machine in under five minutes." **Currently measured at ~1 second on this host (2026-07-29).**

## What this standard defines

### The minimum-viable surface (in order of dependency)

1. **Hermes binary on `$PATH`** — the CLI; without this, no tool can be invoked.
2. **`HERMES_HOME` env var** — points at the shared profile root; default `~/.hermes`.
3. **Profile directory at `$HERMES_HOME/profiles/$HERMES_PROFILE/`** with at minimum:
   - `config.yaml` (model + provider + Linear preferences)
   - `.env` (secrets)
   - `state/current.json` (handoff file; auto-created on first write)
4. **One Linear credential** — `LINEAR_API_KEY` (raw API key, preferred) or `LINEAR_OAUTH_CLIENT_ID` + `LINEAR_OAUTH_CLIENT_SECRET` (OAuth).
5. **One model credential** — matching `config.yaml`'s `model.provider`. On this host: `OPENROUTER_API_KEY` (for openai-codex) or `MINIMAX_API_KEY` (for minimax).
6. **Telegram adapter** (only if Telegram is in scope) — `TELEGRAM_BOT_TOKEN` + `TELEGRAM_HOME_CHANNEL`.

### What is NOT minimum (the negative scope)

- 53 of the 54 .env keys defined today (Cloudflare × 3 zones, PVE6 VM, Jules, Cal.com, etc.) — those are per-project accelerators
- 70 of the 76 config.yaml top-level keys — most are display/preferences/optional features
- Cron jobs (per-machine, not per-profile)
- Per-profile skills (loaded on demand)
- AGY CLI (only for AGY dispatch; not needed for Linear queries/writes)
- Most platform adapters (Discord, Slack, Mattermost, Matrix, WhatsApp)

### The assertion script

`scripts/assert_runtime.sh` (sibling file under `~/.hermes/profiles/orchestrator/scripts/`) runs the 5 minimum checks and exits 0 on PASS, 1 on FAIL. Has `--json` for machine-readable output and `--strict` to also fail on warnings.

**Current state on this host (2026-07-29):**

```
[PASS] hermes binary on PATH (version: Hermes Agent v0.17.0 (2026.6.19))
[PASS] HERMES_HOME=/home/ubuntu/.hermes (profiles/ exists)
[PASS] orchestrator/config.yaml exists
[PASS] orchestrator/.env exists
[PASS] LINEAR_API_KEY is set
[WARN] Telegram adapter not asserted (HERMES_PLATFORM != telegram; CLI mode or unknown)
[FAIL] model: MiniMax-M3 via minimax but MINIMAX_API_KEY is empty
```

The single FAIL is a real config bug worth flagging: the orchestrator's `config.yaml` says `provider: minimax` but `MINIMAX_API_KEY` is empty in this shell's env. Either the config should switch to `openai-codex` (the actual provider in use per `hermes profile list`) or the env needs `MINIMAX_API_KEY` set.

### The verification recipe (5 minutes from clean machine)

```bash
# 1. Install hermes (1 minute if pre-built binary)
curl -L -o /usr/local/bin/hermes https://github.com/.../hermes-binary
chmod +x /usr/local/bin/hermes

# 2. Set env (1 minute)
export HERMES_HOME=~/.hermes
export LINEAR_API_KEY=lin_api_...
export OPENROUTER_API_KEY=sk-or-...   # or whatever model provider requires

# 3. Confirm profile tree (1 minute)
test -d $HERMES_HOME/profiles/orchestrator || mkdir -p $HERMES_HOME/profiles/orchestrator
# Write a minimal config.yaml from the template in RUNTIME_REQUIREMENTS.md

# 4. Run the assertion (30 seconds)
bash $HERMES_HOME/profiles/orchestrator/scripts/assert_runtime.sh

# 5. Live Linear probe (30 seconds)
curl -sSf -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ viewer { id name email } }"}' \
  https://api.linear.app/graphql
```

**Verified 2026-07-29:** end-to-end probe completed in 1.069 seconds from a warm shell, expected to be similar from a cold shell once the env is sourced.

## What this standard explicitly does NOT cover

- The session-state-handoff primitive (gap #1) — the cold-start handoff is a separate concern.
- The proactive-execution discipline (gap #2) — turn-level behavior, not runtime surface.
- The projector-aware discipline (gap #3) — reply shape, not runtime.
- Other profiles' runtime surfaces (Kai, Ned, etc.) — they have their own profile trees and may have different minimums. The pattern is the same; the specific credential list may differ.

## Adoption status (as of 2026-07-29)

- `~/.hermes/profiles/orchestrator/RUNTIME_REQUIREMENTS.md` ships (10,489 bytes, all 7 sections present).
- `~/.hermes/profiles/orchestrator/scripts/assert_runtime.sh` ships (6,655 bytes, 5 minimum checks, JSON + strict modes).
- 5/6 minimum checks pass on this host. The 1 failure (missing `MINIMAX_API_KEY`) is a real config bug worth fixing separately.
- End-to-end Linear probe verified in 1.069 seconds (well under the 5-minute threshold).

## Honest lessons from the build

- **Most of `.env` is not runtime.** 53 of 54 keys are optional accelerators. The single required key for Linear work is `LINEAR_API_KEY` (or OAuth pair). Everything else is per-project.
- **Most of `config.yaml` is not runtime either.** 70 of 76 top-level keys are display/preferences/optional. The required minimum is `agent.max_turns`, `model.default`, `model.provider`, and the matching `providers.*` block.
- **The hermes binary is the silent dependency.** If the binary is missing or on the wrong PATH, nothing else matters. The assertion script's check 1 catches this; future-self should run it before chasing other failures.
- **HERMES_HOME may be a per-profile nested path.** A naive assertion script double-counts `/profiles/`. The fix: detect `*/profiles/*` in the env var and strip the trailing profile before computing paths.
- **A real config bug surfaced.** The orchestrator says it uses `minimax` but `MINIMAX_API_KEY` is empty. Either the config is wrong (should be `openai-codex` like the actual model route) or the env is wrong. Worth fixing as a follow-up, separate from gap-#4 closure.

## Related work

- `~/.hermes/profiles/orchestrator/RUNTIME_REQUIREMENTS.md` — the canonical requirement document
- `~/.hermes/profiles/orchestrator/scripts/assert_runtime.sh` — the assertion script
- `okf/standards/hermes-session-handoff-discipline.md` (gap #1)
- `okf/standards/hermes-proactive-execution-discipline.md` (gap #2)
- `okf/standards/hermes-projector-aware-communication-discipline.md` (gap #3)
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` — full session report

---
type: Standards
title: Hermes Agent Session-Handoff Discipline — Cross-Profile State Continuity
description: Standard for the per-profile `state/current.json` handoff file that bridges durable memory and source-of-truth Linear tasks. Defines the JSON schema, write cadence, cold-start integration, and adoption mechanism so every Hermes agent (orchestrator, fred, george, kai, ned, autobot, next-step, and future profiles) reads a current session's state on cold start instead of re-deriving context. Authoritative reference: the `session-state-handoff` skill at `~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/`.
resource: okf/standards/hermes-session-handoff-discipline.md
tags: [standards, hermes, session-handoff, cold-start, cross-agent, continuity]
timestamp: 2026-07-29T02:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-session-handoff-discipline.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Agent Session-Handoff Discipline

## Purpose

Every Hermes agent session should read the previous session's state on cold start instead of re-deriving context. The handoff file is the bridge between durable-but-slow memory and source-of-truth-but-expensive Linear. The gap is "cold start greets with where we left off, not what can I help with."

## What this standard defines

- **The handoff file** at `~/.hermes/profiles/<profile>/state/current.json` (plus `archive/` for one-step history).
- **The JSON schema** (1.0.0) for the file: required fields, allowed enums, and field semantics. See the canonical schema at `~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/templates/handoff.schema.json`.
- **Write cadence**: at the end of every substantive turn (any tool call that changed external state), and at session end. The CLI helper is `handoff.py write --from-stdin --profile <name>`.
- **Cold-start integration**: Pattern A via `prefill_messages_file` (active, dormant-correct on Hermes 0.17.0), Pattern B via plugin `pre_llm_call` (deferred, blocked on [hermes-agent#2817](https://github.com/NousResearch/hermes-agent/issues/2817)).
- **Adoption mechanism**: `_adopt_shared_skills.py` symlinks the canonical orchestrator source into every running profile's `skills/agent-operations/` directory. Symlinks keep a single source of truth — any future edit propagates to every profile.

## What this standard explicitly does NOT cover

- The session-end `write_and_wire.py` step is implementation, not a normative rule. The norm is: end every substantive turn with a handoff write.
- The `proactive-execution-discipline` skill is a separate concern (turn-level discipline) and lives at `okf/standards/hermes-proactive-execution-discipline.md` (or the same standards index).
- The pattern of probing every documented Hermes mechanism with a unique marker phrase is in [`okf/standards/hermes-mechanism-probe-recipe.md`](./hermes-mechanism-probe-recipe.md).

## How to adopt on a new or existing profile

```bash
# 1. Seed the handoff
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py \
  init --profile <new> --agent <new>

# 2. Wire Pattern A (generates prefill JSON + config key)
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py \
  wire --profile <new>

# 3. Adopt across every running profile (idempotent, has hard guards)
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/_adopt_shared_skills.py --all-running

# 4. Verify
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py \
  status --all
```

## Critical findings (2026-07-27)

1. **In Hermes 0.17.0, three documented cold-start mechanisms are declared but not loaded:**
   - `pre_llm_call` plugin hook (defined but no call site in the agent core)
   - `prefill_messages_file` config key (defined in `config.py:2055` but no code path reads the file and passes messages to the agent)
   - `telegram.channel_prompts` (defined in schema but no runtime reader)
2. **The mechanism is dormant, not broken.** The wiring is correct; the runtime is missing the loaders. When upstream Hermes ships the fix, the wiring activates automatically with no code change.
3. **The probe recipe is the durable verification tool.** Inject a unique marker phrase (e.g. `BANANA_PREFILL_PROBE_98271`) into the JSON, ask the model to recall it, confirm the model sees it. If it cannot, the mechanism is dormant.

## Hard guards in the adoption helper

`_adopt_shared_skills.py` refuses to:
- Adopt into the source profile (orchestrator). Adopting into the source creates a self-referencing symlink that destroys the canonical source.
- Replace a non-empty directory with a symlink (without `--force`). Backups go to `state/adopt-backups/<profile>/<skill>-<timestamp>`.

These guards exist because the 2026-07-27 adoption bug destroyed both canonical sources through a self-referencing symlink loop. The guards prevent recurrence.

## Related work

- `okf/standards/hermes-proactive-execution-discipline.md` — turn-level discipline, weekly counter.
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` (proposed) — full session report covering gap #1 (cold-start greeting) and gap #2 (proactive execution), four pins, and the adoption bug.
- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-COLD-START-WORKAROUND-PENDING.md` — pin documenting the dormant mechanism state.
- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-PATTERN-B-BLOCKED-2817.md` — pin documenting Pattern B research and the upstream blocker.

## Verification

For each adopted profile, the recipe is:
1. `hermes skills list --profile <name>` shows `session-state-handoff` and `proactive-execution-discipline` (both enabled).
2. `wire_cold_start.py status --profile <name>` shows `prefill_exists: true` and `config_prefill_setting: /home/ubuntu/.hermes/profiles/<name>/state/prefill_messages.json`.
3. **Live model probe** (when the upstream loader is fixed): inject a marker phrase, ask the model to recall it. If it can, the mechanism is live.

Until the upstream fix lands, "wired" means "files exist and config keys are set." It does NOT mean "the model sees the prefill on every turn." Be precise.

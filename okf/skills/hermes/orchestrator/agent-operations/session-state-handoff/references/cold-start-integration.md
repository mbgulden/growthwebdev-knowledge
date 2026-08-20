# Cold-start integration per Hermes profile

The handoff file only helps if the agent actually reads it before greeting the user. We support two patterns; the active one is Pattern A. Pattern B is documented and ready to migrate to when its blocker lands.

## Pattern A — `prefill_messages_file` (active today)

**Mechanism.** Each profile's `config.yaml` sets `prefill_messages_file` to a per-profile JSON file. Hermes injects that file's messages at every LLM call, so the agent sees the handoff greeting on the first turn of every fresh session.

**Steps.**

```bash
# 1. Wire all adopted profiles at once
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py wire --all

# 2. Verify
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py status --all

# 3. Keep the prefill fresh (run after every handoff write)
echo '<handoff-json>' | python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/write_and_wire.py --profile kai --agent kai --session-id <id>
```

**Auto-rewire.** Use `write_and_wire.py` instead of `handoff.py write` on the hot path. It writes the handoff and immediately regenerates the prefill JSON so the greeting stays in sync with the latest `current_state.one_line`. Cost: one extra subprocess (~10 ms).

**Verification.** `hermes config check --profile <name>` reports the key. The verifier in this skill proves the config round-trips and the prefill JSON is well-formed.

**CRITICAL FINDING (2026-07-27, Hermes 0.17.0).** Pattern A wiring is correct, but the `prefill_messages_file` config key is **declared in `config.py:2055` but never loaded by the runtime**. We confirmed by injecting a unique marker phrase (`BANANA_PREFILL_PROBE_98271`) into the prefill JSON, asking the model to recall it, and the model said "no probe marker." The mechanism is dormant until upstream Hermes ships the loader. Probe with the same recipe to verify any future fix.

**Limitation.** Depends on the `prefill_messages_file` config key staying supported. If Hermes removes it, every profile silently regresses.

## Pattern B — plugin `pre_llm_call` hook (deferred)

**Mechanism.** A plugin installed under `~/.hermes/plugins/session-state-handoff-cold-start/` registers `pre_llm_call` and `on_session_start` hooks. The hook reads the active profile's handoff and returns `{"context": "..."}` which Hermes prepends to the user message on every turn.

**Status.** Blocked on [NousResearch/hermes-agent#2817](https://github.com/NousResearch/hermes-agent/issues/2817) — the documented hooks are not actually invoked. We confirmed this by installing a probe plugin that registered both hooks, sending a probe chat, and observing that neither hook ever fired. The hook infrastructure exists (PluginManager.invoke_hook, VALID_HOOKS includes pre_llm_call) but there is no invoke_hook("pre_llm_call", ...) call site anywhere in the agent core.

**Why we picked A over B today.** Pattern A is provable end-to-end with `hermes config check` plus a file-existence verifier. Pattern B requires a real LLM call to prove it fires. Wires that fail silently are worse than wires we can prove.

## Adopting on a new profile

```bash
# 1. Seed the handoff
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py \
  init --profile <new> --agent <new>

# 2. Wire Pattern A
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py \
  wire --profile <new>

# 3. Verify
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py \
  status --profile <new>
hermes --profile <new> config check   # confirms config.yaml still parses
```

## Verifying the integration

For each profile you wire:

1. Run `wire_cold_start.py status --profile <name>` and confirm:
   - `prefill_exists: true`
   - `config_prefill_setting` equals the absolute path
   - `messages_count: 2`
   - `first_message_preview` contains the active handoff greeting
2. Run `hermes --profile <name> config check` and confirm no new errors vs. baseline.
3. **Probe the live model** (most important, even with Pattern A dormant): inject a unique marker phrase, ask the model to recall it. If it cannot, the mechanism is dormant. If it can, the wiring is genuinely live.
4. Edit the handoff (`handoff.py write …` or `write_and_wire.py …`) and confirm the prefill JSON rewrote within the same turn.

If any step fails, fall back to the manual flow: edit `prefill_messages_file` in `config.yaml` directly and write a JSON array to the path it points at. The wiring script is convenience, not a hard dependency.

## The "documented but unverified" pattern

ANY time you read a Hermes config key, schema field, or hook name in docs and plan to use it, run a live probe before declaring success. Three documented mechanisms in 0.17.0 (pre_llm_call, prefill_messages_file, channel_prompts) are declared in code/config but not loaded. Trust docs after you probe; do not trust docs alone.

## MANDATORY directive backfires — use REQUIREMENT (2026-07-27 finding)

When the FIRST-REPLY REQUIREMENT wording in the prefill is too strong, the LLM weights the user prompt more heavily and the agent gives a one-line "ready, what do you need?" reply that ignores the prefill. **Verified across 7 profiles** with the live CLI probe recipe.

| Wording | Verdict | Reason |
|---|---|---|
| `FIRST-REPLY REQUIREMENT: surface …` | ✅ Works | Hints, doesn't override. Agent follows when user prompt is compatible. |
| `MANDATORY FIRST-REPLY FORMAT: your response MUST begin with …` | ❌ Backfires | Strong directive triggers the agent to ignore the prefill and answer the user prompt directly with a brief acknowledgment. All 7 profiles reverted to one-line replies. |
| Omit the directive entirely | ⚠️ Varies | Some profiles surface, some give a one-liner. Depends on the agent's system prompt. |

**Use only the gentle "REQUIREMENT" wording in the prefill.** Stronger language is worse, not better. The constant is `FIRST_REPLY_REQUIREMENT` in `scripts/wire_cold_start.py`. Patching the constant to use MANDATORY will silently regress surface-on-cold-start.

## Adoption loops must exclude the source profile (2026-07-27 finding)

The skill ships `_adopt_shared_skills.py` which symlinks the canonical orchestrator source into every other running profile's `skills/agent-operations/`. **The source profile must be in the exclusion list, not the target list.** This is a hard guard (`SOURCE_PROFILE` constant in the script) because the failure mode is silent and catastrophic:

1. Including the source in the target list creates a self-referencing symlink: `skills/agent-operations/session-state-handoff -> .../orchestrator/skills/agent-operations/session-state-handoff` (the directory pointing to itself).
2. The next step in the loop removes the existing canonical directory and replaces it with the symlink — destroying the canonical source.
3. All other profiles' symlinks now point at deleted targets and are silently broken.
4. Recovery requires rebuilding every file from the conversation transcript. Pins and OKF docs that reference the canonical paths all break at once.

**Future-self should treat any "install X everywhere" script — not just this one — as a candidate for the same bug class.** Hard guards:

1. Exclude the source profile (and any other path that is the canonical source).
2. Refuse to clobber a non-empty directory without an explicit `--force` flag.
3. Take a backup of any pre-existing target to a safe location (e.g. `state/adopt-backups/<profile>/<skill>-<timestamp>/`) before any replace.
4. Run a `--dry-run` before real install and confirm the plan matches intent.

A verifier should run dry-run, then check that real install produces the same error list. **The guard must fire before the dry-run short-circuit** so dry-run doesn't lie about safety — this was a separate bug in 0.1 of the script (the dry-run path bypassed the non-empty-dir check).

## Live verification recipe — use this before claiming "wired"

The verifier recipe that proved the dormant-loader finding:

```bash
# 1. Inject a unique marker phrase into the mechanism's input slot
# For prefill: edit the JSON, insert the marker
# For plugin hook: register a callback that logs the marker when invoked
# For channel prompts: set a channel prompt to a string containing the marker
MARKER="BANANA_PREFILL_PROBE_98271"   # pick something unique + descriptive
# Format suggestion: <WORD>_<KIND>_<8-DIGIT-NUMBER>

# 2. Run a probe that asks the agent to recall the marker
hermes --profile <name> -z "Are you aware of any marker named '${MARKER}' in your context? If yes, repeat it. If no, say 'no probe marker'."

# 3. Read the response
# - If the model repeats the marker: the mechanism is LIVE.
# - If the model says "no probe marker" or fabricates something: the mechanism is DORMANT.
```

**Do not claim "wired" until the probe returns the marker.** File-existence and config-key-presence checks are necessary but not sufficient. Three documented mechanisms in 0.17.0 passed those checks while failing the probe (pre_llm_call, prefill_messages_file, channel_prompts). This is captured as a standalone standard: `okf/standards/hermes-mechanism-probe-recipe.md` in the OKF repo.
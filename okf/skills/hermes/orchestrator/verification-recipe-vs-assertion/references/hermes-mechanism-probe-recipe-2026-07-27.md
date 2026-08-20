# Hermes Mechanism Probe — the "is this feature actually wired?" recipe

**The trap.** Hermes documents many config keys, hooks, and CLI options. Some are wired (changing them changes runtime behavior). Some are **declared but not implemented** (changing them does nothing). Without live probing, you cannot tell which.

Examples observed in Hermes 0.17.0 (2026-07-27) where the documented feature was a no-op:

- `pre_llm_call` plugin hook — registered in `VALID_HOOKS`, contract documented, but never invoked by the agent core. (Issue [#2817](https://github.com/NousResearch/hermes-agent/issues/2817).)
- `prefill_messages_file` config key — declared in schema, env-var equivalent `HERMES_PREFILL_MESSAGES_FILE` documented, agent constructor accepts `prefill_messages=...`, but no code path reads the file or populates that parameter.
- `telegram.channel_prompts` config key — declared in 4 platform-specific schema sections, never read at runtime.

Treating any of these as functional led to incorrect claims ("cold-start greeting works," "Pattern A is wired," "Pattern B is going all-in") that took multiple rounds to retract.

**The recipe.** When you need to confirm whether a documented Hermes mechanism actually reaches the model at runtime:

1. **Identify the injection point.** For prefill_messages_file, it's the messages array sent to the LLM. For a plugin hook, it's whatever the hook's contract says (e.g., pre_llm_call returns `{"context": "..."}` which Hermes prepends to the user message). For channel_prompts, it's the system prompt for that channel.

2. **Plant a unique, discoverable marker.** A phrase that's extremely unlikely to occur anywhere else. The pattern `BANANA_PREFILL_PROBE_<10-digit-number>` is fine. The phrase must be:

   - Specific enough that the model can search for it.
   - Unique enough that it cannot appear in any default prefill, default system prompt, or default tool output.
   - Long enough to be unambiguous (≥30 chars).

3. **Inject the marker through the mechanism you're testing.** For prefill_messages_file: write the marker into the JSON the mechanism is supposed to read. For a plugin hook: have the hook return `{"context": "<marker> ..."}`. For channel_prompts: put it in the configured prompt value.

4. **Send a probe chat via CLI, not the gateway.** Use `hermes --profile <name> -z '<question that asks the model to recall the marker>' --ignore-user-config`. Reasons:

   - CLI chat works even when the systemd gateway is offline.
   - It avoids conflating the probe with Telegram routing.
   - It returns the model's first reply directly.

5. **The probe question must be specific.** Don't ask "do you see anything new in your context?" — that's vague. Ask: *"Are you aware of any marker named `BANANA_PREFILL_PROBE_98271` in your context? If yes, repeat it back. If no, say 'no probe marker'."*

6. **Interpret the result.** Three outcomes:

   - Model repeats the marker exactly → mechanism is wired and reaches the model. Confirmed functional.
   - Model says "no probe marker" (or any other non-recall response) → mechanism is declared but not wired. Cite the schema/docs but the code path is missing.
   - Model paraphrases or invents a "similar" marker → mechanism partially wired (e.g., message injection works but at the wrong position) or the model is confabulating. Re-probe with a more distinctive marker.

7. **Persist the proof.** Save the probe question, raw CLI output, marker used, and verdict to a `/tmp/hermes-verify-mechanism-<feature>-<date>.log` file. The verifier recipe in `references/hermes-mechanism-probe-recipe-2026-07-27.md` is durable; the proof is per-incident.

8. **Update the relevant skill/pin immediately.** If the probe shows the mechanism is non-functional, the handoff/pin/architecture claim that relied on it must be retracted in the same turn — not after a separate "investigation" turn.

## Why this recipe works when file existence doesn't

A "Pattern A" file-exists check (`wire_cold_start.py status --profile X` returns `prefill_exists: true`) only proves that the file was written. It says nothing about whether the file was read by the agent loop. The unique-marker probe bypasses this by checking **the model's actual context** rather than the config layer's stated intent.

This is the same discipline as `references/reconciliation-session-2026-07-27.md`'s "live verifier on the host, not in your head" — but applied at the model-injection layer instead of the file/config layer.

## Common anti-patterns

- **Probing with content the model might have seen elsewhere.** Don't reuse a generic phrase like "hello world" — it might be in default tool output. Don't reuse real-looking IDs (`G-PRRRLMBR8Z`) — they might actually be on the live site. The marker must be unique enough that there's no possible source other than the mechanism under test.

- **Asking the model "did you see X?" instead of asking it to repeat X.** "Did you see it?" can be answered "yes" by a confabulating model. "Repeat it back" requires actual recall. Always ask for the exact value.

- **Trusting one probe.** Run the probe twice with different markers. If the model recalls one but not the other, you have a flaky mechanism, not a working one.

- **Skipping the probe when docs say it works.** The recipe exists because docs lie (or lag behind code). The cost of one probe is ~10 seconds; the cost of trusting a doc that turns out wrong is dozens of turns and broken handoffs.

- **Probing with `--ignore-user-config`.** This flag bypasses user-level config but may also bypass the very mechanism you're trying to test. Drop the flag unless you've confirmed the mechanism you want to probe isn't user-config dependent.

## Worked example: `prefill_messages_file` in Hermes 0.17.0

**Setup.** Wrote a prefill JSON containing `BANANA_PREFILL_PROBE_98271`. Configured `prefill_messages_file` to point at it. Verified file existence via `wire_cold_start.py status`.

**Probe.**

```bash
hermes --profile orchestrator \
  -z "Are you aware of any marker named 'BANANA_PREFILL_PROBE_98271' in your context? If yes, repeat it back. If no, say 'no probe marker'."
```

**Result.** Model replied `no probe marker`.

**Verdict.** `prefill_messages_file` is declared and configurable but the file is never read into the agent's `prefill_messages` parameter at runtime. Wiring is dormant.

**Action taken.** Updated [PIN-2026-07-27-COLD-START-WORKAROUND-PENDING](../../orchestrator/state/pins/PIN-2026-07-27-COLD-START-WORKAROUND-PENDING.md) with the finding. Pattern A wiring across 6 profiles left in place (dormant) rather than rolled back, because the wiring will activate automatically when upstream fixes the loader — no code changes needed at that point.

## When to use this recipe

- Before claiming a cold-start mechanism, plugin hook, or config key is "wired."
- Before spending time building on top of a documented feature.
- After upgrading Hermes (new version may have changed wire-up).
- When a handoff claim relies on a mechanism and the next agent is skeptical.

When NOT to use it: for runtime probes that are themselves expensive (e.g., real API calls, deploys) — those need a different verification recipe (canonical-suite + smoke test, per `references/reconciliation-session-2026-07-27.md`).

## Companion references

- `plan-reconciliation-after-peer-review/references/overclaim-partial-results-discipline-2026-07-27.md` — partner discipline on how *you* report results.
- `session-state-handoff/SKILL.md` pitfall "Don't claim a cold-start mechanism works from file existence alone" — applies this recipe to the cold-start case specifically.
- `hermes-agent/SKILL.md` "Right test surface for cold-start / capability probes" — why `hermes -z '...'` is the right CLI form.
---
type: Standards
title: Hermes Mechanism Probe Recipe — Verify Documented Mechanisms Actually Work
description: Standard recipe for verifying whether a Hermes mechanism that is documented (in user guide, in code comments, in a PR, in a release note) actually reaches the runtime. Use before declaring any mechanism "wired", "set up", "active", or "live". Authoritative reference: the four open pins at ~/.hermes/profiles/orchestrator/state/pins/ that document 2026-07-27 findings.
resource: okf/standards/hermes-mechanism-probe-recipe.md
tags: [standards, hermes, probe, verification, documentation, runtime-vs-declared]
timestamp: 2026-07-29T02:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/hermes-mechanism-probe-recipe.md
linear_issue: null
last_verified: 2026-07-29
verified_by: fred
status: current
---

# Hermes Mechanism Probe Recipe

## Purpose

Multiple documented Hermes mechanisms (in 0.17.0: `pre_llm_call` plugin hook, `prefill_messages_file` config key, `telegram.channel_prompts`) are **declared in code or config schema** but **never reach the runtime**. A 2026-07-27 audit found three such mechanisms by probing them with a unique marker phrase.

This standard defines the probe recipe so future-self doesn't waste turns trusting docs that don't run.

## The recipe

1. **Pick the unique marker phrase.** Format: `<word1>_<kind>_<type>_<8-digit-number>` where the words and kind are descriptive enough that you'd recognize them. Examples:
   - `BANANA_PREFILL_PROBE_98271` — for testing prefill messages
   - `ELEPHANT_PLUGIN_HOOK_44510` — for testing plugin hook invocations
   - `RAVEN_CHANNEL_PROMPT_77332` — for testing per-channel prompts
2. **Inject the marker into the mechanism's input slot.** For prefill: write a prefill JSON containing the marker. For plugin hook: register a hook callback that logs the marker when invoked. For channel prompts: set a channel prompt to a string containing the marker.
3. **Run a probe that asks the agent to recall the marker.** For prefill: send a chat message like "Are you aware of any marker named 'BANANA_PREFILL_PROBE_98271' in your context? If yes, repeat it. If no, say 'no probe marker'." For plugin hooks: trigger a chat that should fire the hook and grep the log file.
4. **Read the response.** If the model/harness reports the marker: the mechanism is live. If it doesn't: the mechanism is declared but not loaded.
5. **Document the finding** in a pin at `~/.hermes/profiles/orchestrator/state/pins/PIN-YYYY-MM-DD-<slug>.md`. Include the marker, the probe transcript, the response, and the conclusion.

## Why the recipe works

LLM agents will confidently claim they have context they don't actually have. They will fabricate markers they should have seen, generate plausible-looking error messages, and answer "yes" to questions they have no information about. The recipe defends against this in two ways:

- **The marker is unique.** The agent cannot reasonably know the marker unless it actually read the input that contained it.
- **The probe is open-ended.** "Are you aware of any marker..." gives the agent a chance to say "no" without losing face. A "no" is a clean signal the mechanism is dormant.
- **The probe tests the load path, not the model.** The marker is in the input mechanism; the question is whether the harness actually passes that input to the LLM call.

## When to use this

Use before any of:

- Declaring a config key "wired" because the schema declares it
- Declaring a hook "active" because the docs say it's invoked
- Marking an integration "live" because the implementation file exists
- Closing a task that says "set up X for future use" without live verification
- Trusting release notes, blog posts, or third-party tutorials that claim X is supported

The recipe is cheap. Each probe takes under a minute. The cost of skipping is what's documented in `okf/reports/2026-07-27-agent-harness-discipline-session.md` — three declared mechanisms, none of them actually running.

## The 2026-07-27 findings (use these as reference for "what can be wrong")

| Mechanism | Documented as | Actually does in 0.17.0 |
|---|---|---|
| `pre_llm_call` plugin hook | Injects context into user message on every turn | Not invoked anywhere in the agent core (verified with probe plugin) |
| `prefill_messages_file` config key | Loads JSON, injects messages on every LLM call | Schema declares it, no code path reads the file |
| `telegram.channel_prompts` config key | Per-channel ephemeral system prompts | Schema declares it, no code path reads at runtime |

The fix for all three is upstream. The wiring in the meantime is correct but dormant.

## Anti-patterns to refuse

- "The doc says it works, that's good enough." Probe or don't claim.
- "I'll verify when it actually breaks." It already broke. You didn't notice.
- "It's a release-note claim, must be true." Hermes 0.17.0 release notes claimed all three mechanisms. Live probe disproved.
- "The schema declares it, so the runtime supports it." Schema is necessary, not sufficient.
- "I tested it last week, it worked." Was your test a live probe, or a file-existence check? File-existence proves the file exists. It doesn't prove the runtime reads it.

## What to do when a probe finds a documented-but-broken mechanism

1. **Don't fix it locally.** The mechanism is upstream's responsibility. Local patches diverge from the project.
2. **File a pin.** Document the marker, the probe, the conclusion, and the trigger to revisit. Pins are the durable record.
3. **Continue as if it's dormant.** Your local wiring can be correct. When the upstream fix lands, your dormant wiring activates without code change.
4. **Don't claim "closed" or "wired"** in any artifact (Linear issue, OKF doc, Slack message) until the live probe succeeds. Use "shipped dormant-correct" or "dormant-pending-upstream" instead.

## Related work

- `okf/standards/hermes-session-handoff-discipline.md` — companion standard for the handoff primitive
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` — full session report
- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-PATTERN-B-BLOCKED-2817.md` — pin using the recipe
- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-COLD-START-WORKAROUND-PENDING.md` — pin using the recipe

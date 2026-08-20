---
name: product-bot-voice-governance
description: Use when tuning customer-facing bot voice, onboarding copy, generated persona/soul prompts, or LLM style rails for product bots such as HDE Sanctuary. Focuses on soft style bias, relatable language, and avoiding brand/esoteric overperformance without brittle banned-word rules.
---

# Product Bot Voice Governance

## When to use

Use this skill when Michael asks to improve the tone, relatability, brand feel, or language behavior of a customer-facing bot or generated assistant persona, especially when the bot is powered by a reusable system prompt, `soul.md`, onboarding router copy, or prompt scaffold.

Typical triggers:

- Reduce loaded, theatrical, therapy-ish, esoteric, mystical, or over-branded language.
- Make a bot feel more human, grounded, ordinary, or relatable.
- Tune generated prompt instructions without making brittle hard rules.
- Adjust onboarding, first-contact, wake/error, trial/access, or guide-name copy.
- Review “brand voice” complaints where the model is technically correct but socially off.

## Core principle

Prefer **soft style bias** over hard blacklists.

Do not solve tone drift by banning individual words unless safety/legal constraints require it. Banned-word rails make the model brittle, evasive, and weird. Instead, set the desired center of gravity:

> Sound like a grounded, perceptive person helping another person think clearly — not a mystical app, not a therapist performing brand voice, not a guru, and not a feature menu.

Loaded words can still appear when they are specific, earned, and natural. The goal is lower density and better context, not mechanical absence.

## Practical workflow

1. **Find both prompt and router copy**
   - Inspect generated persona/soul/system prompts.
   - Inspect deterministic onboarding, welcome, wake, waiting, error, demo/access, and CTA strings.
   - Loaded language often enters through seed examples, not only through the live model prompt.

2. **Name the voice target before editing**
   - Write one plain-English sentence describing the desired voice.
   - Example: “A grounded, perceptive person helping the user take one practical next step.”

3. **Convert word avoidance into usage guidance**
   - Bad: “Never use honest, true, alive, fair, slice.”
   - Better: “Words like honest/true/alive/fair/slice are not banned, but should be occasional, earned, and specific. Most replies should use ordinary language.”

4. **Rewrite anchor examples**
   - Prompt examples strongly bias generation.
   - Replace ceremonial examples with ordinary, human versions.
   - Keep examples as “shape, not script” unless exact wording is required.

5. **Reduce product-name repetition**
   - Keep branded terms for onboarding, access/status, and product navigation.
   - In normal conversation, prefer “here,” “this,” “this space,” or no container label at all.

6. **Keep mechanics real, translate the surface**
   - Do not remove real domain mechanics.
   - Translate jargon into plain English unless the user asks for technical depth.
   - Avoid implying the bot is a fake companion, oracle, therapist, or authority.

7. **Roll out current + future surfaces when requested**
   - Future instances need source/provisioning templates patched.
   - Current instances need live prompt surfaces patched too: host instance dirs, user workspaces, base/active soul files, and prompt-regeneration scripts.
   - If prompts are mounted into containers, restart only the affected bot containers/services after patching and verify health.

8. **Verify by ratio and samples, not a forbidden list**
   - Add focused checks that flag old anchor phrases and unusually dense loaded-language clusters.
   - Review representative prompt snippets and generated sample replies.
   - Treat flags as review prompts, not automatic failures, unless the product requires strict compliance.
   - For code-backed products, also run the canonical project verifier requested by the platform/user, not just the focused voice check.

## Rewrite patterns

| Less relatable | More relatable |
|---|---|
| “Bring me one honest sentence, and we’ll start there.” | “Tell me what’s going on, and we’ll take it one step at a time.” |
| “Reflect what is true.” | “Reflect what seems to be happening.” |
| “Keep the wording alive.” | “Keep the wording natural and situation-specific.” |
| “This is a private practice room for honest healing and deconditioning.” | “This is a private place to slow down, notice patterns, and choose the next practical step.” |
| “Activating / aligning energy.” | “Opening this up / getting your space ready.” |
| “No performance required.” | “You do not need to package it perfectly.” |

## HDE Sanctuary-specific guidance

- Preserve the Sanctuary positioning and real Human Design mechanics.
- Do not turn the bot into a fake companion loop or separate invented persona.
- “Sanctuary” may remain the product/container name, but reduce repetition during normal chat.
- Avoid overusing words Michael has flagged as loaded in this context: “fair,” “honest,” “true,” “alive,” “slice,” and similar moralized or poetic intensifiers.
- Prefer ordinary language: “what’s going on,” “what seems to be happening,” “one practical next step,” “what your body is telling you,” “test it in real life.”
- Human Design terms are allowed when needed, but translate them immediately into lived behavior.

## Verification checklist

Before reporting done on a bot-voice patch:

- [ ] Prompt/persona scaffold reviewed.
- [ ] Deterministic router/onboarding/wake/error copy reviewed.
- [ ] Seed examples updated where they over-anchor loaded language.
- [ ] Product/domain terms preserved where needed.
- [ ] Current live prompt surfaces patched when Michael asked for existing instances, not only future templates.
- [ ] Active bot containers/services restarted when mounted prompt files require it, then health checked.
- [ ] A focused sample or scan checks old anchor phrases and density of loaded terms without enforcing a brittle ban.
- [ ] Canonical project verifier run when code/repo files changed.
- [ ] Temporary bulk updater scripts removed after the migration.
- [ ] Final report distinguishes “tone guidance updated” from “live bot redeployed,” if deployment was not performed.

## References

- `references/2026-07-hde-sanctuary-loaded-language.md` — session note on reducing loaded Sanctuary bot language through soft style bias rather than hard rules.

## Pitfalls

- Do not overcorrect into sterile corporate language; relatable does not mean bland.
- Do not remove safety boundaries while making the bot warmer.
- Do not make “avoid esoteric language” into “never mention the domain.” Keep mechanics accurate and translate the surface.
- Do not claim the live bot changed unless the relevant code/config was patched, deployed, and verified.
- Do not rely only on model prompt changes when deterministic router strings still seed the wrong feel.

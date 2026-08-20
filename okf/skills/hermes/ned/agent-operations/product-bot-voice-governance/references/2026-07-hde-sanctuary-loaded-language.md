# HDE Sanctuary loaded-language tone tuning — 2026-07

## Context

Michael asked to reduce loaded words in the HDE Sanctuary bot — examples included “fair,” “honest,” “true,” “alive,” and “slice” — without using hard rules. The product goal was a more relatable bot that does not sound esoteric.

## Reusable lesson

The right fix is not a blacklist. Use a soft style bias that lowers density and changes the default voice:

> Prefer plain, emotionally normal language. Avoid making the interaction feel sacred, theatrical, or like therapy-speak unless the user is already speaking that way. Words like “fair,” “honest,” “true,” “alive,” “slice,” “sanctuary,” “healing,” and “deconditioning” are not banned, but should be occasional, earned, and specific. Most replies should sound like a grounded person helping another person think clearly.

## Places to inspect in HDE-like bot stacks

- Future-instance scaffolds: generated persona/soul prompt code, e.g. provisioners that write `soul.md` / `active_soul.md`.
- Deterministic router strings: onboarding prompts, guide-name prompts, ready messages, wake/loading copy, errors, trial/access notices.
- Runtime prompt builders inside guest servers; a product may use both `SOUL.md` and a separate explicit LLM prompt builder.
- Current instance files, not only source templates: host-side `guest_hermes_bot_*`, user workspaces such as `/home/ubuntu/users/guest_*`, mounted `soul.md` / `active_soul.md`, and any `update_soul_profile.py` that can reintroduce old copy after chart generation.
- Skill files installed into guest workspaces that may reintroduce old tone.
- Product/docs language used as source material for prompt scaffolding.

## Current + future rollout pattern

When Michael asks for a bot-voice change “for all current and future bot instances”:

1. Patch source/provisioning templates first so new instances inherit the style.
2. Patch deterministic router/onboarding/wake/error copy.
3. Patch every current instance surface that can drive the live prompt, including base and active prompt files plus update scripts that regenerate active prompts.
4. Restart active containers/services only after live-mounted files are patched, then verify health/start times.
5. Add a focused verifier that checks old anchor phrases and loaded-word density as a review signal, not a brittle banned-word rule.
6. If repo files changed, run the canonical build/test command in addition to the focused voice verifier; remove temporary updater scripts after use.

## Concrete rewrite examples

| Before | After |
|---|---|
| “Bring me one honest sentence, and we’ll start there.” | “Tell me what’s going on, and we’ll take it one step at a time.” |
| “This is a quiet room for honest work — no performance required.” | “This is a quiet place to say what’s going on without packaging it perfectly.” |
| “Reflect what is true, name the avoidance cleanly, and offer one grounded move.” | “Reflect what seems to be happening, name the pattern gently, and offer one practical next step.” |
| “Hard rules matter; the wording around them should stay alive, human, and situational.” | “Keep the safety boundaries, but let the wording sound natural and situation-specific.” |
| “Aligning energy…” | “Reconnecting…” or “Getting your space ready…” |
| “single source of truth” | “main decision signal” |

## Product nuance

- Keep “Sanctuary” as the product/container name, but do not repeat it in normal chat unless access/status/product context calls for it.
- Do not erase real Human Design mechanics. Translate them into ordinary lived language.
- Avoid fake companion framing. The bot should be useful and grounded, not a mystical friend, guru, therapist, or validation machine.

## Verification idea

Use a focused prompt/sample scan that reports loaded-term density and old anchor phrases. Treat loaded-term density as a review signal, not a hard failure. Pair the scan with human review of representative first-contact and stressed-user replies. For code-backed products, also run the canonical project verifier requested by the platform/user, e.g. `npm run build`, even when the voice change is mostly Python/string files.

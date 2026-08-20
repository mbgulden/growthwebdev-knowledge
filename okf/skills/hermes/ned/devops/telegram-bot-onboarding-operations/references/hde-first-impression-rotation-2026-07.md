# HDE first-impression rotation pitfall — 2026-07

## Trigger
Michael reported George failed the first-impression test after `/new`: it recycled the same “I’m here / one honest sentence” phrase repeatedly. The copy technically followed the Soul but felt scripted and inauthentic.

## Durable lesson
For HDE/Sanctuary guest bots, do not rely on the LLM alone for repeated reset/greeting openings. `/new`, `/start`, reset, and simple greetings need a light deterministic guard that rotates first-impression prompts so the bot does not create a stale loop before the relationship even starts.

## Preferred first-touch shape
Use short binary or “this/that” doorways rather than wide-open prompts:

- “Is today more a ‘sort it out’ day, or a ‘just sit with me’ day?”
- “Do you want to name the thing first, or feel where it lands in your body?”
- “Should we start with what feels heavy, or with what still feels true?”
- “Do you want the direct thread, or the gentler doorway in?”

Rationale: Generators + Manifesting Generators are commonly treated as the majority of the population (~70% in HD teaching), and sacral-response users often respond better to concrete choices. Keep it inclusive: the prompt should still work for Projectors, Manifestors, and Reflectors; do not assume type before the chart exists.

## Implementation pattern
- Add explicit `/new`/reset and greeting detection ahead of the LLM fallback in the guest agent server.
- Clear structured chart state on reset.
- Persist a tiny greeting state file (e.g. `/workspace/greeting_state.json`) with index/last prompt so sequential greetings rotate.
- Do not include birth details, `YYYY-MM-DD`, chart menus, or “show don’t tell” instruction language in greeting responses.
- Keep chart intent separate: chart requests still start with birth date only, using `MM/DD/YYYY` or natural language.

## Focused verification recipe
Use a `/tmp/hermes-verify-*` ad-hoc verifier that checks:

1. `guest_agent_server.py` compiles.
2. reset/greeting guard constants/functions exist.
3. guest container is healthy.
4. After clearing `conversation_state.json` and `greeting_state.json`, API calls to `/new`, `Hi`, and `Hi George` return three distinct prompts.
5. The prompts contain simple choice framing and do not mention birth-date walls, `YYYY-MM-DD`, “three things,” or internal philosophy.
6. `I want to build my chart` still asks only for birth date with `MM/DD/YYYY` or natural language.

# HDE LLM-first static layer reduction notes — 2026-07

## Session signal
Michael reported that the Human Design bot felt painful, rigid, and unlike the intended Sanctuary/George experience: he could not get past profile and first-chart setup. The core product issue was too much static conversation control in front of the LLM.

## Durable architecture lesson
Use this boundary for HDE/George guest runtime work:

- **LLM owns conversation:** tone, repair, pacing, contextual interpretation, mixed-initiative dialogue, and ordinary replies.
- **Tools own facts/actions:** profile field saves, chart generation, comparison generation, journal writes/searches, media paths, search context.
- **Validators own correctness:** auth/start tokens, malformed birth data, date/time/location parsing, rate/budget limits, DB writes, media delivery, safety/abuse boundaries.
- **State owns memory:** known profile fields, missing fields, latest chart artifacts, recent conversation history, current user goal.

Do not let regex/static handlers become George. They should expose known state, detect critical interrupts, and call tools — not dictate the conversation.

## Pre-emptive changes to prefer before live user testing
1. **Frustration/repair interrupt**
   - Detect signals like “this is painful,” “you already have that,” “I can’t get past this,” “why are you asking again,” “stop,” “this isn’t working.”
   - Immediately pause any active flow and respond with: brief ownership + known state + one next action.
   - Example shape: “You’re right. I’m making this harder than it needs to be. I have X. I’m missing Y. Want me to use that and continue?”

2. **LLM-managed slots for profile/chart intake**
   - Give the LLM known fields, missing fields, and allowed actions.
   - Let it ask naturally for one missing field.
   - Deterministic code validates and persists each field.
   - Avoid flow-state wording and hard-coded menu dialogue.

3. **Known-state prompt primitive**
   - Every LLM prompt should include: profile exists?, birth-data status, chart exists?, current user goal, missing next field/action.
   - Common response pattern: “I have X. I’m missing Y. I can do Z now.”

4. **Use-what-you-have behavior**
   - Do not block completely on missing birth time.
   - If exact time is missing, offer rough/unknown-time mode with caveat instead of dead-ending.
   - Store confidence (`exact`, `approximate`, `unknown`, `inferred`) per birth field when possible.

5. **Conversation mode classification instead of regex-heavy intent routing**
   - Lightweight LLM classification can pick mode: `profile_setup`, `chart_generation`, `chart_explanation`, `relationship_friction`, `practical_life_issue`, `frustration_repair`.
   - Deterministic code then validates allowed actions.

6. **Transcript replay harness**
   - Preserve painful chat logs as replay fixtures.
   - Score each turn for: context preservation, one-question pacing, no re-asking known data, progress toward goal, Sanctuary tone, no rigid/menu behavior, and frustration recovery.
   - Treat replay as focused ad-hoc proof; live Telegram canary is still separate.

## Research directions that map to implementation
- Conversational repair strategies: acknowledge breakdown, avoid making the user repeat context, provide an actionable next step.
- Progressive disclosure: ask for only the field needed now; do not expose full menus/flows up front.
- Mixed-initiative dialogue: let the user lead and George guide; avoid system-initiative lock-in.
- LLM slot filling + deterministic validation: extraction and natural questioning by LLM, persistence and validation by code.
- Trust calibration/uncertainty: represent exact vs approximate vs unknown birth data instead of false certainty or hard blocking.

## Pitfall
If a server-side canary passes but live use still feels bad, inspect the conversation-control layer first. Generic “health,” compile, and single-turn canaries do not prove the bot feels like Sanctuary across a short real conversation.

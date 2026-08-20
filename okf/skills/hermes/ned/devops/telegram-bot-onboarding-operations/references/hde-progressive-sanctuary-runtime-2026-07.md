# HDE progressive Sanctuary runtime wiring — 2026-07

## Trigger

Michael reported that George / the HDE Telegram guest bot opened with a rigid chart intake block:

```text
Welcome in. Let's get your chart built. I'll need three things...
1. Birth date (YYYY-MM-DD)
2. Birth time (HH:MM...)
3. Birth location...
```

This failed the product intent: Human Design Engine Sanctuary should embody the progressive conversational soul, not recite instructions or overwhelm guests.

## Durable product rules

- Greeting: one warm sentence plus one open invitation. No menu, no chart intake, no philosophy lecture.
- “Show, don’t tell”: hard rules live in the Soul; do not read the instruction manual to guests.
- Chart intake: only after explicit chart/reading/bodygraph/report/comparison intent.
- Intake pacing: one field at a time.
- American-facing dates: ask for `MM/DD/YYYY` or natural language; convert to ISO only for internal tool calls.
- MiniMax M3 should have room to weave. Use deterministic routing for safety-critical flows, but avoid rigid visible scripts for normal conversation.

## Runtime pattern that worked

The stable shape is a hybrid:

1. **Soul prompt** defines product essence and hard rules:
   - Sanctuary / George is a working handle, not a fake companion.
   - No dependency loops, no validation-to-stuckness.
   - Kind with backbone, embodied rather than announced.
2. **Mounted skills** keep original progressive procedures available:
   - `collect-birth-details.md`
   - `deconditioning-coach.md`
   - `read-hd-context.md`
   - `task-atomicizer.md`
3. **Deterministic guest server shortcuts** intercept fragile structured flows before the LLM:
   - greetings remain LLM/Soul-led,
   - chart intent starts progressive birth-date intake,
   - comparison intent starts Person 1 progressive intake, then Person 2,
   - journal shortcut writes directly to SQLite,
   - all other conversation falls through to Hermes/MiniMax.
4. **Chart artifacts** are written where router/coach systems can see them:
   - personal: `/workspace/charts/personal/chart_data.json` plus `/workspace/charts/personal/user/`
   - comparison: `/workspace/charts/friends/person_1/` and `person_2/`
   - each subject directory gets `chart_data.json` and a PDF.

## Verification pattern

Server-side direct API canaries are valid for focused ad-hoc verification:

- `Hi George` must not mention birth details or `MM/DD/YYYY`.
- `I want to build my chart` must ask only for birth date.
- `I want to compare two charts` must ask only for Person 1 birth date.
- Full comparison canary should generate:
  - final Person 1 / Person 2 summary,
  - grounded practical experiment,
  - two `chart_data.json` files,
  - two PDFs.
- Journal canary should write a probe row and delete it afterward.
- Always clear `conversation_state.json` and remove fake chart artifacts after canaries.

## Pitfalls

- `chart` regexes must match plural `charts`; otherwise “compare two charts” falls through to generic MiniMax chat instead of deterministic comparison intake.
- Refreshing generated guest files can accidentally replace the MiniMax config with stale OpenRouter template config; preserve or regenerate `provider: minimax` / `default: MiniMax-M3`.
- A chart PDF can be valid even if optional PNG rendering fails. Do not make PNG preview failure break the user-facing chart flow.
- Direct guest API passing is not the same as a full Telegram canary. Final end-user proof still requires a real Telegram message because Bot API cannot send `/start` as the user.

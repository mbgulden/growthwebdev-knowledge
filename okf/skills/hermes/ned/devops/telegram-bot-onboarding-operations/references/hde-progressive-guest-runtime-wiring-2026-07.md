# HDE progressive guest runtime wiring — July 2026

## When this applies

Use when an HDE/George guest bot is technically reachable but fails the product promise: generic chart intake, rigid instruction-manual copy, YYYY-MM-DD user prompts, missing progressive skills, charts/comparisons not attaching, or coaches cannot inspect backend continuity.

## Durable lessons

- The public Telegram/head-bot route is only one layer. The actual guest behavior lives in the guest template/runtime files and the mounted Hermes profile inside each `guest-hermes-*` container.
- Progressive behavior must be wired in two places:
  1. **Soul/skills** for model behavior: show-don't-tell, one warm invitation, no menu/instruction dump, Sanctuary framing, progressive collection rules.
  2. **Deterministic server guards** for hard UX rules: date/time/location one field at a time, American-facing `MM/DD/YYYY` or natural language, compare two charts person-by-person, journal shortcuts.
- MiniMax should not be over-scripted. The Soul carries the stance; deterministic code should enforce only hard boundaries and tool routing.
- Do not overwrite generated guest `config.yaml` with stale template config. Verify live guests still have MiniMax provider config mounted.

## Guest runtime files that mattered

- `/home/ubuntu/guest_hermes_bot/guest_agent_server.py`
  - progressive chart intake
  - comparison intent detection including plural `charts`
  - journal shortcut routing
  - response cleanup for `__CHART_FILE_PATHS__`
- `/home/ubuntu/guest_hermes_bot/daily_journal_mcp.py`
  - journal DB tools
  - report PDF generation/copying
  - chart data persistence
  - coach-visible manifests/events
- `/home/ubuntu/guest_hermes_bot/SOUL.md` or `soul.md` source copied into guest `.hermes/SOUL.md`
- `/home/ubuntu/guest_hermes_bot/docker-compose.guest.yml`
  - reports mount for attaching generated PDFs

## Required runtime behavior

### Greeting

A greeting must not trigger chart intake. Expected shape:

- one warm sentence
- one open invitation
- no birth-date request
- no menu
- no recitation of “kind with backbone” or other internal rules

### Personal chart

For `I want to build my chart`, ask one field at a time:

1. birth date — user-facing `MM/DD/YYYY` or natural language
2. birth time — normal human input, approximate/unknown accepted
3. birth location — city/state/country is enough

Internally convert date/time to tool formats; never make the guest use ISO dates.

### Chart comparison

For `I want to compare two charts`, gather person-by-person:

1. Person 1 date/time/location
2. generate/store Person 1 chart
3. Person 2 date/time/location
4. generate/store Person 2 chart
5. return a plain-English comparison with type/authority/profile, shared centers/channels, and one practical experiment

Expected artifact counts after a successful comparison canary:

- 2 `chart_data.json`
- 2 `coach_manifest.json`
- 2 PDFs
- 2 `chart_generated` events in `/workspace/coach_view/events.jsonl`

### Coach/backend continuity

Chart generation should leave coach-readable artifacts under the guest workspace:

- `/workspace/charts/<relationship>/<subject>/chart_data.json`
- `/workspace/charts/<relationship>/<subject>/coach_manifest.json`
- `/workspace/coach_view/events.jsonl`

Journal writes should append `journal_entry` events to the same JSONL stream.

## Focused ad-hoc verification pattern

When canonical tests do not exist, create a temporary verifier with `tempfile.mkstemp(prefix='hermes-verify-', dir='/tmp')`, run it, then delete it. Verify:

- edited Python files compile
- HDE services are active
- `guest-hermes-23` is healthy
- mounted Soul/config/skills exist and include progressive/Sanctuary/MiniMax signals
- greeting does not trigger chart intake
- personal chart starts with date only
- comparison starts with Person 1 date only
- full comparison produces both chart artifacts and coach events
- journal shortcut writes DB row and coach event
- canary artifacts and `conversation_state.json` are cleaned afterward

Always call this ad-hoc verification, not canonical suite green.

## Cleanup after canaries

Remove fake artifacts so George's live persona and coach backend are not contaminated:

- `/home/ubuntu/users/guest_<id>/conversation_state.json`
- fake `/home/ubuntu/users/guest_<id>/charts/friends` or personal chart outputs
- fake `/home/ubuntu/users/guest_<id>/coach_view` events created only for verification
- any fake journal DB rows

Reset `active_soul.md` if a personal chart canary adapted the Soul from fake data.

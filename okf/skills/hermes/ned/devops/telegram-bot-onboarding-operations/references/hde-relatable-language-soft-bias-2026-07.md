# HDE Sanctuary relatable-language soft bias — 2026-07

## Trigger

Michael asked to reduce loaded/ceremonial language in the Sanctuary bot without hard rules or esoteric phrasing. Target words included `fair`, `honest`, `true`, `alive`, `slice`, plus similar grandiose/therapy-coded words.

## Durable lesson

Do not solve this with a blacklist. Use a soft style bias across the generated Soul, router/head-bot copy, current guest workspaces, and runtime LLM prompt:

> Sound like a grounded, perceptive person, not a mystical app, therapist, or coach performing a brand voice. Prefer ordinary, emotionally normal language. Loaded words are not banned, but should be occasional, earned, and specific.

## Implementation pattern

1. Patch future provisioning in `scripts/vm_orchestrator.py` so generated `soul.md` includes a `## Relatable Language` section.
2. Patch router/head-bot copy in `scripts/hde_tenant_router.py` for onboarding/wake/error phrases.
3. Patch current instances in both host-side config directories and mounted workspaces:
   - `/home/ubuntu/guest_hermes_bot_{id}/soul.md`
   - `/home/ubuntu/guest_hermes_bot_{id}/active_soul.md`
   - `/home/ubuntu/users/guest_{id}/soul.md`
   - `/home/ubuntu/users/guest_{id}/active_soul.md`
   - `/home/ubuntu/users/guest_{id}/update_soul_profile.py`
   - `/home/ubuntu/users/guest_{id}/guest_agent_server.py` when present
4. Patch the base guest template under `/home/ubuntu/guest_hermes_bot/` if the orchestrator still uses it as `TEMPLATE_DIR` fallback.
5. Add or run a soft verifier that checks old anchor phrases and prompt surfaces, but avoid a hard word blacklist.
6. Restart current guest containers after editing mounted live prompt files; verify Docker health afterward.

## Good replacements

- “Bring me one honest sentence…” → “Tell me what’s going on, and we’ll take it one step at a time.”
- “honest healing, deconditioning…” → “pattern work, clearer choices, and grounded change.”
- “Reflect what is true…” → “Reflect what seems to be happening…”
- “single source of truth” → “main decision signal.”
- “Aligning energy…” → “Reconnecting…”

## Verification recipe

Run all applicable checks:

```bash
python3 -m py_compile scripts/vm_orchestrator.py scripts/hde_tenant_router.py scripts/check_hde_bot_voice.py
python3 scripts/check_hde_bot_voice.py
npm run build
```

Also scan current instances for old anchor phrases and missing `## Relatable Language`. If temporary updater scripts were used under `/tmp`, remove them before final verification so platform changed-path checks do not keep flagging them.

## Pitfalls

- Do not hard-ban the words. The desired behavior is taste and relatability, not compliance theater.
- Do not only patch repo templates; current guests keep live mounted prompt files.
- Do not restart via `docker compose` without the right env file/context; direct `docker restart guest-hermes-*` is safer for already-running containers when only mounted prompt files changed.
- Do not claim a full live user-tone proof from static checks alone. Static checks prove the prompt surfaces changed; a real Telegram tester is still needed to judge conversational feel.

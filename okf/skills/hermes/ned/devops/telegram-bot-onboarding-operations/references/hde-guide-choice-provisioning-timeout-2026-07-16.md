# HDE guide choice + provisioning timeout pitfall — 2026-07-16

## Trigger

During a real Human Design Companion onboarding test, the bot told Michael to contact support immediately after guide-name selection.

Observed state:

- Router accepted the Telegram guide choice and sent the setup/provisioning message.
- Staging orchestrator did eventually return `200 OK` and created `guest-hermes-2`.
- Router had already timed out its HTTP call at 25 seconds, marked the bot instance `error`, and sent the user-facing support message.
- The guide name had been stored as the literal phrase `Let’s do ember` because the parser treated a natural preset-selection phrase as a custom name.

## Root causes

1. **Provisioning timeout too short for cold guest builds**
   - First-time guest provisioning may build/install a container and can exceed 25 seconds.
   - A router timeout does not prove provisioning failed; check orchestrator logs and Docker state before declaring setup broken.

2. **Natural preset phrase parsed as a custom guide name**
   - Inputs like `Let’s do ember`, `use ember`, `pick Ember`, `choose mira`, and `go with mira` should resolve to the preset guide names.
   - Otherwise the guest Soul is generated with awkward names like `Let’s do ember`.

## Durable fix pattern

- In `normalize_guide_name`, preserve exact presets and add a regex for natural preset-selection phrases:

```python
for preset_key, preset_name in GUIDE_PRESETS.items():
    if re.fullmatch(rf"(?:let'?s\s+)?(?:do|use|pick|choose|go\s+with)\s+{re.escape(preset_key)}", key):
        return preset_name, "preset"
```

- Keep ordinary questions from becoming names:

```python
if "?" in raw or len(clean.split()) > 3:
    return None, None
```

- Make provisioning timeout configurable and long enough for cold builds:

```python
resp = await client.post(
    target_url,
    content=payload_bytes,
    headers=headers,
    timeout=float(os.getenv("HDE_ORCHESTRATOR_PROVISION_TIMEOUT_SECONDS", "180")),
)
```

- If a user is already stuck in `error` after a timeout but the container exists and is healthy:
  1. Check `hde_orchestrator_staging.service` logs for `POST /api/orchestrate/provision HTTP/1.1" 200 OK`.
  2. Check `docker ps -a --filter name=guest-hermes-USER_ID`.
  3. Verify `/home/pn/.hermes/SOUL.md` inside the container is a file and has the intended guide name.
  4. Correct `users.guide_name` / `guide_name_source` if needed.
  5. Set the bot instance back to `active` only after container and router-to-guest checks pass.

## Verification recipe

Focused verification should include:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 -m py_compile \
  scripts/hde_tenant_router.py shared/database.py scripts/vm_orchestrator.py
```

Then import and check guide normalization cases:

- `Ember` -> `("Ember", "preset")`
- `Let's do ember` -> `("Ember", "preset")`
- `use ember` -> `("Ember", "preset")`
- `pick Ember` -> `("Ember", "preset")`
- `choose mira` / `go with mira` -> `("Mira", "preset")`
- `what can you do?` -> `(None, None)`

Operational checks:

- `systemctl is-active hde_router.service hde_orchestrator_staging.service`
- `scripts/hde_router_metrics.py --pretty` shows `status=ok`, Redis ok, pending queues = 0.
- `docker exec guest-hermes-USER_ID test -f /home/pn/.hermes/SOUL.md` and inspect the first lines.
- Exercise router-to-guest path, not only direct container health: router should resolve the guest container IP and receive HTTP 200 from `/api/message`.

## Pitfalls

- Do not trust the support message alone. It can be emitted by the router timeout path even when orchestrator succeeds later.
- Do not rerun the old onboarding link if the Telegram chat is already linked and the bot instance is active; send a normal chat message instead.
- Do not leave phrase-like guide names in the Soul file when the user clearly selected a preset.

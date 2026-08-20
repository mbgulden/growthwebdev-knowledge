# HDE location-only chart/PDF recovery + new-bot permission pitfall — 2026-07

## Trigger

Use when a Human Design Engine tester/bot appears to calculate a chart after a location reply like `Provo, UT`, but no PDF/bodygraph is attached, or when new HDE bots cannot update live Soul/profile context after chart generation.

## Root cause pattern

Family/beta testers often split birth intake across turns:

1. Date/time in one turn, e.g. `March 18, 1988`, then `9:30 AM`.
2. Location-only reply in the next turn, e.g. `Provo, UT`.

If transient `pending_chart` state is gone or the prior response went through the LLM path, the location-only turn can fall through to the LLM. The bot may then narrate a chart but never call deterministic chart/PDF generation, leaving no `pdf_path`, `pdf_paths`, image path, `chart_data.json`, or Telegram media upload.

## Durable fix shape

Patch the guest runtime, not the prompt:

- Add a short city/state classifier for location-only replies.
- If recent user turns contain birth/chart context plus date/time, combine the recent user turns with the current location.
- Treat the current location as authoritative.
- Call deterministic `generate_chart_for_birth_details(...)` / chart generation before LLM fallback.
- Extract `__CHART_FILE_PATHS__` and return `image_path`, `pdf_path`, and `pdf_paths` to the router.
- Keep Provo, Utah mapped to `America/Denver` with real Provo coordinates so it cannot drift to UTC/0,0.

Important parser pitfall: existing `parse_birth_time('Provo, UT')` may return `UNKNOWN`. Do not treat `UNKNOWN` as a real time when classifying city/state replies; only reject location-only recovery when parsed time is present and not `UNKNOWN`.

## New-bot permission pitfall

The orchestrator may correctly `chown` `/home/ubuntu/users/guest_<id>` but miss the per-container base directory `/home/ubuntu/guest_hermes_bot_<id>`. Files from that base directory are bind-mounted into `/home/pn/.hermes`, including `active_soul.md` / `SOUL.md`. If those stay root-owned, chart generation can succeed while `update_soul_profile.py` throws `PermissionError` updating the live Soul.

Fix provisioning by chowning both:

```python
subprocess.run(["sudo", "chown", "-R", "1000:1000", workspace_dir], check=True)
subprocess.run(["sudo", "chown", "-R", "1000:1000", base_dir], check=True)
```

Do this for future bots and also repair/restart the affected live guest container when needed.

## Verification recipe

Use a focused `/tmp/hermes-verify-*` script and label it ad-hoc, not canonical suite green:

1. `py_compile` changed guest/orchestrator Python files.
2. Static assertions:
   - location-only helper exists,
   - recent birth-context recovery helper exists,
   - `UNKNOWN` time parse guard exists,
   - orchestrator `base_dir` chown exists,
   - ops docs mention recovery and writable `active_soul.md`.
3. Back up affected guest files: `conversation_history.json`, `conversation_state.json`, `people/index.json`, `active_soul.md`.
4. Seed recent history with a date/time turn and ask the live guest API `/api/message` with `Provo, UT`.
5. Assert returned JSON has `pdf_path`, `pdf_paths`, and `image_path`.
6. Assert generated PDF/image files exist and are non-trivial size.
7. Read generated `chart_data.json`; assert timezone `America/Denver` and Provo coordinates around `40.2338,-111.6585`.
8. From inside the guest container, call `host.docker.internal:8081/api/compute` with the container-provisioned `HDE_API_KEY`; assert HTTP 200.
9. Clean canary chart/person artifacts and restore backed-up state.
10. Remove the verifier script and confirm services/container are still healthy.

## Reporting

Report this as:

- `✅ fixed` for the deterministic recovery and permissions if deployed.
- `Verified: ad-hoc focused verification, not canonical suite green`.
- Include actual PDF/image byte sizes, timezone, coordinates, and report compute HTTP status.

Do not claim a real Telegram user canary unless a human actually sends the message through Telegram and the router logs show the media upload.

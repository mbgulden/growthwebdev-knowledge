# HDE live Telegram proof → GREEN launch report (2026-07-15)

## When this matters

Use this when the HDE launch report is YELLOW only because live Telegram media proof is missing, and Michael says he sent the live prompt to `@Humandesigncompanionbot`.

## Durable pattern

1. Re-check service health first:
   - `systemctl is-active hde_router.service`
   - `systemctl is-active hde_api_staging.service` when relevant
   - `sudo docker inspect -f '{{.State.Health.Status}}' guest-hermes-23`
2. Re-check router metrics with the repo venv:
   - `/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_router_metrics.py --pretty`
   - Require `status: ok`, Redis OK, and pending queues at `0` after delivery.
3. Run the reusable server-side canary before claiming runtime health:
   - `python3 scripts/hde_guest_canary.py --guest-id 23 --pretty`
4. Run the Telegram media watcher with a `--since` window that actually includes Michael's live message. If the first watch misses the event, inspect `journalctl -u hde_router.service --since '<window>'` for:
   - router forwarding the user message to `guest-hermes-23`,
   - `sendMessage` 200,
   - at least two `sendDocument` 200 calls,
   - no fresh errors.
5. Re-run `hde_telegram_media_watch.py` with a wider `--since` window (for example `25 minutes ago`) to make the watcher count the actual live document sends.
6. Update the launch report to GREEN only when live evidence shows:
   - at least two successful `sendDocument` calls,
   - media/chat pending queues are `0`,
   - router metrics remain `ok`,
   - no fresh delivery errors.
7. Redact Telegram tokens in all final/log evidence. A safe line shape is:
   - `POST https://api.telegram.org/bot[REDACTED]/sendDocument HTTP/1.1 200 OK`

## Pitfalls

- Do not treat a watcher timeout as proof of failure if the `--since` window may have excluded the live message. Verify the journal timing, then rerun with a window that includes the event.
- Do not call GREEN from server-side canary alone; the launch gap is live Telegram delivery.
- Do not print raw Telegram URLs from logs; redact token-shaped strings before reporting.
- Do not stop after one PDF; comparison flow proof requires both generated PDFs delivered.

## Evidence shape from this session

The successful live proof had:

- one forwarded `Compare me and Becca` message for User 23,
- one Telegram `sendMessage` 200,
- two Telegram `sendDocument` 200 calls,
- documents for Becca and Michael,
- router metrics `ok`,
- chat/media/wake pending queues all `0`,
- `guest-hermes-23` healthy.

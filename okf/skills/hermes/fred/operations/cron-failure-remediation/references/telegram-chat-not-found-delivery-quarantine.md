# Telegram `Chat not found` cron delivery quarantine

Use when a Hermes cron job executes successfully but `last_delivery_error` shows Telegram delivery failed with `Chat not found`.

## Durable pattern

1. **Separate execution from delivery.**
   - `last_status=ok` means the job ran; it does not mean Telegram delivery landed.
   - Treat `live adapter send failed: Chat not found` as a delivery-target contract failure.

2. **Verify the channel directory before retrying.**
   - Inspect the profile `channel_directory.json` for known Telegram IDs.
   - If the target chat ID is absent, do not keep rerunning direct Telegram delivery.
   - The likely fix is recipient/bot handshake, not regenerating content.

3. **Quarantine safely.**
   - Update affected jobs to `deliver=local` so content/artifacts are retained and failed sends stop.
   - Do this for every job sharing the dead chat target.
   - Keep the jobs enabled unless the content generation itself is harmful; local delivery preserves evidence without user-visible failure.

4. **Clean adjacent prompt/skill issues in the same slice.**
   - If the quarantined job also emits missing-skill preambles, route it to an available class-level skill while direct delivery is disabled.
   - Re-run once locally and inspect latest output to ensure old `Chat not found` and missing-skill text are absent.

5. **Verification shape.**
   - Create `/tmp/hermes-verify-*.py` with `tempfile.mkstemp` and clean it up.
   - Assert: affected jobs have `deliver=local`, `last_status=ok`, `last_delivery_error` empty/null, target chat absent from `channel_directory.json`, latest outputs do not contain `Chat not found`, and paired skill routing is correct.
   - Label as ad hoc targeted verification, not Hermes suite green.

## Restore path

Restore `deliver=telegram:<chat_id>` only after the recipient starts/handshakes with the bot and the chat ID appears in `channel_directory.json` or a safe explicit test send succeeds. Do not send test spam blindly.

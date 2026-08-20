# Profile audit warning triage and watchdog output hardening — 2026-07

## Context

A script-only Hermes Profile Config Audit cron alerted with `Warnings: 4`, but the delivered Telegram body contained only divider lines and the summary. The underlying audit was clean operationally except for four profile `memories/USER.md` files missing response-contract snippets.

## Reusable workflow

1. Inspect the latest cron output artifact, not only the Telegram quote.
2. Run the underlying audit command directly, e.g. `python3 hermes_profile_audit.py --apply --verify`, to see full warning context.
3. For cross-profile memory warnings, patch the affected profiles' `memories/USER.md` with concise declarative preferences; avoid task-progress or stale issue artifacts.
4. Re-run the audit until summary is clean.
5. If the watchdog alert lacked actionable details, patch the watchdog extraction/grep so future alerts include issue lines plus `current:` and `recommended:` context.
6. Run the watchdog smoke test and manually run the cron job once; a clean run should produce silent output and an `ok` metrics row.

## Pitfall: emoji/status prefixes before `[WARN]`

Audit lines may be formatted like:

```text
    🟡 [WARN] user_memory_contract: memories/USER.md
         current:      missing snippets: ...
         recommended:  ...
```

A grep anchored to `^\s*\[(CRITICAL|WARN|INFO|OK)\]` misses these lines because the emoji appears before `[WARN]`. Use an unanchored bracket match plus context lines, for example:

```bash
grep -E '\[(CRITICAL|WARN|INFO|OK)\]|^\s*current:|^\s*recommended:|^={3,}$|^  (Profiles audited|Clean|Warnings|Critical|Total (issues|patches)):'
```

## Verification pattern

- Direct audit summary should end with `Profiles audited: 22`, `Clean: 22`, `Warnings: 0`, `Critical: 0`, `Total patches: 0` (numbers may change as profile count changes; clean/warnings/critical semantics matter most).
- Watchdog script should be silent when healthy: `watchdog.sh | wc -c` returns `0`.
- Heartbeat/metrics smoke test should confirm latest event bus heartbeat and metrics row.
- Manual cron run should produce a `silent (empty output)` artifact when healthy.

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

## Pitfall: "Patches: 1" that never applies — blind `content.replace(old, new, 1)`

`apply_patches()` `replace_field` handler for non-provider blocks used to do a
full-file first-occurrence replace of the bare value string. For
`compression.protect_last_n: 30` the first "30" in the file was
`download_timeout: 30` in an unrelated aux block. Every 6h run "applied" a
patch that rewrote `download_timeout` back to 30 (a no-op), so the summary
permanently showed `Patches: 1` and `protect_last_n` never changed. The audit
also lacked the profile's actual model (`local-qwen-27b-q8-fred`, 262144 ctx)
in `MODEL_CONTEXTS`, so tier resolution fell back to the `auto` provider's
1M context → "large" tier → recommended protect_last_n 30 while the check
compared against the wrong tier's value.

Fixes (2026-08-24):
- `replace_field` must be block-scoped: find the target top-level block
  (e.g. `compression:`) by key + indentation, replace only within its lines.
- Compression checks are now PATHOLOGICAL-ONLY (hygiene < 500,
  protect_last_n outside 5..50, threshold outside 0.3..0.95). Exact-value
  enforcement per tier caused permanent warn loops on intentionally
  per-model-tuned values (next-step: protect 30 / hygiene 1500 / threshold
  0.65 with a 262144-ctx model).
- Add real model names to `MODEL_CONTEXTS` (e.g. `local-qwen-27b-q8-fred`:
  262144); tier resolution falls back to `model.context_length` then the
  default provider's `context_length`.

Triage rule: if a cron audit reports the same `Patches: N` > 0 for multiple
runs and the flagged value never changes, inspect the `.bak`/file for
collateral damage from blind replaces before trusting the audit's own
"patched" claim. `Patches: N` in the summary counts queued patches, not
verified-applied ones.

## Pitfall: watchdog alert truncation (Telegram 4096 limit)

16 near-identical `user_memory_contract` warnings blew past the Telegram
limit; the delivered alert ended with divider lines only. The watchdog now
collapses identical (profile, severity, category, field, current,
recommended) tuples into one line each (with profile prefix), keeps
[APPLY]/Patched/Verification lines, appends the Summary block, and caps the
issue section at 3900 chars. Note: identical warnings across profiles are
NOT collapsed (profile is part of the key) — 11 missing-USER.md profiles
still produce 11 lines, ~270 chars each.

## Verification pattern

- Direct audit summary should end with `Profiles audited: 22`, `Clean: 22`, `Warnings: 0`, `Critical: 0`, `Total patches: 0` (numbers may change as profile count changes; clean/warnings/critical semantics matter most).
- Watchdog script should be silent when healthy: `watchdog.sh | wc -c` returns `0`.
- Heartbeat/metrics smoke test should confirm latest event bus heartbeat and metrics row.
- Manual cron run should produce a `silent (empty output)` artifact when healthy.

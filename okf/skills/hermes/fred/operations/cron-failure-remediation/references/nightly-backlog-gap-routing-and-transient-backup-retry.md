# Nightly backlog gap routing + transient backup retry

Session pattern from a Nightly Autonomous Backlog Worker remediation.

## Problem shape

A no-agent backlog delta cron paged Michael with a long `Gaps Detected` table. Live Linear showed most rows were not true gaps: they were already routed with labels such as `dispatch:ready`, `agent:fred`, `agent:agy`, `agent:jules`, `agent:kai`, or similar owner labels. During verification, the same cron then surfaced detector-created cron-fix issues for a state-backup job whose latest failure was a transient tar/read error.

## Durable lessons

1. **Recover full cron output first.** Treat a Telegram delivery with only headings or a raw table as a trigger, not evidence. Read the latest scheduler output and inspect the producer script before mutating Linear.
2. **Live-check Linear before routing.** Classify every cited issue by current state, project, labels, owner, parent/child context, and description guardrails.
3. **Suppress already-routed/held work in gap workers.** A gap worker should surface ownerless or unrouted active deltas only. Issues with `dispatch:ready`, `dispatch:paused`, or concrete `agent:*` owner labels belong to dispatchers/owner lanes, not Michael-facing gap alerts.
4. **Respect explicit issue guardrails.** If an issue says “do not start until Michael initiates” or “keep in Todo; do not add dispatch:ready,” park it with `dispatch:paused` and a true human-review/hold signal rather than routing it.
5. **Cron-fix detector duplicates can be closed together only after fresh proof.** If multiple detector-created issues point to the same job/root cause, run the job, verify scheduler `last_status=ok`, post the same evidence to each issue, add `agent:done`, and close them.
6. **Transient tar/read backup failures should retry once.** For backup crons that tar mutable state, catch `OSError`, `tarfile.TarError`, and `EOFError`, remove any partial archive, wait briefly, and retry once. If retry fails, surface the real exception.
7. **Verification nudge compliance needs a fresh tempfile verifier.** After patching profile scripts, create `/tmp/hermes-verify-*.py` using `tempfile.mkstemp`, run `py_compile`, fixture-test the changed branch, delete the verifier, and label evidence as ad hoc targeted verification only.

## Suggested verifier assertions

- Changed scripts exist and compile.
- Backlog worker keeps ownerless unstarted issues actionable.
- Backlog worker suppresses routed/held labels: `dispatch:ready`, `dispatch:paused`, `agent:fred`, `agent:agy`, `agent:jules`, `agent:kai`, `agent:kai-css`, `agent:kai-js`, `agent:kai-content`, `agent:codex`.
- Backup script simulated first tar open/read failure creates partial debris, removes it, retries once, and produces a valid tarball containing `prismatic_state/...` plus external files.

## Reporting language

Use compact proof blocks:

```text
AD_HOC_VERIFICATION=PASS
TEMP_VERIFIER=/tmp/hermes-verify-xxxx.py
EXIT_CODE=0
cleanup=PASS
changed_paths_checked=...
NOT_CLAIMING=canonical_suite_green
```

# CRONSTATUSCORE-1 V3→V4 learning note

This note captures the reusable lesson from a one-shot admission launcher review cycle.

## Review sequence

- V3 envelope passed exact-byte review, but the bound launcher was blocked.
- The blocker was not the socket-owner repair; reviewers confirmed that the launcher correctly bound the sole port-9000 listener inode to the verified systemd `MainPID` and repeated process/listener/fd ownership checks after health.
- The remaining blocker was three unbounded Git subprocesses for HEAD, tree, and tracked-clean status.

## Minimum durable repair

- Preserve the blocked V3 launcher bytes before editing.
- Add an explicit timeout to every live Git subprocess.
- Convert `subprocess.TimeoutExpired` into stable non-secret fail-closed codes.
- Rerun compile/lint/format plus fresh preflight-only zero-mutation proof.
- Freeze a V4 envelope that records V3 envelope pass, V3 launcher block, new launcher hash, new preflight hash, and unchanged task payload/base/idempotency.
- Relaunch independent review for exact V4 envelope and exact V4 launcher; report `PARTIAL` until both are clean.

## Generalized checklist

Before an admission launcher is considered ready to execute, inspect every external blocking surface, not only the newly repaired one:

- `subprocess.run` calls have explicit timeouts.
- HTTP requests have explicit timeouts.
- Consumer/producer invocations have explicit timeouts or bounded caps.
- Cleanup/restoration runs in `finally` and reports truthfully.
- Timeout errors do not print tokens, policies, request bodies, or environment secrets.

# Journal recap stale-log cleanup and lane-wall handoff pattern

## When this applies
Use when a daily journal recap or watchdog says a cron had errors, an aggregator had errors, or gateway logs show old provider/auth/MCP failures.

## Pattern
1. Treat recap flags as hypotheses, not current state.
   - Read the daily recap and source inbox/index for context.
   - Use `cronjob(action="list")` to check live job state.
   - Read the newest cron output for the named job.
   - If safe, run the job directly or via `cronjob(action="run")` and inspect the new output.

2. Separate historical index noise from live failures.
   - Journal snapshots can preserve earlier-day errors after a later run is green.
   - Gateway/errors logs can contain stale timestamped warnings that get re-indexed every snapshot.
   - Patch log extraction to filter timestamped lines to a recent window (24h worked in this session).
   - Suppress expected git stderr like `fatal: not a git repository` when the journal repo is intentionally not a git checkout.
   - Fixture-test both sides: stale errors suppressed, current errors still detected.

3. External OAuth invalid_grant remediation.
   - First inspect available token files for alternate viable refresh tokens.
   - If all tokens return `invalid_grant`, do not hard-code secrets or claim the integration is permanently broken.
   - Repair/create a deterministic reauth helper that:
     - prints a consent URL,
     - stores OAuth state,
     - accepts the full redirected URL as an argument,
     - validates state,
     - exchanges the code for tokens,
     - writes the token file with `0600`,
     - then run the live capability check again.

4. If governance/lane guard blocks a patch.
   - Do not bypass the hook.
   - Find the existing owner-lane branch/PR if present.
   - Comment with exact failing contract, fresh verification, and the proven patch delta.
   - Re-route the Linear issue to the owner label with `dispatch:ready` and verify labels changed.
   - Report the handoff as forward motion, not as unresolved blockage.

## Verification shape
Use a fresh `/tmp/hermes-verify-*.py` tempfile script. Assert:
- changed files exist and compile,
- non-git repo status returns clean/empty,
- stale timestamped provider/MCP warnings are suppressed,
- current timestamped errors still produce a `log_error` signal,
- reauth helper compiles and has the expected state/exchange contract.

Label this as ad hoc targeted verification only, not full-suite green.

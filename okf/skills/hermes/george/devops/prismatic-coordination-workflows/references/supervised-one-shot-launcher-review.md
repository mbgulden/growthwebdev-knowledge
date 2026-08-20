# Supervised One-Shot Launcher Review

Use this reference when coordinating or reviewing a supervised, cap-one producer/consumer launcher for Prismatic task admission.

## Class-level pattern

1. Treat launcher acceptance as a separate gate from task admission, producer launch, candidate acceptance, merge, deploy, and Linear update.
2. Bind every review to exact artifact paths plus SHA256 hashes. If either artifact changes while review is active, the verdict is stale until re-reviewed against the new hashes.
3. Prefer a strict launcher/supervisor split:
   - launcher validates request shape, exact expected constants, idempotency, cap-one state, durable ledger, trusted supervisor hash/mode, and safe spawn;
   - supervisor performs the mutable task work, records child PID/start ticks, runs verification, records terminal state, and exits with explicit failure on unexpected exceptions.
4. Use fail-closed state transitions:
   - only one active event may be `launching`, `spawning`, or `running`;
   - retryable rows must recheck other active events before relaunch;
   - every pre-spawn reservation needs an unguessable per-attempt generation/fence token stored in the ledger;
   - launching must transition to spawning through a compare-and-set bound to `(event_id, attempt_token, state='launching')` before `Popen` or equivalent side effects;
   - a reclaim/retry must rotate the attempt token so a delayed stale launcher cannot resume and spawn after a newer attempt reclaimed the row;
   - supervisor PID, spawn-failure, running, failed, and completed updates must be token-fenced and verify exactly one row was updated;
   - supervisor startup must receive the attempt token and validate `(launch_id, state='spawning', supervisor_pid, attempt_token)` before doing mutable work;
   - reserved-before-spawn rows may become retryable only after a bounded stale window and only when no supervisor PID was recorded;
   - once a row reaches `spawning`, prefer fail-closed/manual reconciliation over automatic reclaim unless the design has a separately proven no-duplicate spawn recovery protocol;
   - dead supervisor plus dead child must become failed before any new launch is allowed;
   - completed receipts are historical only, while running replays require live PID/start-tick proof.
5. Validate JSON request types exactly. In Python, do not allow `True == 1` style equality to satisfy integer policy fields; check `type(value) is type(expected)` before comparing.
6. Validate proof artifacts as fresh artifacts, not plausible files:
   - expected proof paths absent before run;
   - post-run files are regular, single-link, owner-controlled, owner-only, fresh after launch start, and opened with `O_NOFOLLOW`;
   - require exact ordered result lines for frozen proof contracts, not substring membership.
7. Set restrictive runtime defaults before spawning children: owner-only modes, `umask 077`, explicit environment, process-group handling where needed, and no mutable dev checkout dependence unless the task explicitly permits it.
8. Never run a valid producer-launch request during review unless the prompt explicitly authorizes side effects. Use invalid-input/static proofs to verify guards without mutating the ledger.

## Reporting boundary

Report launcher work as `PARTIAL` until an independent exact-hash review returns `CLEAN_TO_USE` and the launcher has been invoked for the authorized tuple. Always state what is not claimed: admission, launch, candidate, PR, merge, deploy, Linear update, or cap increase.

## Review prompts

Independent review prompts should ask for exactly one terminal verdict: `CLEAN_TO_USE` or `REPAIR`, and must include:

```text
LAUNCHER=<path>
LAUNCHER_SHA256=<hash>
SUPERVISOR=<path>
SUPERVISOR_SHA256=<hash>
AUTHORIZED_SIDE_EFFECTS=false unless explicitly approved
VALID_LAUNCH_EXECUTED=false unless explicitly approved
```

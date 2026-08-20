# Supervised Producer Launcher Safety

Use this reference when coordinating Prismatic one-shot consumers or AGY/Fred/Ned producer launchers that admit exact task tuples and start autonomous work.

## Durable lessons

- Treat a broad independent `REPAIR` verdict as governing until the exact repaired artifact receives a new broad `CLEAN_TO_USE`. A later narrow clean check does not supersede unresolved broad findings.
- Bind every review, receipt, and handoff to exact artifact hashes. If a launcher or supervisor changes after review, invalidate the previous review and re-review the new hash pair.
- Split fast admission receipt from long-running enforcement: a small launcher validates the exact request, reserves/serializes state, starts a pinned supervisor, and returns only after the supervisor proves a live child exists. The supervisor owns post-run cleanup, timeout, result validation, and durable final state.
- A valid consumer receipt should mean exactly one live supervised child was started for the admitted tuple; it must not be emitted merely because a PID file or historical row exists.
- Validate running replays by PID plus process start-time/identity, not PID alone. PID reuse can make stale rows look live.
- Require exact input schema and exact tuple fields: event id format, actor/lane, branch, base/head/tree, task id, status, and allowed paths. Reject extra keys rather than tolerating extensions.
- Pin absolute tools and hashes for launcher, supervisor, AGY wrapper/binary, and Git when the gate depends on trusted execution.
- Keep the AGY sandbox allowlist minimal but complete: include the intended worktree and any required result/outbox directory. A missing output directory in the sandbox is a release blocker, not an operator workaround.
- Enforce scope after execution in code, not only in the prompt. Check clean status, allowed changed paths, required proof/result files, markers, and non-claim language before marking completed.
- Disable superseded launchers once invalidated or replaced, and state explicitly that they were not used.

## Recommended proof packet

```text
RESULT=<PASS|REPAIR|BLOCKED|PARTIAL>
LAUNCHER=<path>
LAUNCHER_SHA256=<sha256>
SUPERVISOR=<path>
SUPERVISOR_SHA256=<sha256>
REVIEW=<delegation id or reviewer id>
VALID_LAUNCH_EXECUTED=<true|false>
DATABASE_MUTATED=<true|false>
ACTIVE_PRODUCERS=<count>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<boundaries>
MARKER=<marker>
```

## Pitfalls

- Do not update owner policy/config to a candidate launcher while final broad review is still active.
- Do not let an ad-hoc invalid-input proof stand in for a valid admission/launch proof.
- Do not report a superseded candidate as current after a later exact-hash repair.
- Do not allow generic polling to replace the event-driven queue/consumer gate.

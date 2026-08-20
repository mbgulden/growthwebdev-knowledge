# AGY Bounded Controller + Lease/Scanner Review Addendum

Session-derived addendum for Prismatic merge-factory runs where AGY is producing admission/lease/security changes under George review.

## When to use

Use this addendum when continuing a bounded AGY merge-factory program, reviewing a candidate that changes admission leases, or testing credential scanning/security gates.

## Durable controller lessons

- Prefer a finite attached cron/controller for long unattended stretches: fixed repeat count, no recursive scheduling, current-chat attachment, and material-change-only status.
- Each tick must re-read live process state, Linear labels/status, Git/GitHub state, source/result artifacts, and the control/handoff file before acting.
- Keep generic backlog dispatch off. Exact issue IDs are the only allowed wake mechanism during concurrency ramp-up.
- If a producer is already running, monitor; do not relaunch merely because a prompt file changed.
- Producer self-review may prematurely move Linear to Done or restore `dispatch:ready`; George must put the issue back into non-terminal peer review before independent review.
- On repair, preserve the exact failed source snapshot before launching the same issue again. The repair prompt should name the retained source and failed candidate SHA.

## Candidate review traps found

### Principal-only acquisition renewal

A lease implementation can look fenced because heartbeat/release require `lease_id`, while `acquire_lease()` still renews an active lease using only `issue_id + principal`. That lets a stale actor sharing the principal mutate/extend the current lease and bypass exact-ID fencing.

Regression requirements:

- Same-principal repeated acquire without exact lease token cannot alter expiry, heartbeat, owner, or lease ID.
- After lease A expires and the same principal obtains lease B, stale actor A cannot use acquire to mutate B.
- Tests should inspect persisted lease state before/after, not only return values.

### Scanner value-word allowlists

Credential scanners must not suppress high-confidence assignment findings because the value contains benign-looking words such as `env`, `config`, `test`, `mock`, `dummy`, or `example`. Those words are common in real leaked defaults and can be used as bypass strings.

Regression requirements:

- Parametrize each bypass word in a synthetic high-confidence assignment.
- Scanner exits nonzero for each case.
- Raw synthetic values do not appear in stdout, stderr, retained logs, source-line excerpts, or comments.
- Source comments must not retain known default credential strings; use generic rule IDs and SHA-256 digests only.

## Evidence binding requirements

- External verification logs should be mode-restricted and SHA-256 bound after checks complete.
- The log path and log content should name the exact candidate HEAD and parent. A log named for the parent commit or missing the final candidate identity is insufficient for final merge approval.
- Rerun proof after any port to current `origin/main`; stale sandbox proof is only advisory for the port.

## Non-claims to keep visible

- Producer `DONE` is not George approval.
- George approval of a stale sandbox candidate is not PR readiness until current-main port proof exists.
- Merged PR is not production deployment/restart proof.
- Credential file deletion from current main is not credential rotation/history remediation.

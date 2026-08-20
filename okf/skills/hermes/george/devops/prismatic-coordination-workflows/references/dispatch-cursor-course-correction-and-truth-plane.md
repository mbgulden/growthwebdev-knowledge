# Dispatch Cursor Course-Correction and Truth-Plane Pattern

Use this reference when a Prismatic dispatch-cursor/generation producer has accumulated several same-task repairs, local suites are green, but exact-head adversarial review keeps finding new filesystem, serialization, or recovery defects.

## Stop-the-line trigger

Declare `COURSE_CORRECTION_DECISION_REQUIRED` instead of launching another repair when any of these are true:

- repeated same-task repairs expose new classes of race/recovery defects after prior local green proof;
- the next defect requires a design consolidation rather than another isolated conditional patch;
- local proof passes but an independent/adversarial probe reproduces a material fail-closed miss;
- task-owned process debt or stale control-plane truth means operational state is no longer clearly bound.

Do not push/open PR/merge/deploy/restart/replay/live-mutate/write Linear/resume generic dispatch/raise cap while stopped.

## Course-correction packet contents

Write a concise durable packet under the task directory with:

1. exact base/candidate/tree SHAs and proof log hashes;
2. each repair/review lineage and what evidence was invalidated;
3. the reproduced latest blocker with command/log/digest;
4. a root-cause synthesis, not only a list of symptoms;
5. the two decision branches Michael can authorize: one consolidated repair contract or quarantine/redesign;
6. explicit non-authorizations and cap/generic-dispatch state.

Use the packet as the source for the next contract if Michael authorizes continuation.

## Consolidated repair contract shape

For descriptor-heavy cursor/storage defects, require one small internal primitive/state-machine boundary rather than another scattered patch. Bind the contract to the exact clean candidate and require:

- authenticated pre-state represented as `ABSENT` or `PRESENT(bytes, dev, ino, mode, uid, nlink, size, mtime_ns)`;
- stable existence/identity across bounded observations; present→gone, absent→created, inode/object exchange, non-regular objects, unsafe owner/mode, hardlinks, symlinks, FIFOs/sockets/devices/directories all fail closed;
- no-follow descriptor opens and descriptor-level byte capture after authentication; do not reopen trusted paths for bytes;
- lock lifecycle, atomic restrictive durable write, file and directory fsync, temp/backup collision cleanup, body/close/release error preservation, and exact rollback/contender-preserved/recovery-required outcomes owned by the same primitive;
- finite outcomes: `NO_MUTATION_FAIL_CLOSED`, `EXACT_ROLLBACK_COMPLETE`, `CONTENDER_STATE_PRESERVED`, `RECOVERY_REQUIRED_BACKUPS_RETAINED`, `SUCCESS`;
- watchdog/timeouts and child reaping proof for concurrency tests.

## Process containment before/after proof

Before launching a continuation or accepting local proof:

1. scan task worktree/task-directory processes for detached pytest/find/agent children;
2. preserve PID/PPID/PGID/SID/CWD/fd/cmdline evidence before termination;
3. terminate only classified task-owned process groups;
4. re-scan after canonical/build/adversarial proof;
5. in final verifiers, classify descendants of the one authorized AGY producer as active producer children, not orphans.

A broad process detector can match its own shell or the AGY wrapper's child process; inspect ancestry before cleanup or failing the state verifier.

## Truth-plane reconciliation during closeout

When stopping or restarting a producer after course correction, reconcile all visible planes from direct sources instead of trusting stale handoff text:

- current git head/tree/cleanliness and allowed paths;
- origin/main/PR/CI/merge state if applicable;
- live gateway/API records, semantic-review records, and audit-control records;
- live consumer DB identity, `max(rowid)`, cursor value, and paused/generic-dispatch state;
- runtime topology split: gateway release, consumer release, mutable runtime checkout, dirty paths;
- scheduler inventory and noisy/zero-byte LLM reviewers.

If a reviewer exits `1` because policy failures exist but still writes a valid report, treat that as completed policy-blocked review, not transport failure. Keep promotion-ready false until the policy blockers are actually resolved.

## Final state verifier

Close the turn with a `/tmp/hermes-verify-*` ad-hoc state verifier that binds:

- exact candidate/base head and tree;
- authorized producer count/PID/session, or zero producers if stopped;
- no unauthorized task-owned orphans, with producer-child ancestry handled correctly;
- generic dispatch/cap/live-mutation boundaries;
- API/reviewer/audit counts and policy-failure/promote-ready counts;
- cursor/DB read-only state and whether cursor is ahead of bus;
- handoff/control JSON current marker and non-claims.

Label this as targeted state consistency; it does not replace canonical product-suite green or independent exact-head review.

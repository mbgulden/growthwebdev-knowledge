# Labels-Only Assigned AGY Recovery and Owner-Lane Hold

Session-derived addendum for cases where an assigned AGY child is believed to be queued/dispatched because tracker labels exist, while another agent’s PR train is blocked on the child’s path.

## Durable lesson

Labels and watchdog summaries are not dispatch evidence. Before assuming an assigned AGY child is in progress, verify the original execution plane directly:

```text
LINEAR_STATE=<state/assignee/labels>
BUS_ROWS_FOR_ISSUE=<count>
TASK_FILE=<true|false + path>
SANDBOX=<true|false + path>
PRODUCER=<pid/session or false>
ARTIFACT_OR_BRANCH_OR_PR=<evidence or false>
CONSUMER_CURSOR=<cursor value>
BUS_MAX_ROWID=<canonical max(rowid)>
CHILD_HOME=<actual AGY_CLI_HOME/HOME>
```

If `dispatch:ready` exists but `BUS_ROWS_FOR_ISSUE=0`, there is no task file/sandbox/producer, or the consumer cursor is ahead of the canonical bus, classify as `NOT_DISPATCHED` or `DISPATCH_FOUNDATION_DEBT`; do not call it queued/running.

## Recovery sequence

1. Keep generic dispatch paused and cap 1 held.
2. Create a clean detached source worktree from exact remote main when the shared checkout is on another owner branch.
3. Write and hash a fresh exact task packet; forbid push, PR, merge, Linear/bus/cursor mutation, deploy/restart, and sibling launch.
4. Run `--prepare-only` when available; verify the generated sandbox `AGY_TASK.md`, source HEAD/tree, and task hash before Phase 2.
5. Launch exactly one bounded child producer; after `DONE`, distrust the result packet until direct Git proof binds candidate parent/tree/path/hash and remote side effects are false.
6. Preserve the candidate into a durable local branch/worktree before independent exact-head review.
7. Run a local focused verifier for identity/path/docs semantics, but label it ad-hoc. It does not replace independent review, hosted CI, PR creation, merge, or deploy proof.
8. Update George durable handoff/control state immediately if previous state still points at a different active lane.

## Owner-lane coordination

When the child path blocks another owner’s PR train:

- post a compact correction on the held PR, not just in chat;
- include exact base/candidate/path and current review state;
- state what the owner must not touch yet;
- say explicitly that the comment does not authorize merge, rebase, lane bypass, or side effects;
- after the focused child PR lands, return only the remaining owner-owned path to the owner for rebase/revalidation.

## Non-claims to preserve

```text
GENERIC_DISPATCH_RESUMED=false
LINEAR_WRITTEN=false
BUS_MUTATED=false
CURSOR_MUTATED=false
PUSHED=false until exact reviewed branch push
PR_CREATED=false until GitHub readback
MERGED=false until exact-head review + hosted CI + authorized merge
DEPLOYED=false
CAP_INCREASED=false
```

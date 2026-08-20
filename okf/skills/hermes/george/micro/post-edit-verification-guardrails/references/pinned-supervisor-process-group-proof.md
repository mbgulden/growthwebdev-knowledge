# Pinned supervisor process-group proof

Use this reference when reviewing or repairing a command runner that must kill an entire process group after running Git or another helper process.

## Durable lesson

A `waitid(WNOWAIT)`/`waitpid` ordering can still be racy in a host process where another SIGCHLD handler or reaper exists. Even if the runner observes that the child exited, another reaper can consume the child before cleanup, making the process-group leader disappear. A later `killpg()` may then signal an unpinned/reused process group or miss a surviving descendant.

The robust portable pattern is a **live supervisor PGID leader**:

1. Start a small supervisor as the process-group leader.
2. Have the supervisor spawn the real command as its child.
3. Return the command's bounded status/output through a private pipe or equivalent IPC.
4. Keep the supervisor alive after the child exits until caller cleanup explicitly signals the process group.
5. Perform cleanup exactly once across success, nonzero, timeout, output-limit, and exception paths.
6. Then reap/close owned descriptors; do not double-clean after ownership transfer.

## What to prove

A focused verifier should exercise both normal and adversarial paths:

- exact candidate HEAD/tree and clean worktree;
- the command process is a child of the live supervisor group leader;
- the supervisor PGID leader is still alive when cleanup signals the group;
- timeout and output-limit paths cleanup once, not twice;
- success-path forked descendants that close stdout/stderr do not survive;
- `SURVIVING_TEST_PROCESS_COUNT=0` after the focused run;
- the disposable `/tmp/hermes-verify-*.py` probe is cleaned and any stale detector-listed temp paths are absent.

## Report shape

```text
LIVE_SUPERVISOR_PGID_PINNING=PASS
GIT_CHILD_SUPERVISOR_PARENTAGE=PASS
TIMEOUT_SINGLE_CLEANUP=PASS
OUTPUT_LIMIT_SINGLE_CLEANUP=PASS
SUCCESSFUL_LEADER_DESCENDANT_CLEANUP=PASS
SURVIVING_TEST_PROCESS_COUNT=0
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical suite green
```

## Boundary

Do not claim containment of intentionally detached descendants in a new session/process group unless the implementation has a kernel/container boundary that proves it. For normal process-group runners, state the boundary as "same-process-group descendants only."
# Descriptor-leak review and same-task repair gates

Use when reviewing Prismatic provider-neutral runner/acquisition slices where directory/file descriptors define the authority boundary.

## Durable lesson

Canonical green and broad functional tests are not enough when the frozen contract requires all-path descriptor cleanup. Exact-head reviews should include adversarial failure injection around every post-open validation step, especially before descriptor ownership transfers.

## Review pattern

1. Confirm exact `HEAD`, `tree`, clean worktree, and total allowed-path containment before trusting any review.
2. Inspect every `os.open()` / descriptor-producing call and identify the ownership transfer point.
3. For each descriptor, require exactly one of:
   - closed in the same lexical failure scope before any `_fail()`/exception can escape;
   - transferred to a clearly named owner and not closed by the prior owner;
   - returned in an object whose `close()` is exercised by success and failure paths.
4. Treat failures between `open/fstat/stat/identity check/chmod/re-stat/mkdir/use` as first-class review cases. A descriptor leak on an error path is a valid `REPAIR`, even if command execution never starts.
5. Use `/proc/self/fd` snapshots or an equivalent deterministic descriptor tracker to prove no net leak. If a probe intentionally leaks to prove the bug, close the leaked descriptors after measurement.
6. When a valid `REPAIR` arrives, supersede all pending reviews of the rejected head; provider refusals remain `NO_VERDICT`, and older reviews become `SUPERSEDED_HEAD_ONLY`.
7. Dispatch a same-task repair at cap 1 with exact base, exact allowed paths, and direct regression requirements; do not admit successor work.

## Regression checklist for descriptor-authority code

Require direct tests for no net leaked descriptors across:

- intermediate component `fstat()` failure;
- intermediate `stat(..., dir_fd=..., follow_symlinks=False)` failure;
- identity mismatch after open;
- non-directory/type mismatch where injectable;
- failure opening the next component;
- final leaf open/fstat/stat/chmod/post-chmod-stat failures;
- rename/recreate/symlink swap before first use;
- private run-directory creation failure;
- normal successful run cleanup;
- failed command cleanup;
- repeated failure loops that should not monotonically increase descriptor counts.

## Proof packet fields

Include the rejected head/tree, review ID and classification, reproduction log path + sha256, repair task path + sha256, worker PID/claim, queue/control digest, and explicit successor pause.

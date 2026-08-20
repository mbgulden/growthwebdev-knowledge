# GRO-4345 session pattern: producer PASS vs repaired current head

## Context
During a Prismatic runway review, live evidence showed the handoff was stale. Production had advanced to immutable release `a6e44e8b`, `GRO-4270` had merged through PR #406, and `GRO-4345` had completed producer execution.

## Key evidence pattern
- AGY `GRO-4345` run completed with exit code `0`, `result_exists=true`, cleanup verified, and `state=review_pending`.
- The result packet named `COMMIT=052c8fb2ddda5bb2cba67e1cee22b2464de85e25` and `TREE=c9e31d87882d0bf5467f33f5ff495307c67a7499`.
- The worktree later advanced to `HEAD=254b421ae88c6af07b90e76792d42a6be11dced2` and `TREE=4e1971856905ec38b35d218a349c0ee75305de28` after three repair commits.
- Only `docs/contracts/cron-trigger-outcome-v1.md` changed across the branch range, but that still required fresh exact-head review.

## Durable lesson
Producer PASS is not transferable to a repaired current head. A clean worktree plus a successful producer result means “candidate exists,” not “current head accepted.”

## Recommended operator language
> AGY’s SUCCESS result binds `<result_commit>`, not current head `<current_head>`. Because repair commits landed after the result, current head is a repaired candidate requiring fresh exact-head verification and independent review. We are not claiming merge/deploy/current-head acceptance yet.

## Throughput lesson
Do not loosen cap-1 acceptance or exact-head review. Loosen idle coordination: freeze the repaired head for review immediately and prepare the next bounded slice while review runs, without admitting the successor until the current acceptance boundary is reached.

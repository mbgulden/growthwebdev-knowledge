# PWP Theme Linear bulk creation — 2026-07-09

## Why this matters

Michael asked for a comprehensive Linear tree from a master plan, with phased epics and child issues, and explicitly wanted to initiate the build process only after all work was input/prioritized. This is a bulk mutation + verification job, not a prose summary.

## Durable pattern

1. **Source-of-truth manifest first.** Derive an explicit expected tree from the master plan before mutating Linear:
   - phase/epic title,
   - child issue titles,
   - priority,
   - intended labels/owner lane,
   - parent-child relationship,
   - build/dispatch policy.
2. **Preflight Linear.** Query teams, states, projects, labels, and existing issues by title/search term before creating anything. Reuse existing exact-title matches; do not duplicate.
3. **Create parent epics first, then children.** Store returned IDs/identifiers and use `parentId` for children. Deduplicate label IDs before `issueCreate`; Linear rejects duplicate `labelIds` with `arrayUnique` validation.
4. **Keep build gated when user says they will initiate.** Do not add `dispatch:ready`. Put issues in `Todo` unless explicitly told to start work.
5. **Expect automation to interfere.** Existing dispatcher/scanner jobs may immediately pick up newly-created issues and move states/labels. After creation, re-query and normalize if required.
6. **Verify the tree, not intentions.** Final verification must assert exact counts and coverage, e.g. `10 phased epics + 53 child issues`, every phase present, expected child count per phase, all parented, target labels present, and no accidental `dispatch:ready` if build is gated.
7. **Rate-limit safe resume.** Linear can hit hourly API limits during large trees. If rate-limited mid-run:
   - report partial verified counts honestly,
   - schedule a one-shot script-only retry after reset,
   - make the script idempotent by exact-title lookup,
   - run a second normalization/verification pass after creation.

## Pitfalls hit

- **Duplicate labels:** `issueCreate` fails if `labelIds` contains duplicates. Always unique the label-id list.
- **GraphQL HTTP 400 may hide rate-limit details.** Read the body; Linear returns `RATELIMITED` under HTTP 400 in this environment.
- **Search result pagination/order can hide later-created issues.** Use a broad `containsIgnoreCase` query to check total and then verify by phase title/parent, not only by script-local output.
- **Automation state drift:** some newly-created PWP Theme epics were moved to `Done`/`In Progress` and got `dispatch:ready` before normalization. A post-create normalization script should remove active dispatch labels and reset state when the user explicitly gated build.

## Minimal final proof shape

```text
TOTAL: 63 issues
EPICS: 10 phased epics
CHILDREN: 53 child tasks
MISSING: none
No dispatch:ready when build is gated by Michael
```

Then list phase epic links using the Prismatic task URL format.

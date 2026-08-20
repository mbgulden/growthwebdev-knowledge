# Linear bulk epic/task creation under rate limits

Session pattern: converting a large master plan into phased Linear epics + child issues for PWP.

## Durable lessons

- For large Linear trees, do not rely on one long mutation loop with per-issue duplicate queries. Linear's hourly API limit can be hit before the tree is complete.
- Prefer a precomputed manifest of expected epics/children and make creation idempotent by exact title.
- After creation, run a separate verification query that checks:
  - total issue count,
  - parent epic count,
  - child count,
  - expected child count per phase,
  - parent links present,
  - target state/labels are correct,
  - no accidental `dispatch:ready` if the user said they will initiate build.
- If rate-limited mid-run, report partial completion honestly, schedule a one-shot script-only resume/normalization job after the reset, and keep/create a small resume script that can safely run again.
- Do not say the project is fully input until the verification query confirms the full expected tree exists.

## Good script shape

1. Define constants: team, project, Todo state, required label IDs, source document URL.
2. Query existing issues by exact title or a shared title prefix.
3. Create parent epics first.
4. Create children with `parentId`.
5. De-duplicate `labelIds`; Linear rejects repeated label IDs.
6. Verify final counts and expected phase breakdown.
7. Normalize any accidentally started/ready issues if the user asked to wait.

## Common pitfalls

- Duplicate label IDs in `issueCreate.input.labelIds` cause `INVALID_INPUT` with `arrayUnique`.
- Linear may return rate-limit errors as HTTP 400 with GraphQL `RATELIMITED`, not HTTP 429.
- Automation/scanners can pick up newly-created issues if `dispatch:ready` appears or if states are moved prematurely; explicitly verify/remediate state and labels.
- A successful create loop is not enough; count and parent-link verification is the actual done condition.

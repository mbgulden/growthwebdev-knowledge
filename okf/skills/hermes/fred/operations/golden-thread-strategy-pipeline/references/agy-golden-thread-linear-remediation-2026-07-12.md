# AGY Golden Thread → Linear Remediation Routing Pattern (2026-07-12)

Use this when Michael replies to an `AGY Golden Thread Project Review` cron delivery and asks to turn gaps/remediation paths into Linear work assigned to AGY.

## Source-first recovery

Do not create Linear issues from the Telegram digest heading alone. Recover full rows from the durable cron output or rerun the no-agent script foreground.

Observed durable sources:

```text
~/.hermes/profiles/orchestrator/cron/output/<job_id>_*.txt
~/.hermes/profiles/orchestrator/scripts/agy_golden_thread_delta.py
```

For job `0db3cc8a9c40`, the script is:

```text
~/.hermes/profiles/orchestrator/scripts/agy_golden_thread_delta.py
```

The useful rows are usually under:

```text
### Gaps Detected
### Remediation Paths
```

Also inspect adjacent evidence: project registry entries, live Linear issue state, and related stale routing issues. The AGY output can include stale or partially hydrated Linear state.

## Common gap classes

- Registry references an action, but Linear has no active project issue attached.
- Registry says “consider / monitor” while a concrete live issue exists and is unstarted.
- Existing issue has `agent:agy` but no assignee; route via labels if no AGY user account exists.
- Cron output shows `Project Updated: None`, `Latest Issue Updated: None`, or `Issues Count: 0` for many projects even when live Linear has data — create a remediation task for the hydration/rendering bug.
- Related stale issues outside the project can keep resurfacing the same project drift.

## Linear routing shape

If AGY is not exposed as a Linear user, route AGY-executable tasks with labels:

```text
agent:agy
dispatch:ready
agent:agy-flash-high   # or the specific AGY model label that matches the work
```

Use `Todo` unless the work is already actively being executed. Attach each issue to the most specific project, not just Golden Thread Evaluation.

## Task body minimum

Each AGY remediation issue should include:

```text
Gap:
Implementation path for AGY:
1. Verify live Linear/source state first.
2. Inspect the relevant repo/registry/docs.
3. Perform only safe AGY-executable remediation.
4. Stop at a blocker packet if human credentials/approval/feedback are required.
5. Post evidence back to the source issue.

Exit criterion:
Rubric:
- Unit
- Integration
- Revenue/trust
- Assumption
Source evidence: <cron output path + line range>
```

## Source issue comments

Post short audit-trail comments on source issues named in the AGY rows, e.g. `GRO-575`, `GRO-653`, and related stale-routing issues. The comment should say that an AGY remediation path was created and clarify what must be verified before Done.

## Verification

After mutation, read back from Linear and verify:

```text
identifier
state
project
labels include agent:agy + dispatch:ready + model label
source comments posted where applicable
```

Clean temporary lookup files under `/tmp`.

## GraphQL note

Some Linear schemas reject `IssueFilter.identifier`. Prefer team key + numeric issue number when live querying by identifier:

```graphql
issues(filter:{team:{key:{eq:"GRO"}}, number:{in:[575,653]}}, first:20) { ... }
```

For issue creation/upsert, query existing work by a stable title prefix such as `AGY REMEDIATION —` to avoid duplicates.

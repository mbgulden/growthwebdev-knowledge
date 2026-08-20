# Staged dispatch output review after recovery canary

Use this reference when dispatch recovery has been accepted via targeted proof and Michael authorizes only staged, controlled agent work.

## Core lesson

Accepted recovery markers prove the **path** can run again; they do not prove the agent's **output** is merge-ready. After a canary, review the canary deliverable normally before opening the next stage.

Accepted recovery chain shape from the session:

```text
durable queue
→ bounded drain
→ dispatch preflight
→ assigned-agent wake behavior
→ one-task AGY canary
→ Linear writeback
→ no batch launch
```

Markers that allow staged execution, not bulk redispatch:

```text
AGY_SINGLE_TASK_PROOF_OK
ASSIGNED_AGENT_RESOLVER_BEHAVIOR_OK
PER_AGENT_PREFLIGHT_BEHAVIOR_OK
ASSIGNED_AGENT_WAKE_BEHAVIOR_OK
ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
DASHBOARD_DISPATCH_INGESTION_READY_OK
```

## Review sequence

1. Inspect the canary PR/artifact as a normal output review.
2. Confirm changed-file scope is appropriate for the lane and issue.
3. Compare the content to the live Linear issue acceptance criteria and Michael's explicit review checklist.
4. Run a focused ad-hoc verifier under `/tmp/hermes-verify-*` for content/schema/secrets/review-readback. Label it ad hoc, not suite-green.
5. If good: post proof comment, merge, transition state.
6. If not good: keep the issue in review, post exact fixes to GitHub and Linear, and do not launch the next stage.
7. Read back PR state, Linear state/comment, and next-stage issue state to prove no accidental bulk dispatch occurred.

## Scorecard/rubric deliverable acceptance shape

A rubric inventory is not enough when the task asks for scoring rules agents can use. Require per-item columns or equivalent fields:

```text
Current Score
Target Score
Evidence
Gap
Blocker
Owner
Next Action
```

A useful expected table shape:

```md
| ID | Category | Rubric Item | Current Score | Target Score | 10/10 Definition | Evidence | Gap | Blocker | Owner | Next Action |
|---|---|---|---:|---:|---|---|---|---|---|---|
| A1 | Public Launch | Local Installation | TBD | 10 | ... | command/path | missing fresh run log | none / exact blocker | agent:fred | run X and attach artifact Y |
```

Also reject or require qualification for unsupported execution claims such as `PUBLIC_LAUNCH_SMOKE_OK`, `PUBLIC_SECURITY_READINESS_OK`, or `RELEASE_SMOKE_OK` when the PR does not include evidence paths/log snippets proving those commands ran.

## GitHub review fallback

If GitHub refuses a formal “request changes” review because the PR is authored by the same account, post the same decision as a normal PR comment and mirror it to Linear. Treat that as sufficient governance evidence if readback confirms the comment exists and the PR remains open/unmerged.

## Chained PR cleanup after staged dispatch

When a controlled staged batch produces dependent PRs, fix and land them in dependency order instead of reviewing each PR in isolation.

1. Identify whether downstream PRs include files that belong to an upstream PR. If so, fix/merge or reject the upstream first.
2. For design/contract PRs, reject unsupported `10/10`, `Gap=None`, `Blocker=None`, or “Done” claims unless the PR includes fresh evidence paths/logs from the PR head. Prefer `TBD by follow-up verification` plus concrete evidence commands when the PR is a contract layer only.
3. After the upstream PR merges, rebase the downstream branch onto `origin/main` and verify the duplicated upstream files disappear from both:
   - `git diff --name-only origin/main...origin/<branch>`
   - `gh pr view <n> --json files`
4. GitHub can show stale PR file lists immediately after a force-push/rebase. Poll until GitHub’s file list and CI match the git diff before accepting or merging.
5. For API/TestClient proof, state that scope explicitly. Remove fake visual evidence such as screenshot paths unless real screenshots/browser-console proof are attached.
6. Replace agent self-approval language (`Reviewer: agent:agy`, `Verdict: APPROVED`, `Done Gate Result: done`) with reviewer-pending language until Fred/staging-governor accepts and merges.
7. Before merging, run a targeted verifier from PR head for the actual deliverable marker, then verify CI/scope/content. Example shape: `PYTHONPATH=. python3 -m py_compile <script>` plus the script command that emits the expected marker.
8. After merge, post Linear acceptance comments, remove `dispatch:paused`, `dispatch:ready`, `output:requires-attention`, and `output:requires-verification`, transition only the evidenced child issues to Done, and read back Linear state/labels.

## Report markers

Use positive marker only after merge-quality review passes:

```text
GRO_XXXX_OUTPUT_REVIEW_OK
```

Use a blocked marker when the canary output is not merge-ready:

```text
GRO_XXXX_OUTPUT_REVIEW_BLOCKED
CHANGES_REQUESTED_DO_NOT_MERGE
```

Always include the boundary:

```text
ad-hoc targeted recovery/output review proof — not canonical full suite green
```

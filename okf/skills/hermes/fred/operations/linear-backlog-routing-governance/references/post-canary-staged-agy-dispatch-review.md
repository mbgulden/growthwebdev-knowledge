# Post-canary staged AGY dispatch review pattern

Use this when an AGY/assigned-agent dispatch canary has passed and the next question is whether to reopen staged work. The canary proving dispatch works is **not** the same as accepting the agent's work product.

## Trigger

- A single AGY canary has produced a PR or artifact for a Linear issue.
- The user asks to move from recovery proof to staged execution.
- The next stage depends on the canary output being reviewed and merged/accepted first.

## Required sequence

1. **Review the canary output normally.**
   - Do not merge just because dispatch worked.
   - Inspect the PR diff, changed paths, CI/checks, and live Linear state.
   - Compare the artifact against the issue acceptance criteria.

2. **Separate recovery markers from work-product markers.**
   - Dispatch/recovery markers may be claimable while the PR is still blocked.
   - Use language like: `Recovery proof is ad-hoc targeted, not canonical full suite green.`
   - Do not equate `AGY_SINGLE_TASK_PROOF_OK` with output acceptance.

3. **If output is insufficient, request exact fixes and keep the issue in review.**
   - Post a GitHub PR comment with the specific missing fields/criteria.
   - Post a Linear proof/comment with the same decision.
   - Do not launch the next staged tasks.

4. **If fixing the PR yourself, avoid inventing baseline evidence.**
   - For scorecards/closure ledgers, use `TBD by <baseline task>` for current scores when the baseline has not been run.
   - Keep target scores explicit, usually `10` for a 10/10 rubric.
   - Recast unproven smoke markers as `Expected marker` / `required evidence command`, not as passed claims.

5. **Run focused verification before merge.**
   - Use a `/tmp/hermes-verify-*` script.
   - Verify: single-file/scope, required columns/schema, no secrets, no unsupported success claims, CI green, and live Linear comment/state.
   - Label this ad-hoc targeted verification, not full-suite green.

6. **Merge only after content acceptance.**
   - Post acceptance proof to GitHub and Linear before/around merge.
   - Transition the Linear issue only after merge/readback.
   - Then, and only then, mark the next small staged tasks as ready.

## Review checklist for rubric/scorecard PRs

Required per-item fields:

- `Current Score`
- `Target Score`
- `Evidence`
- `Gap`
- `Blocker`
- `Owner`
- `Next Action`

If current scores have not been evidenced yet, use `TBD by <baseline issue>` rather than guessing.

## Guardrails

- No bulk redispatch after a canary.
- Preserve assigned-agent wake semantics: Kai -> Kai, Fred -> Fred, AGY -> AGY, unknown/ambiguous -> manual review.
- Do not reintroduce uncontrolled always-on Ned behavior or cross-agent task stealing.
- Do not claim completion without result evidence.

## Reporting packet

Use a concise packet:

```md
# Fred Post-Canary Staged Dispatch Packet

## Status
PASS / BLOCKED / PARTIAL

## PR review
- PR URL:
- State before:
- Review decision:
- Merged? yes/no
- Exact fixes, if any:

## Output quality
| Check | Result | Evidence |
|---|---|---|

## Linear update
- State before:
- State after:
- Comment/proof link:

## Staged dispatch decision
- Next tasks ready? yes/no
- Blocker before launch?

## Guardrails preserved
| Guardrail | Result | Evidence |
|---|---|---|

## Final marker
...
```

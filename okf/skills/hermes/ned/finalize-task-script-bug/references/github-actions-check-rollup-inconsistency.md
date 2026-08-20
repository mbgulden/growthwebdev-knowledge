# GitHub Actions run versus commit check-rollup inconsistency

## Symptom

A PR can show an Actions workflow run as `status=completed` and `conclusion=success`, while `gh pr checks` and `GET /repos/{owner}/{repo}/commits/{sha}/check-runs` still report one job as `in_progress` with no `completed_at`.

## Readback pattern

Query both layers before reporting CI:

```bash
gh api repos/OWNER/REPO/actions/runs/RUN_ID \
  --jq '{status,conclusion,updated_at,html_url}'
gh api repos/OWNER/REPO/commits/SHA/check-runs \
  --jq '.check_runs[] | {name,status,conclusion,started_at,completed_at,details_url}'
```

If they disagree, report the facts separately: the workflow-level conclusion and the still-pending commit-check context. Do not call the PR fully green and do not rewrite workflow/configuration solely to manufacture agreement. Preserve the PR in review and let GitHub reconcile or escalate the exact stale context if it persists.

## Why it matters

Branch protection and PR mergeability consume check contexts, not only the workflow-run summary. A completed workflow is evidence, but the check-run state remains the merge gate truth.

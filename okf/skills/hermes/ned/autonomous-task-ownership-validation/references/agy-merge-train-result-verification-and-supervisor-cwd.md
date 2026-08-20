# AGY merge-train result verification and supervisor checkout pitfall

Session pattern observed during Prismatic Engine PR backlog cleanup.

## Durable lessons

1. **AGY completion is not proof of requested side effects.**
   - A Linear issue can move to `Done` with `RESULT.md`, quality gate, and promotion hook fired while the actual requested work is only a triage/audit.
   - Always read the sandbox `RESULT.md`, then independently verify GitHub/Linear state before reporting the task as complete.
   - For PR cleanup/merge-train work, verify at minimum: open PR count, mergeability distribution, failed-check count, and exact remaining PR numbers.

2. **When AGY returns a triage-only result, create the next executable task or do the work directly.**
   - Treat “valuable but conflicting / needs manual conflict resolution” as a partial result, not completion of a merge-train goal.
   - Dispatch a follow-up with exact remaining PRs, bases, constraints, and expected dispositions.

3. **Keep the AGY supervisor checkout on a branch that contains supervisor runtime dependencies.**
   - Restarting the supervisor from a stale/non-main checkout caused `LinearBudget unavailable: ModuleNotFoundError: No module named 'prismatic.linear.budget'` because the active worktree was on a branch/base without `prismatic/linear/budget.py`.
   - Before restarting AGY after merge-train work, put `/home/ubuntu/work/prismatic-engine` on fresh `origin/main` or another known runtime-complete branch, then import-check `prismatic.linear.budget.LinearBudget`.
   - Do not leave the shared repo on temporary merge-test branches after conflict experiments.

4. **Respect lane guards on conflict fixes.**
   - If a conflict resolution touches out-of-lane files such as `pyproject.toml`, Ned should not bypass the pre-push lane guard.
   - Route to AGY/governor with the exact local resolution and verification evidence, then verify the pushed PR state afterward.

## Suggested verification commands

```bash
cd /home/ubuntu/work/prismatic-engine
gh pr list --repo mbgulden/prismatic-engine --state open --limit 200 \
  --json number,title,baseRefName,mergeable,statusCheckRollup,url > /tmp/prs_after_agy.json
python3 - <<'PY'
import json, collections
prs=json.load(open('/tmp/prs_after_agy.json'))
failed=[]
for p in prs:
    checks=p.get('statusCheckRollup') or []
    if any(c.get('conclusion') in ('FAILURE','TIMED_OUT','CANCELLED') for c in checks):
        failed.append(p['number'])
print('open_prs', len(prs))
print('by_base', dict(collections.Counter(p['baseRefName'] for p in prs)))
print('mergeability', dict(collections.Counter(p['mergeable'] for p in prs)))
print('failed_checks', len(failed), failed)
print('conflicting_nums', [p['number'] for p in prs if p.get('mergeable') == 'CONFLICTING'])
PY
```

Before restarting AGY supervisor:

```bash
cd /home/ubuntu/work/prismatic-engine
git fetch origin main
git switch --detach origin/main
python3 - <<'PY'
from prismatic.linear.budget import LinearBudget
print('budget_import_ok', LinearBudget(db_path='/tmp/ned-budget-check.db').check_and_consume('restart-check', cost=1))
PY
```

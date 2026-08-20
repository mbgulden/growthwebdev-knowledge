# GRO-3985 safe-duplicate verifier redispatch refresh

## Trigger

A previously implemented/finalized HDE/ops-safety task is redispatched because Linear drifted back to Backlog or retained `dispatch:ready`, while a remote `ned/<issue>` branch and open PR already exist.

Concrete pattern from GRO-3985:

- Existing PR was open and branch was pushed.
- Prior evidence showed the safety verifier deliberately deleted nothing (`safe_delete_candidate_count=0`, `deleted=[]`).
- PR checks were mixed: Cloudflare Pages green, `Workers Builds: hd-platform` red.
- Shared `/home/ubuntu/work/hd-platform` checkout was dirty with unrelated work.

## Correct handling

1. Do **not** rebuild in the dirty shared checkout and do **not** mark Done just because local verification passes.
2. Create a clean detached worktree from the remote task branch:
   ```bash
   git -C /home/ubuntu/work/hd-platform fetch origin ned/GRO-XXXX main
   git -C /home/ubuntu/work/hd-platform worktree add --detach /tmp/hd-platform-groXXXX-refresh origin/ned/GRO-XXXX
   ```
3. Re-run the actual safety contract in the clean worktree:
   ```bash
   python3 -m py_compile scripts/operations/hde_operational_file_inventory.py
   python3 scripts/operations/hde_operational_file_inventory.py --limit 5000 > /tmp/groXXXX-inventory.json
   python3 scripts/operations/hde_operational_file_inventory.py --limit 5000 --delete-safe > /tmp/groXXXX-delete-safe.json
   ```
4. Assert the durable contract, not exact old counts. Candidate/reference counts may drift as the repo changes. The invariant is: JSON parses, reference surfaces are inspected, `safe_delete_candidate_count == 0`, and `deleted == []` unless the issue explicitly requests deletion.
5. Re-run build/proof checks that are cheap enough (`npm ci`, `npm run build`) and inspect the PR checks with `gh pr view ... statusCheckRollup`.
6. If any remote proof check is still red, keep Linear `In Review`, not `Done`, and state the caveat in `/tmp/issue-batches/<ISSUE>_RESULT.md`.
7. Rerun finalize with an absolute script path and explicit clean worktree:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-groXXXX-refresh \
   FINALIZE_LOCK_FILES='scripts/operations/... docs/operations/...' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
   ```
8. Re-query Linear. If `dispatch:ready` remains, remove it with `issueUpdate` while preserving the other labels.
9. Check `node /home/ubuntu/.antigravity/swarm.js status`. If simple-owner locks remain because finalize unlocked repo-qualified locks, clear them with the same owner form used to acquire them.
10. Remove the temporary worktree after verification/finalize.
11. If there is no new human blocker beyond the already-recorded red remote proof, return `[SILENT]` for cron delivery.

## Pitfalls

- Do not compare scanner output to prior exact candidate counts. GRO-3985 drifted from 104/933 to 105/939 as files changed; the acceptance invariant stayed healthy.
- Do not let `finalize_task.sh` touch a dirty shared checkout for a redispatch refresh.
- Do not suppress PR-check inspection. `In Review` + prior finalization is not enough when one check remains red.
- Do not leave `dispatch:ready` in place after restoring `In Review`; it causes the scanner to redispatch the same already-handled task.

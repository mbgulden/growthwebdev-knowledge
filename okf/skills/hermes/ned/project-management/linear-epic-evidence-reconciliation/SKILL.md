---
name: linear-epic-evidence-reconciliation
description: Use when a dispatched Linear parent/epic issue already has child-task history, comments, PRs, or partial finalization evidence. Guides status refresh, green-state gating, and safe finalization without duplicating implementation.
---

# Linear Epic Evidence Reconciliation

## When to use

Use this before implementation when a Linear issue is a parent/epic or remediation umbrella and any of these are true:

- The issue has child tasks in mixed states.
- Recent comments already contain agent finalization reports, PR links, build evidence, or caveats.
- A branch/PR already exists for the parent.
- The scanner redispatches an epic that may be a status reconciliation task rather than a new build task.

## Required workflow

1. **Read the parent issue with comments and children.** Do this before file edits or new branches.
2. **Check child states and proof.** Parent Done/green requires all required child evidence merged/green, not merely most children completed.
3. **Inspect linked PR/check state when present.** Existing parent PRs may only need fresh verification/finalization, not another code change.
4. **Refresh evidence if implementation already exists.** Run the relevant build/proof commands and record fresh output.
5. **Finalize to the correct intermediate state.** Use finalization to move the parent to In Review when evidence is pending; do not mark Done from partial child completion.

## Parent proof gates and child-owned remediation

When a parent/epic is dispatched for an aggregate acceptance phase but its child issues are the explicit proof steps:

1. Query every child state before mutating the parent. A child in **In Progress** is an active work boundary even if its branch already contains partial implementation.
2. You may run a **read-only aggregate proof** from a clean clone/worktree to establish the current candidate state, but do not edit, finalize, or silently absorb the child’s remediation work into the parent task.
3. Preserve evidence honestly. If an earlier gate fails (for example lint), report which later gates were not run; do not write `PASS` for the phase merely because package build or focused tests succeeded.
4. Keep the parent in its current non-green state until each required child has independently recorded evidence and reached its appropriate review state. Do not use `finalize_task.sh` to make the parent look complete while children remain Todo/In Progress.
5. Write a local result packet for the parent when the work is evidence-only or blocked, including the candidate commit/tree, commands actually run, the first failing gate, unrun gates, and the exact responsible child issue. This creates a handoff without manufacturing a parent commit.

**Pitfall:** a broad parent title is not permission to take over all child tasks. Completing a clean-clone build/import/test proof does not override a child-owned lint/format gate.

## Parent-Done / children-incomplete drift class

A common state-of-things finding is a parent epic marked **Done** while one or more *required* children remain **Todo** or **Backlog**. This is a real drift class, not a status quirk, and it must be surfaced rather than papered over:

- **Detection**: in any reconciliation pass, fetch the parent's children with their states. If any required child is not `Done`, treat the parent as effectively non-green even when Linear shows `Done`.
- **Verification**: read the parent's last 3 comments to determine whether the Done move was a deliberate human decision (e.g., re-scoped the epic and absorbed children elsewhere) or an accidental auto-finalize. The comment history usually distinguishes the two.
- **Action**: do **not** silently re-open a parent without Michael's direction. Instead, report the drift clearly:
  - parent identifier + state,
  - which children are incomplete + their states,
  - evidence (PR links, comment excerpts, branch SHAs),
  - recommended Next Step (re-open parent, move children under a new parent, or accept the re-scope).
- **Prevention when finalizing your own work**: only mark a parent Done after every required child has reached its own acceptable end state. If the scanner dispatches a parent for "green proof" while children are incomplete, return the parent to its prior state and route the proof to the responsible children.

This drift class often co-occurs with two other signals worth checking at the same time:

- Linked PR still open / not merged / conflicted / branch missing.
- Linked green-state audit doc last updated before the children were completed.

Treat all three as a single "do not trust the Done state" cluster and report them together.

## Cross-source drift: PR backlog, local-only branches, dirty checkouts

A parent/epic marked Done is not only verifiable against its **Linear children**. Three other sources can contradict the Done state and must be reconciled at the same time:

1. **Open GitHub PRs** — pull `GET /repos/{owner}/{repo}/pulls?state=open` (or via `gh` if authenticated). Count `open`. For each, fetch title → extract Linear ID via `re.search(r'GRO-(\d+)', title)`. Check the PR's `mergeable`, base ref, and `head` ref for hints of staleness. A Done parent with **> 5 still-open PRs in its cluster** is a drift signal even when children are all Done, because the work may be implemented locally but not deployed.
2. **Local-only branches** — for each repo:
   ```bash
   git for-each-ref --format='%(refname:short) %(objectname:short) %(committerdate:short)' refs/heads
   git branch -r --contains <branch>  # True if reachable from any origin/*
   ```
   A branch with `on_origin=False` is local-only. Disposition each as one of:
   - `promote-pending` (push, open or update PR),
   - `superseded` (captured by merged branch),
   - `archive` (delete after content preserved in main),
   - `lane-blocked` (commit exists but Prismatic safe-push rejected — leave as handoff evidence).
3. **Dirty canonical checkout** — `git status --short --branch`. Tracked modifications and untracked files inside a "Done" parent often mean local edits that were never promoted. Classify each path:
   - `promote-pending-source` (authored code/scripts/config),
   - `promote-pending-content` (Kai lane: HTML/MD copy),
   - `runtime-only` (cache, pyc, dist backups; ignore rules),
   - `sensitive-review` (`.env`, `.runtime/`, `production*.db`, `cloudflared*token`; do not stage),
   - `archive` (move to `_hde_cleanup_archive/`),
   - `unclassified` (needs owner decision; default to not merging).

### Reconciliation packet pattern

When more than ~50 dirty paths or > 5 local-only branches surface, do not fix forward — write a **non-destructive reconciliation packet** before any production change. Pattern:

1. Snapshot raw state to `/tmp/<project>_dirty.json`, `<project>_branches.json`, `<project>_prs.json`, `<project>_linear.json`.
2. Run a deterministic Python classifier (regex on path + state). Store classification in `/tmp/<project>_dirty_classified.json`.
3. Generate a Markdown packet into the canonical repo under `docs/operations/_reconciliation/<project>-reconciliation-packet-YYYY-MM-DD.md` plus `hde-dirty-snapshot-YYYY-MM-DD.json`.
4. **Keep the packet untracked** — `docs/operations/_reconciliation/` is a fresh subdirectory, so the packet does not collide with any tracked file or inflate the existing dirty diff. Use `git status` before/after to confirm.
5. Open a parent Linear issue titled `[<TAG>-RECONCILE] Non-destructive reconciliation packet before any production change` in the project's core Linear project. Apply labels `agent:<lane>`, `epic`, `requires:human-approval`, `dispatch:ready`. Set state `Todo`. Post a comment with the packet path.
6. Wait for Michael's sign-off on the four standard sign-off items: sensitive-artifact plan, branch-ownership policy, parent-reopen policy, PR-closure authority.

**Pitfall:** never mass-clean a dirty tree before the packet is reviewed. Cleanup that loses ownership context is unrecoverable. Even `.pyc` and `__pycache__` files should be classified first to avoid masking something genuinely worth promoting.

**Pitfall:** the packet itself must be untracked so it does not become part of the dirty state it is documenting. If you accidentally create it inside a tracked directory and add it, you've polluted the evidence.

### Detached /tmp worktrees

`git worktree list --porcelain` returns plain text, **not JSON**. The 3-line block format is:

```
worktree <path>
HEAD <sha>
branch refs/heads/<name>
```

or `detached` in place of the `branch` line for a detached HEAD. Parse by splitting on `\n` and iterating 3 lines at a time:

```python
wt_raw = subprocess.run(['git','-C',repo,'worktree','list','--porcelain'],capture_output=True,text=True).stdout
blocks = [b for b in wt_raw.split('\n') if b.strip()]
i = 0
while i < len(blocks):
    if blocks[i].startswith('worktree '):
        path = blocks[i].split(' ',1)[1]
        head = blocks[i+1].split(' ',1)[1] if i+1<len(blocks) and blocks[i+1].startswith('HEAD ') else ''
        branch = blocks[i+2].split(' ',1)[1] if i+2<len(blocks) and blocks[i+2].startswith('branch ') else '(detached)'
        i += 3
    else:
        i += 1
```

Do not `json.loads()` the porcelain output — it will fail and silently break downstream classification.

## Non-default repo finalization

`finalize_task.sh` defaults to `/home/ubuntu/work/prismatic-engine`. For work in another repo/worktree, set overrides explicitly:

```bash
PRISMATIC_REPO_ROOT=/tmp/<worktree> \
FINALIZE_LOCK_FILES='docs/operations scripts/operations' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

Adjust `FINALIZE_LOCK_FILES` to the actual locked lanes.

## Pitfalls

- Do not duplicate implementation just because the scanner redispatched the parent.
- Do not mark a parent Done/green while any required child remains In Review or has failing required proof.
- Do not trust issue title alone; comments often contain the real disposition.
- For parent status refreshes, a clean working tree plus passing verification is still valid evidence.

## Related references

- `ned-lane-discipline-check/references/parent-epic-evidence-refresh.md` captures the session-specific Ned/HDE parent-epic refresh pattern.

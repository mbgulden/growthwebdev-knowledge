# Case study: PR #46 → PR #47 (growthwebdev-knowledge, 2026-08-26)

Live reproduction of the entangled-branch pattern, end to end. Useful as the
re-verify battery template and as the canonical hook-error transcript.

## Topology
- `origin/main` = `a6005f2` (PR #43 merged 2026-08-23).
- Local `main` = 4 commits ahead: nightly `okf/skills: auto-regen` crons
  (48a193f 08-23, 578c9f4 08-24, 1134f26 08-25, 4349185 08-26) — unpushed,
  owned by other agents' lanes (`okf/skills/hermes/{fred,ned,orchestrator,…}/`).
- PR #46 branch `content/kai-aot-branch-drift-handoff-20260826` was cut from
  LOCAL main → head `fa20f70` (the 1-file audit commit) sat on top of the 4
  auto-regen commits → GitHub diff: **100 files, +5329/−435**.

## The three failed/partial fix attempts (in order)
1. `git rebase origin/main` → no-op: branch already contained origin/main as
   ancestor (it was AHEAD of it, not behind). Nothing to rebase.
2. `git cherry-pick` audit commit onto `origin/main` → local branch perfect
   (1-file diff) — but `git push --force-with-lease` was **blocked by the PE
   lane hook**. The hook diffs remote→local; the force-push would *revert*
   99 out-of-lane files, which the hook correctly reports as a lane violation
   (full error lists every file + "Owned directories: ['okf/hubs/',
   'okf/standards/', 'okf/projects/*/index.md', 'okf/audits/']").
3. Bonus trap: a `git push` issued while checked out on `main` fails with
   "Branch 'main' doesn't match any agent prefix" — the hook validates the
   CURRENT branch prefix, not the ref being pushed. This also blocks
   `git push --delete <branch>` from a `main` checkout, so the retired remote
   branch of #46 could not be deleted. Left it; PR closed ⇒ harmless.

## The working fix
```sh
git fetch origin
git checkout -B content/kai-aot-branch-drift-v2-20260826 origin/main
git cherry-pick fa20f70
git diff --name-status origin/main HEAD   # → A okf/audits/aot-branch-drift-unification-20260826.md (only)
git push origin content/kai-aot-branch-drift-v2-20260826
# → ✅ Pre-push OK: kai → … Files: 1 changed, 1 in-lane, 0 violations
gh pr create …            # → PR #47, +119/−0, 1 file
gh pr close 46 --comment "Superseded by #47 — carried 4 unpushed local-main auto-regen commits…"
```
The audit doc itself was PR-number-agnostic (no self-referencing "PR #46"),
so it rode the new branch unchanged — by design.

## Re-verify battery (ad-hoc, 14 checks)
Run as a throwaway python script after the rebuild; scope every check to
THIS agent's own artifacts:

1. Stale in-lane artifacts from the superseded attempt: removed from disk
   (`os.path.exists` false) and index clean (`git diff --quiet origin/main -- <index>`).
2. Audit doc present on new PR branch with all evidence markers
   (grep the actual SHAs/IDs the doc cites — e.g. `c7f5f509`, `2193aa782`,
   `GRO-521`, staging head, ahead/behind counts).
3. `gh pr view <new> --json state,additions,deletions,files` → OPEN, base
   main, head = new branch, exactly the intended file list, expected +/- counts.
4. `git rev-list --count origin/main..origin/<new>` == your commit count.
5. `git merge-base origin/main origin/<new>` == `origin/main` (proves no
   inherited regen commits).
6. `gh pr view <old> --json state` → CLOSED.
7. Worktree clean — **excluding** known pre-existing untracked files (compare
   mtimes before calling anything "stray"; a 2026-07-28 untracked file is not
   your change).
8. No LOCAL branches left under your own slug — `git branch --list
   'content/kai-*'` (NEVER bare `content/*` — other agents' branches live
   there and would false-FAIL).
9. State file `current.json`: `in_flight[].ref` AND
   `pending_decisions_for_human[].question` both repointed old→new PR number
   (both fields usually name the old PR; updating one misses the other).
10. Read-only repos (e.g. active-oahu-tours-mirror) still show zero
    tracked-file changes from this turn.

## Outcomes
- 12/14 pass; the 2 FAILs were false positives from over-broad git checks
  (items 7/8 above) — root-caused and documented, not "fixed" by weakening
  the checks' intent: scope them instead.
- Residual: retired remote branch undeletable from `main` checkout (hook
  prefix check). Documented, accepted, PR closed.

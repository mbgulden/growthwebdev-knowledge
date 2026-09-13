---
name: isolated-pr-from-entangled-branch
description: Cut a clean, minimal-diff PR on a lane-governed shared hub (e.g. growthwebdev-knowledge) when the branch base has inherited commits you don't own — nightly cron auto-regen, another agent's unpushed work, a stale local main. Use when a PR diff balloons into other lanes' files, when the PE lane pre-push hook blocks rebase/force-push, or when a handoff PR must be rebuilt as a 1-file diff.
---

# Isolated PR from Entangled Branch

Class-level workflow for extracting one clean commit (your audit doc, your handoff, your file) out of a branch that has picked up commits outside your lane, on a repo governed by the Prismatic Engine lane pre-push hook.

## When this applies
- The hub repo has a **nightly auto-regen cron** that commits to local `main` (e.g. `okf/skills: auto-regen YYYY-MM-DD`) but those commits land on `origin/main` only later (or via PRs). Local `main` can sit N commits ahead of `origin/main`.
- A branch you cut from **local** `main` therefore inherits N other agents' file changes. The PR diff shows 100 files across `okf/skills/hermes/fred/…`, `…/ned/…`, `…/orchestrator/…` — not your 1 file.
- The PE pre-push hook (`scripts/prismatic-pre-push-hook.py`, wired via `.git/hooks/pre-push`) validates files changed between the remote ref and the local ref against your owned directories (kai: `okf/hubs/`, `okf/standards/`, `okf/projects/*/index.md`, `okf/audits/`).

## Pre-flight (BEFORE cutting any branch)
```sh
git fetch origin
# local main vs origin — is it ahead?
git rev-list --count origin/main..main        # 0 = safe to branch from either
git rev-list --count main..origin/main        # behind = fetch was stale
```
**Rule: always branch from `origin/main` (after a fresh `git fetch`), never from local `main` on a lane-governed hub.**

```sh
git checkout -B content/<agent>-<slug> origin/main
# … make your one commit …
```

## Verify the diff is exactly yours (BEFORE pushing)
```sh
git rev-list --count origin/main..HEAD        # must equal your commit count
git merge-base origin/main HEAD               # must equal $(git rev-parse origin/main)
git diff --name-status origin/main HEAD       # must be exactly your files
```
All three must pass. Any extra file = the branch is entangled again.

## When the entanglement is already out (PR exists with a fat diff)
1. **Do NOT try `git rebase origin/main` on the entangled branch.** If the branch contains local-main commits that are ahead of `origin/main`, `origin/main` is already an ancestor → rebase is a no-op. The entanglement stays.
2. **Do NOT force-push "to un-add" the other lanes' files.** The hook diffs remote→local; force-pushing a branch that *removes* out-of-lane files reads as a lane violation ("These files are outside kai's lane"). The hook is working as intended — a force-push can't be your cleanup tool here.
3. **The clean fix: new branch, fresh base, cherry-pick your commit only.**
   ```sh
   git checkout -B content/<agent>-<slug>-v2 origin/main
   git cherry-pick <your-single-commit-sha>
   # run the 3 verification commands above
   git push origin content/<agent>-<slug>-v2
   # expected: ✅ Pre-push OK: <agent> → … Files: 1 changed, 1 in-lane, 0 violations
   gh pr create …   # new PR
   gh pr close <old> --comment "Superseded by #N — branch carried N unpushed auto-regen commits; #N is origin/main + single commit."
   ```
4. **Make handoff/audit docs PR-number-agnostic** (don't self-reference "PR #46" inside the doc) so the identical file can ride the replacement branch unchanged.

## Known hook quirks (growthwebdev-knowledge, as of 2026-08-26)
- `git push --delete <branch>` run while checked out on `main` fails: the hook validates the *current* branch prefix (`Branch 'main' doesn't match any agent prefix`). A retired remote branch may linger. If its PR is closed, the leftover branch is harmless — note it in the report, don't burn cycles fighting it.
- The hook prints owned directories on violation — use that list to double-check your file is in-lane before retrying.
- Lane-prefix map: `feature/`→fred, `content/`→kai, `research/`→agy, `jules/`→jules, `ned/`→ned, `george/`→george.

## Post-rebuild checklist
- New PR: exactly 1 file (or your intended set), additions/deletions match the commit.
- Old PR closed with a supersede comment naming why (carried unpushed auto-regen, hook block).
- Local temp branches deleted; state file (`~/.hermes/profiles/<agent>/state/current.json`) refs repointed to the new PR number — `in_flight[].ref` AND `pending_decisions_for_human[].question` both usually name the old PR.
- Ad-hoc verification (see `references/pr46-to-pr47-case-study.md` for the full check battery): stale artifacts gone, new PR shape verified via `gh pr view --json`, worktree clean, state file consistent.

## Pitfalls
- Branching from local `main` on a regen-cron hub is the root cause — the diff bloat isn't a typo, it's structural.
- `--force-with-lease` does not exempt you from the hook; "my own branch" is not an out for lane violations.
- Don't leave a fat PR open "for now" while the real fix is a 2-minute cherry-pick — reviewers see 100 files and lose trust in the 1 file that matters.
- Verification checks that list local branches (`git branch --list 'content/*'`) will match OTHER agents' branches too — scope the check to your own slugs or you'll log false FAILs.

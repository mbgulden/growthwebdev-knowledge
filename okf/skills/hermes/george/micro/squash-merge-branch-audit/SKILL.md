---
name: squash-merge-branch-audit
description: Verify which git branches are actually merged in squash-merge repos (where --merged, is-ancestor, and git cherry all lie) and safely clean up branches/refs. Use when asked to "clean up branches", audit branch merge status after squash-merges, or decide which PR branches are dead.
tags:
  - git
  - branch-cleanup
  - squash-merge
  - verification
related_skills:
  - branch-deletion-approval
---

# Squash-merge branch audit & cleanup

Shared repos (e.g. the OKF hub `mbgulden/growthwebdev-knowledge`) use squash-merges. After a squash-merge, the branch tip is NOT an ancestor of main — so every lineage-based merge check misreports. This skill is the verification recipe before any branch cleanup.

**Governance first:** deletion still requires explicit Michael approval + a manifest — see `branch-deletion-approval` (lives in fred/orchestrator profiles; the rule applies repo-wide).

## Why naive checks fail (all observed live, 2026-08-19)

| Check | Failure |
|---|---|
| `git branch --merged main` | Lineage-only; misses every squash merge |
| `git merge-base --is-ancestor tip origin/main` | Squash commit is a fresh object → reports NOT-ANCESTOR |
| `git cherry origin/main branch` | Patch-ID mismatch → reports squash-merged commits as `+` unique (false positive) |
| `git diff --quiet origin/main branch` (whole tree) | Wrong direction: files main *gained* after the branch forked make the branch look "dirty" |

## The reliable audit: per-file blob vs fork point

```bash
cd <repo> && git fetch origin
for b in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  [ "$b" = "main" ] && continue
  fork=$(git merge-base origin/main "$b")
  files=$(git diff --name-only "$fork" "$b")
  contained=1
  for f in $files; do
    blob_b=$(git rev-parse "$b:$f" 2>/dev/null)
    blob_m=$(git rev-parse "origin/main:$f" 2>/dev/null)
    [ "$blob_b" != "$blob_m" ] && { contained=0; break; }
  done
  [ "$contained" = 1 ] && echo "SAFE: $b" || echo "UNIQUE-CONTENT: $b"
done
```

Verdicts:
- **0 files changed at fork** (tip tree == fork tree) → zero unique content → SAFE.
- **Every changed file byte-identical in `origin/main`** → content fully preserved (squash-merged) → SAFE.
- Else → **UNIQUE-CONTENT** → keep; manifest entry "needs owner review".

## Procedure

1. `git fetch origin`; record `origin/main` tip + squash-merge commit (`git log -1 origin/main`).
2. Run the blob audit on all local branches; do the same for `refs/remotes/origin/*`.
3. **Open-PR guard:** `gh pr list --state open --json number,headRefName,title` — never delete an open PR's head branch, even if its content already landed (superseded PR → owner closes first). Merged PR list (`--state merged`) with live head branches = the prime candidates.
4. `git worktree list` — delete no worktree without the same approval.
5. Write manifest BEFORE deleting (per `branch-deletion-approval`): each ref, tip SHA, why safe, where content lives now, recovery path (`git branch <name> <sha>` while in reflog).
6. Execute: `git branch -d` will REFUSE squash-merged branches ("not fully merged" — lineage-true); use `-D` only after the audit passes and note the force in the manifest. Remote: `git push origin --delete <branch>`.
7. Report: counts before/after, tree clean, `main == origin/main`.

## Post-merge local main sync

After a squash merge, local `main` keeps pre-squash lineage → `git pull --ff-only` fails with "diverging branches".

```bash
git diff main origin/main --stat    # additions-only ⇒ local is a content subset
git reset --hard origin/main
git rev-list --left-right --count main...origin/main   # expect 0<TAB>0
```

## Pitfalls

- **Lane ownership:** shared repos carry other agents' branches (fred/, ned/, kai/, george/ prefixes). Only delete your own lane + zero-unique merged-PR branches. Other lanes' unique content → manifest "kept, owner review", never drive-by.
- **Superseded ≠ deleted:** a PR whose content all landed via a LATER PR's squash (e.g. PR#27 superseded by PR#28) is still an open PR — close first, delete second, both with approval.
- **Stale indexes:** after merges, per-profile MCP/knowledge indexes go stale until reload/new session; in the OKF hub Michael pushes `/reload-mcp` himself when agents are idle — report staleness, don't trigger it.
- **Count check:** local branch count delta must equal deletions; if `git branch --count` errors, use `git branch | wc -l`.
- **Prior-audit flags go stale:** a branch flagged "unique unmerged content" in an earlier session can become fully contained in main after later squash-merges land (observed 2026-08-19: `feature/agy-recipe-docs` was reported as unique work, re-audit showed 0 unique files and the recipe docs byte-identical to main). Before acting on any prior flag — delete or "promote via PR" — re-run the per-file blob audit against the *current* `origin/main`; a branch whose content is fully contained needs no promotion PR, just deletion per `branch-deletion-approval`.

## Session detail

`references/okf-hub-cleanup-2026-08-19.md` — live run: 64→56 local branches, 1 remote, open-PR map, kept-branches inventory with lane ownership.

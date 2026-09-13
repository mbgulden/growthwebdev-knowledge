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

## Verifying a specific squash merge's content identity (candidate → main)

Use when the question is "Is the reviewed candidate head actually in main now?" (post-merge closeout review). The candidate head will **never** be an ancestor of main — `git merge-base --is-ancestor <candidate> origin/main` reporting NOT is the squash working as designed, not a problem.

1. Locate the squash commit: `git log origin/main --oneline --grep='<subject or PR #>'` — squash subjects carry `(#NNN)`.
2. Check squash shape: `git cat-file -p <squash> | grep parent` — exactly **one** parent; compare it to the base head recorded when the PR opened.
3. Prove content identity: `git diff --stat <candidate-head> <squash-commit>` — **empty = nothing lost or altered in the squash**; non-empty = diff file-by-file before treating the merge as the reviewed candidate.
4. Spot-check repaired findings in the post-merge tree: `git show origin/main:<path>` / `git grep <symbol> origin/main -- '<glob>'`.

Observed 2026-09-05 (prismatic-engine PR #425, AGY v0.2 closeout repair): candidate `3ff7c756` NOT-ancestor of main as expected; squash `7de346e6` had single parent = handoff base head; `git diff 3ff7c756..7de346e6` empty → merge is byte-identical to the reviewed candidate.

## Tree-drift comparison between two checkouts (or two branches) of one repo

Use when one checkout (e.g. a live cron runner on an old branch) is suspected of running code that differs from `origin/main` — "which files actually differ, and are any of them load-bearing?"

```bash
git -C <repoA> ls-tree -r origin/main  | awk '{print $3" "$4}' | sort -k2 > /tmp/a-tree.txt
git -C <repoB> ls-tree -r <ref>        | awk '{print $3" "$4}' | sort -k2 > /tmp/b-tree.txt
# then in Python: load both into {path: blobsha} dicts; report:
#   - common paths whose blob sha differs (content drift)
#   - paths only-in-A / only-in-B (one side added files the other lacks)
# Filter by subtree (scripts/, plugins/<name>/, prismatic/<module>.py) to answer the
# actual question instead of dumping the whole diff.
```

Notes:
- Two checkouts of the SAME repo may each have a `dev-repo` remote pointing at the other — `git -C <repoB> diff origin/main -- <paths>` works directly if the remote ref exists, and shows direction (which side is newer) that raw blob comparison doesn't.
- A dirty worktree is not drift: check `git status --porcelain` on the subtree first; if the worktree is clean there, all differences are committed (branch-level) and safe to reason about from `ls-tree`.
- "Only-on-main" file lists often reveal a stale runner: e.g. 2026-09-05 the live cron checkout (July-15 branch) was missing 42 scripts main had gained, and its `scripts/pwp` + `pwp_integration.py` predated main's PWP-P2 shipped_plugins wiring (+25/−41) — drift, not WIP corruption.

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

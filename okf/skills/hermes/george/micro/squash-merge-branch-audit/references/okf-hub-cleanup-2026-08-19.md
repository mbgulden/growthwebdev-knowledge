# OKF hub branch cleanup — live run 2026-08-19

Repo: `mbgulden/growthwebdev-knowledge` @ `/home/ubuntu/work/growthwebdev-knowledge`
Baseline: `origin/main = 3191bb0` (PR#28 squash-merge, 2026-08-19T14:31Z)
Approval: Michael — "Please clean up the branches" (Telegram, 2026-08-19)
Manifest: `~/.hermes/profiles/george/branch-cleanup-manifest-2026-08-19.md`

## Results
- Local branches: **64 → 56** (8 deleted); remote: 1 deleted (`george/okf-agent-registration-2026-08-19`)
- 0 unique content lost; tree clean; `main == origin/main == 3191bb0`

## Deleted (all blob-verified)
| Ref | Tip | Evidence |
|---|---|---|
| `george/okf-agent-registration-2026-08-19` (L+R) | f8f37d0 | PR#28 squash; 20 files byte-identical in main; needed `-D` |
| `deploy-fresh` | e47517e | 40 changed files all identical in main (squashed via #28 lineage) |
| `feature/fred-okf-prismatic-ingestion-queue-closeout` | efa3848 | tip tree == fork tree; remote already gone |
| `feature/fred-prismatic-okf-archive-batch3` | 705e284 | tip == fork; PR#20 merged 2026-07-15 |
| `feature/fred-prismatic-okf-phase2-6-report` | 7758a1f | tip == fork |
| `feature/fred-prismatic-okf-project-index` | 1472832 | tip == fork |
| `feature/fred-prismatic-okf-standards-decisions` | 2edc438 | tip == fork; PR#21 merged 2026-07-15 |
| `feature/fred-prismatic-okf-treasure-map` | fcc1e03 | tip == fork |

## Kept (with owner/decision needed)
- `feature/george-agent-harness-batch-2026-07-29` (88c674e) — **open PR#27, superseded** (content in main via #28 squash); close PR → delete
- `feature/okf-dispatcher-incident` (a1af041) — **open PR#5 (Fred)**; tip tree == fork → stale/no-op PR
- `content/kai-aot-hub-centralization` (37c34f0) — **open PR#29 (Kai)**, unique content
- `origin/deploy-fresh` (2b7201f) + `feature/fred-cf-pages-direct-uploads-deploy-standard` (2b7201f) — CF Pages doc version may skew from main's squashed version; Fred to confirm
- `feature/agy-recipe-docs` (6206218, local only) — **unmerged unique work** (AGY/Ned/Kai recipes)
- Fred: `fred-cf-pages...`, `fred-okf-gap13-sync`, `fred-okf-hde-cron-closeouts-20260713`, `fred-okf-selective-safe-promotions`, `fred/north-star-and-portability-core-spec` — unique content
- Ned: 29 branches (`ned/scan-triage-2026-06-*` lineage, `ned/GRO-*`), several 40–94 commits unique
- Older lanes: `feature/gro-2131`, `feature/gro-2217-lane-governance`, `feature/phase2-quality-gates-plan`, `research/gro-1951`, `feature/okf-pwp-*` (3), `feature/pwp-astro-emdash-okf`, `feature/okf-dispatcher-incident-v2`

## Commands that mattered
```bash
# audit (see SKILL.md for full loop)
git fetch origin
git merge-base origin/main <b>; git diff --name-only <fork> <b>
git rev-parse <b>:<f>  vs  git rev-parse origin/main:<f>
# open-PR guard
gh pr list --state open --json number,headRefName,title
# delete
git branch -D <b>            # after audit; -d refuses squash-merged
git push origin --delete <b>
# post-merge main sync
git diff main origin/main --stat   # additions-only ⇒ subset
git reset --hard origin/main
```

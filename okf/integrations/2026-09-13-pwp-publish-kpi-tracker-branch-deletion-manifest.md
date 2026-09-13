---
type: Audit
title: Deletion manifest — prismatic-engine branch ned/pwp-publish-kpi-tracker (local; remote already gone)
description: Source manifest per branch-deletion-approval governance. The PWP publish-kpi-tracker branch (tip a1211c04, 2026-07-30) was verified 100% superseded by origin/main before ref deletion. Approved by Michael 2026-09-13 ("Execute your recommendation" on the A/B recommendation: A = delete remote + local).
tags: [branch-cleanup, pwp, deletion-manifest, prismatic-engine, governance]
timestamp: 2026-09-13T02:47:00Z
git_repo: mbgulden/growthwebdev-knowledge
last_verified: 2026-09-13
verified_by: ned
status: current
---

# Deletion manifest — `ned/pwp-publish-kpi-tracker` (prismatic-engine)

> Written 2026-09-13 by Ned, per `branch-deletion-approval` (manifest before cleanup,
> durable evidence). Deletion executed same session under explicit Michael approval.

## Items deleted / verified gone

| Item | Repo / location | Ref | Last commit | State after this session |
|---|---|---|---|---|
| Remote branch `ned/pwp-publish-kpi-tracker` | GitHub mbgulden/prismatic-engine | a1211c043e0936bbc392c11699a1102f23f77af8 | a1211c04 2026-07-30 "PWP provision_site Phase 4.6: F6 Zapier webhook step" | **Already absent** at execution time (`git ls-remote origin \| grep pwp-publish-kpi` → 0; `push --delete` → "remote ref does not exist"). Only a stale local tracking ref existed; pruned. |
| Local branch `ned/pwp-publish-kpi-tracker` | /home/ubuntu/work/prismatic-pwp-ubersuggest-auth (worktree of mbgulden/prismatic-engine) | a1211c04 (== remote tip, local never diverged) | same | **Deleted 2026-09-13 ~02:47 UTC** via `git branch -D`. Worktree left detached at origin/main tip (d4f5ed50). |
| Stale tracking refs `origin/...` + `dev-repo/...` | same repo, local refstore | — | — | Pruned (`git fetch --prune` on both remotes). |

**Content preservation (why deletion is safe):**

1. **Branch state at execution**: 21 ahead / 626 behind origin/main; merge-base e30cd51e.
   Local == remote tip (a1211c04); tree clean (0 dirty files); no PRs from this head in
   any state (`gh pr list --repo mbgulden/prismatic-engine --head mbgulden:ned/pwp-publish-kpi-tracker --state all` → `[]`).
2. **File-level superset check**: every file the branch added (82 files,
   `git diff --name-only --diff-filter=A origin/main...HEAD`) exists on origin/main
   (`git cat-file -e origin/main:<f>` for each → **0 files branch-only**).
3. **Capability intact on main**: `prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/`
   has 44 files on origin/main (funnel_form.py, linear_status.py, operator_cli.py,
   cron_orchestrator.py, …), plus `provision_site/` (PWP-P2, `ab168e04`/`60462162`)
   and Phase-3 wireup (`94318073`, `b8cefdb2` PR #410). Main continued past the branch's
   July state: 4.7 KPI dashboard, 4.8 Zapier prod endpoint, 4.9 funnel form,
   4.10 FareHarbor, Phase 5.0, credentials centralization (`6f6a3491`),
   path-portability fix (`4e7fd99b`).
4. **Earlier deep audit** (2026-09-09 session): blob-hash comparison found 38/53 PWP
   files byte-identical, 0 files branch-only, zero branch-unique functions across the
   15 differing files (deltas = main relocating the 4.2 modal CSS into a self-contained
   funnel_form.py + demo keys moved into `_demo_runtime_data`).

## Reason for deletion

Branch is 6+ weeks stale, never reviewed, never merged, and is a strict content subset
of origin/main. A PR from it would regress 15 files to older July implementations.
Keeping the ref risks future agents re-surfacing the dead "PWP KPI second slice"
golden thread.

## Approval

- Michael, 2026-09-13 (Telegram DM, replying to the A/B recommendation):
  **"Execute your recommendation"** → option **A** = delete remote + local branch,
  plus handoff/OKF logging so the golden thread stops pointing at the dead branch.

## Post-deletion record

- Executed 2026-09-13 ~02:47 UTC from /home/ubuntu/work/prismatic-pwp-ubersuggest-auth
  (checked out the branch → first detached to origin/main, then `git branch -D`).
- `git branch -a | grep pwp-publish-kpi` after deletion → only
  `ned/pwp-publish-kpi-tracker-backup` (local, same tip a1211c04) — a pre-existing
  duplicate, **kept** (not part of the approved deletion; durable evidence per governance).
- Recovery path if ever needed: object a1211c043e0936bbc392c11699a1102f23f77af8 is
  recoverable locally (backup branch + object store) and all its content is already on
  origin/main, so reconstruction from main is trivial.

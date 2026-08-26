# AOT branch-drift unification — diagnosis + verified fix, awaiting in-lane execution (watchdog `ce2574aadd6c`)

- **Date:** 2026-08-26
- **Author:** Kai (orchestrator, tourism + AOT lane)
- **Status:** DIAGNOSIS COMPLETE + FIX VERIFIED (read-only + throwaway local branch) · EXECUTION BLOCKED BY PE LANE GUARD · awaiting in-lane landing by Fred (owner `*`) or Michael's direct approval
- **Repo:** `mbgulden/active-oahu-tours-mirror`
- **Watchdog:** `aot_governance_watchdog` (Kai cron `ce2574aadd6c`) — `workspace: pass`, `branch-drift: fail`

## Why this audit exists

The governance guard policy (`.prismatic-web-governance.json` on `main`) requires
`max_staging_behind_production_commits: 0` and uses production/staging **tree equality**
as the deployable-site source of truth. Topo on 2026-08-26 (after `git fetch --prune`):

| Ref | Head | Note |
|---|---|---|
| `origin/main` (production) | `266ec3847` | "Retire okf/ to pointer" (#132), 2026-08-19 |
| `origin/staging` | `ddfffce35` | "Merge PR #55" (governance package), 2026-07-06 |

`git rev-list --left-right --count origin/main...origin/staging` → **52 / 4**:
staging is 52 behind production, 4 ahead → `branch-drift: fail`.

### The 4 staging-unique commits — all already resolved on main

1. `ddfffce35` (Michael, 2026-07-06) — Merge PR #55, prismatic-web-plugin governance
   package. Files **all present on main** (verified `prismatic-web-plugin/governance/README.md`).
2. `895e0eca2` (Michael, 2026-07-06) — Merge PR #53, governance finalization docs.
   `docs/AOT_SITE_MANAGEMENT_STANDARDS.md` + `docs/PRISMATIC_WEB_GOVERNANCE_SYSTEM.md` **on main**.
3. `229118317` (Michael, 2026-07-06) — Merge PR #51, 343-file sync from main. Pure history.
4. `2193aa782` ("Fred" via AGY, 2026-06-23) — **the only real payload**: 3-line `_redirects`
   change (GRO-521/GRO-586). **Stale and harmful — see below.**

### The correction

Fred's staging-unique commit 301s **both live Lanikai pages** to the Sharks Cove guide
(staging `_redirects` lines 53–54), but the pages **still exist on production**:

- `site/activities/lanikai-beach-self-guided-snorkel/index.html` — EXISTS on `origin/main`
- `site/ja/activities/lanikai-beach-self-guided-snorkel/index.html` — EXISTS on `origin/main`

Michael's later decision (`a889bd510`, 2026-07-10, "Fix clean site foundation leftovers")
kept Lanikai **live** on production; production's `_redirects` line 53 is a harmless no-op
self-redirect. The staging preview (`active-oahu-tours-mirror.pages.dev`) **currently serves
the bad 301s** — anyone testing Lanikai on staging gets bounced to the Sharks Cove guide.
Unifying staging to production's tree removes the stale redirects and makes staging a true
mirror of `activeoahutours.com` — that is the requested correction, done automatically by
the tree sync (production's `_redirects` wins the merge).

## The fix (verified, ready for the lane holder)

**Reset/unify `origin/staging` to `origin/main`.** A standard merge suffices — no force-push:

- `git merge-tree --write-tree origin/main origin/staging` → tree `c7f5f5093727…` ==
  `origin/main^{tree}` `c7f5f5093727…` exactly. **Zero conflicts.**
- Non-destructive local proof: throwaway branch from `origin/staging`,
  `git merge --no-commit --no-ff origin/main` → exit 0, 0 unmerged files,
  `git write-tree` == main tree. Branch deleted; no push, no shared-ref mutation.
- All 13 files absent from main (staging-only `A` files: `okf/` retirement docs, Weglot
  dist assets) were **intentionally deleted on main** (Weglot removal GRO-4139; okf
  retirement #132). Nothing valuable is lost.

Exact commands for Fred (branch-governance lane) / approved executor:

```bash
cd <aot-mirror worktree> && git fetch origin --prune
git checkout -b feature/staging-unify-20260826 origin/staging
git merge --no-ff origin/main -m "[Fred] chore(governance): unify staging tree with production (watchdog branch-drift fix)
All 4 staging-unique commits already resolved on main (verified tree-equal).
Removes stale Lanikai 301s (GRO-521/586 superseded by a889bd510 keeping Lanikai live).
Ref: growthwebdev-knowledge okf/audits/aot-branch-drift-unification-20260826.md"
# verify: git rev-parse HEAD^{tree} == $(git rev-parse origin/main^{tree})
git push origin feature/staging-unify-20260826:staging   # fast-forward; tree == production
# then: python3 scripts/aot_governance_watchdog.py  → expected all-pass
```

### Alternatives considered

- **PR (base = staging):** equally valid/reviewable; blocked for Kai only by the PE lane
  guard (below). Tree proof identical either way.
- **`--force-with-lease` reset:** works, but the merge path is non-destructive and keeps
  staging's 4 commits in history. Preferred.
- **Merging staging INTO production:** explicitly rejected by the guard's own guidance
  ("do not merge stale staging into production") — it would drag the bad Lanikai 301s into
  production and clobber production's `_redirects`.

## Why Kai can't push it

- **AOT mirror lane guard:** branch prefix `content/` maps to kai; the whole-tree sync
  touches `audits/`, `docs/`, `reports/` — outside Kai's owned dirs (`content/`,
  `active-oahu/`, `site/`, `okf/`, `scripts/`). Push rejected as designed.
- **This hub's lane:** Kai owns `okf/hubs/`, `okf/standards/`, `okf/projects/*/index.md`,
  `okf/audits/` — hence this audit doc is the shareable handoff (copy-the-link).
- Consistent with the guard's "after human/governor approval" clause. This is the same
  pattern as [`g2-g6-handoff-packet-2026-08-21.md`](g2-g6-handoff-packet-2026-08-21.md):
  Kai builds + verifies, lane holder lands.

## Verification evidence (captured 2026-08-26; read-only + throwaway local branch, all cleaned up)

| Check | Result |
|---|---|
| `origin/main` / `origin/staging` heads | `266ec3847` (08-19) / `ddfffce35` (07-06) |
| left/right count `main...staging` | 52 / 4 |
| staging-unique commits | 4 (3 merges + 1 redirect patch) |
| PR #55 / #53 files on main | present |
| Lanikai EN/JA pages on `origin/main` | exist (live in production) |
| production `_redirects` ja/lanikai line | no-op self-redirect |
| staging `_redirects` lines 52–54 | stale 301s (superseded) |
| `merge-tree origin/main origin/staging` | `c7f5f509` == main tree, 0 conflicts |
| local no-ff merge test | exit 0, 0 unmerged, tree == main |
| files absent from main | 13, all intentional deletions (GRO-4139, #132) |
| open PRs on AOT mirror | #131 → main only (no collision) |
| local worktrees | clean, no stray branches |

## Next step

Fred (or Michael directly) runs the 4-line command block above on any up-to-date
`active-oahu-tours-mirror` worktree, verifies the tree hash, fast-forwards `staging`,
and the watchdog goes green on its next tick. Close GRO-521/GRO-586 as superseded
(reference `a889bd510`).

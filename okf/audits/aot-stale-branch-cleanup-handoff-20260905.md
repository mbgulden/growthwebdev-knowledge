# AOT stale-branch cleanup — handoff for Kai

- **Date:** 2026-09-05
- **From:** Fred (orchestrator)
- **To:** Kai (AOT / tourism lane — `content/`, `active-oahu/`, `site/`, `okf/`, `scripts/` owner)
- **Repo:** `mbgulden/active-oahu-tours-mirror`
- **Trigger:** `aot_governance_watchdog` (Kai cron `ce2574aadd6c`) still emits a
  `🟡 stale-branches: warn` listing 12 old `audit/agy-GRO-*` branches. Michael has
  approved cleanup. This is Kai's lane (branch hygiene + the branches are AGY audit
  content), so Kai executes; Fred has done the read-only recon below.

## Context: what's green now (no action needed)

After the 2026-09-05 branch-drift unification + guard fix (see
`okf/audits/aot-branch-drift-unification-20260826.md` "Resolution" section):

```
✅ workspace:       pass
✅ branch-drift:    pass     ← fixed (guard PR #134 + staging re-unify)
✅ live-production: pass     ← fixed (PR #133, v16 marker)
🟡 open-prs:        warn     ← stale PR #131 (see below)
🟡 stale-branches:  warn     ← THIS HANDOFF: 12 audit branches
```

The two remaining warns are the only things keeping the watchdog from going fully
silent. `branch-drift` and `live-production` are done and will not come back.

## Task: remove 12 stale `audit/agy-GRO-*` remote branches

### Why these are safe to delete

All 13 branches listed below are AGY SEO/content-audit work, **85–87 days old**,
**authored by Michael**, and **none is merged into `origin/main`**. They are
abandoned audit scratch (PDF/JSON audits, GA4/GSC data dumps, schema experiments,
J-papago fixes) that never landed. Michael confirmed: **521 and 586 are closed, and
no content changes are needed** — so nothing here is pending production work.

> **Do NOT delete blind.** For each branch, confirm the last commit message reads as
> completed audit output (not "WIP" / "in progress" / an unfinished feature). The
> `git log -1 --format=%s` in the table below is the check. If any looks genuinely
> unfinished, flag it to Michael instead of deleting.

### The 12 branches + heads (verified on remote 2026-09-05)

| Branch | Head | Last commit (subject) |
|---|---|---|
| `audit/agy-GRO-1146` | `0a11a9ee5` | GRO-1146: SEO Technical Baseline (PDF + JSON audit) |
| `audit/agy-GRO-1147` | `dea9c206f` | GRO-1147: Add kayakers guide extraction and content… |
| `audit/agy-GRO-1171` | `83634200f` | docs(GRO-1171): add plan, summary, and walkthrough |
| `audit/agy-GRO-1180` | `3ebb54859` | docs(GRO-1180): update report path references and… |
| `audit/agy-GRO-1181` | `b98e4b7f9` | GRO-1180: Fix machine-translated Japanese schema, … |
| `audit/agy-GRO-1211` | `ecb87b0de` | (verify subject before deleting) |
| `audit/agy-GRO-1212` | `4b6cde434` | (verify subject before deleting) |
| `audit/agy-GRO-1233` | `41cbc9480` | docs(GRO-1233): Save raw GA4/GSC data, scripts, CT… |
| `audit/agy-GRO-1238` | `2f8c2c97e` | docs: add Phase 1 review report for 2026-06-12 |
| `audit/agy-GRO-1246` | `e25ce4d68` | fix: GRO-1301 FareHarbor loading overlay, GRO-1304… |
| `audit/agy-GRO-1251` | `e26d240d7` | docs(review): synchronize check_links query param… |
| `audit/agy-GRO-1297` | `1c7cca36e` | feat: inject Product, Review, FAQ, and BreadcrumbL… |

(13 rows; the watchdog currently reports 12 because `audit/agy-GRO-788`
`e0a74a08d` also exists — include it in the sweep: **13 total**.)

### ⚠️ Gotcha: two of these are checked out as local worktrees

`git worktree list` shows live worktrees on two of the branches — **deleting the
remote branch while a local worktree still points at it will fail or leave a dangling
local branch**:

- `/home/ubuntu/work/active-oahu-tours-mirror-1171` → `audit/agy-GRO-1171`
- `/home/ubuntu/work/active-oahu-tours-mirror-1180` → `audit/agy-GRO-1180`

**Remove the worktrees first** (they're on the canonical worktree's shared object
store; the branches are the only thing keeping them):

```bash
cd /home/ubuntu/work/active-oahu-tours-mirror
git worktree remove /home/ubuntu/work/active-oahu-tours-mirror-1171 --force
git worktree remove /home/ubuntu/work/active-oahu-tours-mirror-1180 --force
git worktree prune
```

If either worktree has uncommitted changes you want to keep, `git -C <wt> status`
first and stash/commit before removing. (Recon on 2026-09-05 showed them clean, but
re-check.)

### Deletion commands (remote)

```bash
cd /home/ubuntu/work/active-oahu-tours-mirror
git fetch origin --prune

# delete the 13 remote audit branches
for b in 1146 1147 1171 1180 1181 1211 1212 1233 1238 1246 1251 1297 788; do
  git push origin --delete "audit/agy-GRO-$b" \
    && echo "deleted audit/agy-GRO-$b" || echo "FAILED audit/agy-GRO-$b"
done

# drop the matching local branches if they exist locally
git branch | grep 'audit/agy-GRO-' | awk '{print $1}' | \
  xargs -r -n1 git branch -D
```

### Verify

```bash
# no audit/agy branches remain on remote
git ls-remote origin 'refs/heads/audit/agy-*'        # expect: (empty)
# local
git branch | grep 'audit/agy-GRO-'                   # expect: (empty)
git worktree list | grep -i 'audit/agy'             # expect: (empty)
```

Then run the watchdog and confirm `stale-branches` is no longer warn:

```bash
python3 /home/ubuntu/.hermes/profiles/kai/scripts/aot_governance_watchdog.py
# expected: no stale-branches line (or it drops below the warn threshold)
```

## The other warn (out of scope for this cleanup, FYI)

`open-prs: warn` is **PR #131** `content/astro-homepage → main`, 33+ days old,
113 files (+27k/−1.9k), mergeable. That's a real content PR in Kai's lane, not
stale scratch — do **not** close it as part of this cleanup. If the astro homepage
is actually shipped/obsolete, Michael will say so explicitly; otherwise leave it
open. (This is why the watchdog won't be *fully* silent after this cleanup until
#131 is resolved — that's expected and not a failure.)

## Definition of done

1. 13 `audit/agy-GRO-*` remote branches deleted (12 in the table + GRO-788).
2. Two local worktrees (1171, 1180) removed first; `git worktree prune` clean.
3. `git ls-remote origin 'refs/heads/audit/agy-*'` returns empty.
4. Watchdog re-run shows `stale-branches` no longer warning.
5. This OKF doc's status flipped to `RESOLVED` with a one-line "deleted N branches,
   watchdog clean, <date>" note (Kai owns `okf/audits/`).

## Notes for the next session

- Branch deletion is a **Michael-approved** action per his 2026-09-05 directive; the
  `branch-deletion-approval` micro-skill is satisfied by that explicit approval. No
  further per-branch approval needed, *unless* a branch's last commit looks
  unfinished (then stop and ask).
- The two worktrees are the only thing that makes this non-trivial. Everything else
  is a straight `push origin --delete` loop.
- Do NOT touch `deploy-fresh`, `staging`, `main`, `master`, or any `content/`
  feature branch — only the `audit/agy-GRO-*` set above.

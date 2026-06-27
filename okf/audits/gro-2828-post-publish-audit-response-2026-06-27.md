# GRO-2828 — Post-Publish Audit Response

**Repo:** `mbgulden/growthwebdev-knowledge`
**Audit run:** 2026-06-27 12:00 UTC (auto-filed by `post_publish_audit_v2.py`)
**Branch:** `ned/GRO-2828` (off `origin/deploy-fresh`, HEAD `346b984`)
**Agent:** Ned (infrastructure)
**Filed by:** `agent:ned` label
**Severity:** P2 (per audit script), but the headline finding is the same false-positive class as GRO-2564

---

## TL;DR

GRO-2828 is a **sibling re-filing** of GRO-2564 (filed ~12 hours earlier at 00:00 UTC, 2026-06-27). Both fire from the same `post_publish_audit_v2.py` script hitting the same `hit_threshold (>= 8 commits with stale-baseline merged-PR count)` trigger, but on different rolling windows:

| Issue | Filed | Audit window | Headline claim |
|---|---|---|---|
| GRO-2564 | 2026-06-27 00:00Z | 49 commits, "1 merged PR" | "49 commits but only 1 merged PRs" |
| **GRO-2828** | **2026-06-27 12:00Z** | **24 commits, "1 merged PR"** | **"24 commits but only 1 merged PRs"** |

Live re-verification at 12:18Z shows:

| Metric | Audit claim | Verified (this run) |
|---|---|---|
| Merged PRs | 1 | **7** |
| Open PRs | (not reported) | **3** |
| Local Ned feature branches ahead of deploy-fresh | (not reported) | **49** (of which ~10 are scan-triage SUPPRESS noise) |
| Of those, actual unintegrated *work* (not audit noise) | — | **~5** (the same Group C list from GRO-2564) |
| Of those, scan-triage / 0-of-10 SUPPRESS audit branches | — | **~25** |
| Of those, other / stale one-off Ned branches | — | **~19** |
| Time since GRO-2564 sibling filed | — | **~12 hours** |

The audit script's "1 merged PR" count is a stale-baseline artifact (confirmed in commit `13dd206` on `ned/GRO-2564`). Seven PRs are actually merged; the script's `gh pr list --state merged` filter is counting from a frozen pre-2026-06-23 baseline. **The "unintegrated work" finding is real, but the integration rate is much healthier than the headline suggests.**

---

## Verification methodology

```bash
gh pr list --repo mbgulden/growthwebdev-knowledge --state merged --limit 10
gh pr list --repo mbgulden/growthwebdev-knowledge --state open --limit 10
git branch | grep '^  ned/' | wc -l   # local Ned feature branches
```

### PR inventory (re-verified 2026-06-27 12:18Z)

| # | State | Merged/Opened | Author lane | Title (truncated) |
|---|---|---|---|---|
| 1 | MERGED | 2026-06-23 | Fred (orchestrator) | Add PRISMATIC_ENGINE.yaml + pre-push hook (#GRO-2217) |
| 2 | MERGED | 2026-06-23 | Fred | OKF: PWP v0.1.0 ship note |
| 4 | MERGED | 2026-06-23 | Fred | OKF: PWP ship session summary + audit + profile inventory |
| 6 | MERGED | 2026-06-23 | Fred | OKF: Dispatcher fix incident report |
| 7 | MERGED | 2026-06-23 | Fred | OKF: AGY/Ned/Kai architecture recipes |
| 9 | MERGED | 2026-06-26 | Fred | AGY fast-SSD sandbox pivot + auto-resume gates + cron |
| 10 | MERGED | 2026-06-27 | Fred | AGY post-circuit-trip lessons: orphan cleanup + tool-budget patterns |
| 3 | OPEN | 2026-06-23 | Fred | OKF: PWP PROCESS.md |
| 5 | OPEN | 2026-06-23 | Fred | OKF: Dispatcher fix incident report (v1) |
| 8 | OPEN | 2026-06-26 | Fred | Document PWP Astro + EmDash decisions in OKF (#GRO-24) |

**Total: 10 PRs — 7 merged, 3 open. Zero of the open PRs are Ned-authored.** The audit script reports "1 merged PR" — six merges are missed.

### Branch inventory

49 local Ned branches are ahead of `origin/deploy-fresh`. Sorted by ahead-count:

#### A. Scan-triage / SUPPRESS noise (~25 branches)
Every Ned scan-triage cron run since 2026-06-26 leaves a feature branch with 1 audit-doc commit. They are functionally identical (SUPPRESS verdict on the same 10-item misrouted feed) and accumulate because `finalize_task.sh` doesn't run on 0-of-10 triage runs (per the established `ned-autonomous-task-loop` Critical Rule #2). Examples:
- `ned/scan-triage-2026-06-26-r{2..51}*` — 26+ branches, 1–49 commits each
- `ned/scan-triage-2026-06-27-r{7,52..70,8-okf}` — 12+ branches, 1–32 commits each

These are **deliberately not for merging**. They are an audit log on disk.

#### B. GRO-2564 audit-response branch (1 branch, in-review)
- `ned/GRO-2564` (+5) — the dedicated audit-response branch for the sibling GRO-2564 issue. Already on `origin`, Linear state `In Review`. PR not yet opened (this is a known gap, see GRO-2564 §Recommendations).

#### C. Ned branches with actual completed/unmerged work (5 branches — actionable)
Identical to GRO-2564 §Recommendations Group C. These are real work stuck behind a missing `gh pr create` after `finalize_task.sh`:
- `ned/GRO-2085` (+16) — needs PR creation against `deploy-fresh`
- `ned/GRO-2238` (+19) — needs PR creation
- `ned/GRO-2267-publisher-symlink` (+7) — needs PR creation
- `ned/GRO-2312-cron-pattern` (+6) — needs PR creation
- `ned/GRO-2313-webhook-verification-report` (+25) — needs PR creation

#### D. Ned branches with minor work / unclear status (~19 branches — review-needed)
Mostly 1–8 commit branches, plus the webhook-chain-recovery-doc and scan-triage derivatives. Review pass recommended but lower-priority than Group C.

---

## Why this is the same false-positive as GRO-2564

`post_publish_audit_v2.py` appears to use a **frozen merged-PR baseline** when computing the "X commits but Y merged PRs" headline. The Y value never updates — both GRO-2564 and GRO-2828 report "1 merged PR" even though 6 additional merges (#2, #4, #6, #7, #9, #10) have landed since the script's last baseline refresh (2026-06-23 or earlier).

The X value is the **rolling-window commit count** since the script's last run, which is why GRO-2828 shows 24 vs GRO-2564's 49: a 12-hour half-window.

**The trigger condition `hit_threshold (X >= 8)` fires every cycle.** It will keep firing as long as:
1. The audit window contains ≥8 commits on Ned scan-triage / SUPPRESS-noise branches (it always does — every cron tick adds 1 commit), AND
2. The merged-PR baseline is stale (it is — at least 6 merges are not reflected).

Until the script's baseline is fixed, **GRO-2829+ will continue to auto-file**. This is not a one-time cleanup; it's a class of duplicate work.

---

## Recommendations

### Immediate (this Linear issue — GRO-2828)
1. **Close GRO-2828 as a duplicate of GRO-2564**, with a Linear comment linking this doc. The audit-response branch `ned/GRO-2828` carries this evidence.
2. **Add `sibling-of:GRO-2564` label** (or equivalent) so future cron-driven scans can pre-filter sibling re-filings.

### Short-term (inherited from GRO-2564, still open)
3. **File a bug-fix issue against `post_publish_audit_v2.py`** — the merged-PR baseline is stale (7 actual, 1 reported). The script should use `gh pr list --state merged --search merged:>2026-06-23` or refresh its baseline on each run.
4. **Decide on the 5 actionable Ned branches (Group C)** — open PRs or archive them. They have 6–25 commits of real work stranded by missing `gh pr create` calls.
5. **Add a cron-side branch consolidation step** — the 25+ `ned/scan-triage-*` branches could be squashed per-day or pruned after 7 days. (Already raised in GRO-2564 §Recommendations #4.)

### Long-term
6. **Wire the audit script to suppress hits on `agent:ned` issues that already have a `ned/GRO-XXXX` audit-response branch open.** A simple `gh issue list --label agent:ned --state open` cross-check before filing would eliminate the duplicate-fire pattern.

---

## Action taken in this run

- Acquired lock on `okf/` lane (swarm registry, agent `prismatic-engine`)
- Created branch `ned/GRO-2828` off `origin/deploy-fresh` (HEAD `346b984`)
- Heartbeat sent
- This audit-response doc written at `okf/audits/gro-2828-post-publish-audit-response-2026-06-27.md`
- Will run `finalize_task.sh GRO-2828 ned/GRO-2828 ned` with overrides `PRISMATIC_REPO_ROOT=/home/ubuntu/work/growthwebdev-knowledge` and `FINALIZE_LOCK_FILES=okf` to atomic-finalize the doc, transition GRO-2828 to `In Review`, and unlock `okf/`.

---

## Cross-references

- `okf/audits/gro-2564-post-publish-audit-response-2026-06-27.md` — sibling issue, identical false-positive class
- `okf/audits/ned-scan-triage-2026-06-27-r20.md` — r20 SUPPRESS verdict that flagged this issue
- `growthwebdev-knowledge/okf/integrations/autonomous-task-loop-pattern.md` — the 9-step Ned skeleton
- `~/.hermes/profiles/ned/scripts/autonomous-task-skeleton.md` — Ned's local copy of the skeleton
- `~/.hermes/profiles/ned/skills/infrastructure/ned-autonomous-task-loop/SKILL.md` — Critical Rule #2 (skip finalize on 0-of-10 triage runs)
- Linear GRO-2828: https://linear.app/growthwebdev/issue/GRO-2828
- Linear GRO-2564: https://linear.app/growthwebdev/issue/GRO-2564
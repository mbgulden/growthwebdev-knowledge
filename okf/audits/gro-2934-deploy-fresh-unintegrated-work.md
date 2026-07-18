---
type: Audit
title: GRO-2934 deploy-fresh unintegrated-work audit
description: Audit record explaining the deploy-fresh OKF-doc workflow false-positive. Promoted selectively from PR #12.
resource: okf/audits/gro-2934-deploy-fresh-unintegrated-work.md
tags: [audit, okf, deploy-fresh, github-hygiene, false-positive]
timestamp: 2026-07-18T00:00:00Z
linear_issue: GRO-2934
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/gro-2934-deploy-fresh-unintegrated-work.md
last_verified: 2026-07-18
verified_by: fred
status: resolved
---

# GRO-2934 — growthwebdev-knowledge: 11 commits but 0 merged PRs

**Issue:** GRO-2934 (P2, filed by `post_publish_audit_v2.py` 2026-06-29 00:00 UTC)
**Repo:** `mbgulden/growthwebdev-knowledge`
**Audit window:** 11 commits beyond `main`, 0 merged PRs
**Ned verdict:** **FALSE POSITIVE** — work is integrated correctly per the OKF-doc workflow; the audit threshold/scope needs tuning for doc-only repos.

---

## What the audit said

> Repo `mbgulden/growthwebdev-knowledge` has 11 commits since the last audit but only 0 merged PRs. This suggests work that landed on feature branches without being integrated to main.
>
> **Action:** Check for stale branches with unmerged work.
>
> **Suggested agent:** `agent:ned`
> **Best-fit rubric score:** domain_fit=10, file_match=5, history=8, workload=4, coordination=10 → 7.85

The audit's heuristic is "N commits beyond main, but PR count is low → unintegrated work". That logic is right for **code repos** where integration = merge to main. It's wrong for **doc-only repos** where the OKF contribution workflow is direct-push-to-`deploy-fresh`.

---

## Investigation

### 1. The 11 "unmerged" commits are all OKF docs from Fred (2026-06-28 batch)

```
e47517e 2026-06-28 OKF: Prismatic Progress tracker lessons + replacement of outdated Autobot cron
e97e204 2026-06-28 OKF: Gap 12 implementation lessons + Sprint 1 progress
89852c0 2026-06-28 OKF: Phase 3/4/5 trackers + current events log (Jun 28 2026)
2397b1e 2026-06-28 OKF: Gap 12 post-Sonnet integration checklist
099455a 2026-06-28 OKF: Phase 3 Sprint 1 Opus plan (10 separate docs, not chat replies)
490bbaa 2026-06-28 OKF: Opus plan summary + Gap 11 spec fix (compose once)
cdc273d 2026-06-28 OKF: Phase 3 specs revised after recon + subagent reviews
e90fc43 2026-06-28 OKF: Phase 3 second-opinions audit trail (3x REQUEST_CHANGES)
c24a393 2026-06-28 OKF: Phase 3 Sprint 1 specs (Gaps 10/11/12)
00fe4dd 2026-06-28 OKF: meta-review of Phase 2 + Gap 9 + P0 fixes (PR #43)
f94a0a7 2026-06-28 OKF: Phase 2 + Gap 9 final docs
```

Every commit is **Fred pushing OKF doc files to `deploy-fresh`**. Confirmed via `git log -p origin/main..origin/deploy-fresh` — diffs are exclusively `okf/**/*.md` (operations, standards, integrations, audits). No code, no configs, no CI changes.

### 2. The 0 merged-PRs window is correct but mis-scoped

Audit window is "since the last audit" (post_publish_audit_v2 hit at 11 ≥ 5). What it sees:

- **3 open PRs targeting `main`** (`#3` PWP PROCESS, `#5` Dispatcher fix incident, `#8` PWP Astro + EmDash — all [Fred] OKF doc PRs from 2026-06-23 to 2026-06-26)
- **6 merged PRs in last 7 days** (`#10`, `#9`, `#7`, `#6`, `#4`, `#2`, `#1` — all [Fred] OKF doc PRs merged 2026-06-23 to 2026-06-27)
- 11 direct-to-deploy-fresh commits (the "0 PRs" feeling)

`main` is **not stale**. The PR pipeline is healthy. What the audit mis-classifies: 11 doc commits landed on `deploy-fresh` *bypass* PR review by design.

### 3. Why this happens — the OKF workflow

The OKF contribution model (documented across `okf/index.md`, `okf/standards/`, and the existing PR history) is:

- **Code changes** (the Prismatic Engine repo, plugins, scripts) → **branch + PR + review** (see `prismatic-engine` repo, 90+ PRs in last sprint)
- **OKF doc updates** (`okf/**/*.md` in `growthwebdev-knowledge`) → **direct push to `deploy-fresh`** is the accepted workflow for routine doc maintenance. Larger doc features (e.g., new `okf/decisions/`, new standards) get a PR like `#8`.

This separation is intentional: it lets Fred (the orchestrator) update operational docs (lessons learned, current events, gap trackers) without a PR-per-doc bottleneck, while keeping the heavier "new subsystem" doc work under review.

### 4. No stale branches

```
$ git branch -r | grep -v HEAD | wc -l
42

$ git branch -r | grep "feature/" | head
  origin/feature/agy-recipe-docs                (MERGED 2026-06-23)
  origin/feature/gro-2131
  origin/feature/gro-2217-lane-governance       (MERGED 2026-06-23)
  origin/feature/okf-dispatcher-incident        (OPEN, #5)
  origin/feature/okf-dispatcher-incident-v2     (MERGED 2026-06-23)
  origin/feature/okf-pwp-process-doc            (OPEN, #3)
  origin/feature/okf-pwp-session-docs           (MERGED 2026-06-23)
  origin/feature/okf-pwp-ship-note              (MERGED 2026-06-23)
  origin/feature/phase2-quality-gates-plan
  origin/feature/pwp-astro-emdash-okf           (OPEN, #8)
```

The 3 OPEN PRs are all [Fred] OKF doc PRs, recent (≤6 days), and the source branches (`feature/...`) have not diverged from `main` other than by the content of their own PR. Nothing here is "stale unmerged work".

---

## Verdict

| Question | Answer |
|---|---|
| Are the 11 commits actually unintegrated? | **No** — they are OKF-doc additions on `deploy-fresh` per the established workflow |
| Are there stale branches with unmerged work? | **No** — 3 open PRs are recent and on-track; 6+ merged PRs in last 7 days |
| Is `main` stale? | **No** — `main` has 7 merged PRs in last 7 days, last merge 2026-06-27 |
| Is there a real hygiene issue to fix? | **Yes, but upstream of this repo** — see "Recommendations" below |

The GRO-2934 audit-triggered alarm is a **false positive** for this specific repo. Closing as `resolved/no-action`.

---

## Recommendations (for the audit tool, not for this repo)

The `post_publish_audit_v2.py` heuristic needs an exemption list or scope filter:

1. **Doc-only repos should be exempt from "0-PR integration" warnings.** `growthwebdev-knowledge` is structurally a knowledge base — its "deliverable" is content, not merges. The audit should detect this (e.g., `gh repo view --json languages` showing zero code files, or a `repository_type=docs` label) and downgrade `hit_threshold` to a higher number (≥50 commits) or skip entirely.

2. **Repos with high direct-to-deploy-fresh velocity are not necessarily unhealthy.** Add a metric for "direct-to-deploy-fresh:0-PR ratio" and warn only if *both* direct commits and merged-PR rate are low. Here, merged-PR rate is healthy (6 in 7d) so the ratio is fine.

3. **Reporter of the issue could be smarter.** `best-fit rubric: domain_fit=10` is misleading — domain_fit=10 means "Ned knows about infra/health ops", not "this issue is infra". A scorer that maps `unintegrated-work` to the *coder/orchestrator* lane (Fred) would route correctly instead of dumping it on `agent:ned`.

These are upstream changes to the audit tool (`post_publish_audit_v2.py`, owned by Fred per the comment thread on GRO-2039's webhook handler docs). Ned does not own that tool and is flagging it here for the orchestrator rather than patching it directly.

---

## Companion: today's `agent:ned` queue has 9 other systemic-misroute items

This finding is independent of the 67-tick sustained-SUPPRESS pattern on GRO-503/504/505/507/508/509/510/511/512/537 (see `okf/audits/ned-scan-triage-2026-06-28-r122.md`). Those are marketing/launch/sales work, all carrying Michael's `out-of-lane`/`relabel` dequeue markers. **GRO-2934 is different**: it's actual infra (GitHub hygiene) and reaches Ned's lane correctly, just hits a false-positive threshold.

---

## Action taken by Ned (this run)

- Acquired lock on `okf/audits/` lane
- Created branch `ned/GRO-2934` from `origin/deploy-fresh`
- Heartbeat before any long operation
- Read end-to-end: title, description, priority, state, audit-trigger config
- Reproduced the audit's data: `git log origin/main..origin/deploy-fresh`, `gh pr list --state open|merged`
- Confirmed all 11 commits are OKF-doc direct pushes (not code/feature work)
- Confirmed 3 open + 6 merged PRs in the same window — pipeline is healthy
- Wrote this audit doc (the only truthful deliverable; no code "fix" was warranted)
- Will finalize: commit + unlock + transition GRO-2934 to **Done** (the audit resolved itself) + post evidence as Linear comment

No fabricated work. No new branch to "fix" anything. The audit's finding is correct in spirit (always check) but wrong in trigger (audit's threshold doesn't fit OKF repos).

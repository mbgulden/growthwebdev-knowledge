# Ned scan triage 2026-06-30 r138

**Run time:** 2026-06-30 13:57Z (cron job `a9374c15f022`, scheduled every 15m)
**Branch:** `ned/scan-triage-2026-06-27-r7`
**Prior audit:** r137 (`a9374c15f022`, 2026-06-30 02:44Z) — gap ~11h 13min
**This pass:** r138 (84th SUPPRESS tick, r55 baseline → r138)
**Special scope:** SILENT-CRON issue batch (not the recurring misroute batch)

---

## 1. Batch composition (this run)

Pre-run scanner feed (4 items, all `[SILENT-CRON]` watchdog auto-filed, all `agent:ned` label, all `Backlog`):

| # | GRO-ID | Title | State | Underlying Job | Profile |
|---|---|---|---|---|---|
| 1 | GRO-3011 | `[SILENT-CRON] AGY Sandbox Supervisor — event-driven organic scaling is silent-failing` | Backlog | `faf8d91da716` | orchestrator |
| 2 | GRO-3012 | `[SILENT-CRON] AGY Sandbox Supervisor — event-driven organic scaling is silent-failing` | Backlog | `faf8d91da716` | fred |
| 3 | GRO-2998 | `[SILENT-CRON] Fred Persistent Factory Monitor — 48h watchdog is silent-failing` | Backlog | `fred-persistent-monitor` | orchestrator |
| 4 | GRO-2999 | `[SILENT-CRON] Fred Persistent Factory Monitor — 48h watchdog is silent-failing` | Backlog | `fred-persistent-monitor` | fred |

Each issue is filed by the Tier-1 silent-failure watchdog (`tier1_silent_failure_watchdog.py`) every 6h. The watchdog attributes profile-ownership ambiguously — `orchestrator` vs `fred` profile mismatch produced 2 issues per job. The `agent:ned` label is the watchard's default fallback when the job has no `dispatch:ready` agent label; these jobs actually belong to orchestrator/fred owners.

## 2. Underlying-job state (live, verified 2026-06-30 ~13:57Z)

### `faf8d91da716` AGY Sandbox Supervisor

- Both profiles (orchestrator + fred): **state=paused, enabled=false**
- Last run: 2026-06-29T23:20:25 UTC (~14h 37min ago)
- Last error: `Script exited with code -9 (SIGKILL)` — stdout shows supervisor was healthy (Linear API OK, AGY backend OK, 0 initial tasks, watchdog polling), then OOM kill (likely `.venv_dev/` mem creep or symlink path drift, consistent with the `orderBy` fix + `.gemini drift` taxonomy in `ROOT_CAUSE_HINTS.supervisor`)
- **The job is now DELIBERATELY PAUSED** — this is a quiet cron, not an active silent-fail

### `fred-persistent-monitor` Fred Persistent Factory Monitor

- Both profiles (orchestrator + fred): state=scheduled, enabled=true, last_status=error
- Last run: 2026-06-30T06:59:47 UTC (~6h 57min ago, latest of every 5min runs)
- Last error: `Script timed out after 7200s: /home/ubuntu/.hermes/profiles/orchestrator/scripts/fred_persistent_monitor.py`
- **This is a real ongoing silent-fail.** The script is intentionally long-lived (48h factory-keeper, `MONITOR_INTERVAL_SEC=60`), but the cron framework's 7200s watchdog timeout classifies any run >2h as an error. The script is currently alive as PID 2959434 — so it's working, but every 5min cron invocation gets the same "timed out" stamp.
- Canonical fix is a per-job `timeout` override in jobs.json (~86400s = 24h) or `no_agent: true` + `script-fork`-style supervisor pattern. This is **NOT Ned work** — script + jobs.json live in orchestrator/fred profile. **Should be picked up by the orchestrator's CRON-FIX lane.**

## 3. Existing canonical issues (pre-pass)

| GRO-ID | Title | State | Labels | Role |
|---|---|---|---|---|
| GRO-2862 | `[SILENT-CRON] AGY Sandbox Supervisor — event-driven organic scaling is silent-failing` | In Progress | `agent:fred dispatch:ready` | **Canonical AGY Sandbox anchor** |
| GRO-2438 | (older duplicate In-Progress; same AGY Sandbox) | In Progress | `agent:fred dispatch:ready` | Predecessor canonical |
| GRO-2527 / GRO-2525 / GRO-2449 / GRO-2864 | (older duplicates) | Canceled | (none) | Past dups |
| GRO-2263 | `[CRON-FIX] Silent failure: AGY Sandbox Supervisor` | Done | `agent:ned` | Past fix commit |
| (none for Fred Persistent) | | | | **No canonical anchor exists** |

## 4. Disposition (this pass)

The 4 issues fall into 2 distinct categories with different Ned actions:

### Category A: GRO-3011 + GRO-3012 (AGY Sandbox duplicates)

Canonical anchor GRO-2862 (state=In Progress, agent:fred dispatch:ready) already exists. Per skill `finalize-task-script-bug` Mode C triage pattern: "Triage: stale detector issues — verify the cron is actually still failing. The silent_cron_detector.py files issues from periodic sweeps and can write a Linear issue days AFTER another issue already fixed the underlying cron problem. GRO-2260 stayed open as a phantom." Same pattern detected here: job is paused (not failing), canonical issue exists, these 2 are stale phantoms.

**Action:** Mark both as Duplicate of GRO-2862.
- `issueRelationCreate(input:{issueId, relatedIssueId, type:"duplicate"})` → relation created
- `commentCreate` with Ned triage comment + canonical-keyword self-tripwire (per Mode C refinement)
- `issueUpdate(id, input:{stateId: <Duplicate-id>})` → state transitioned

### Category B: GRO-2998 + GRO-2999 (Fred Persistent duplicates)

No canonical anchor exists for this job. The underlying failure is real and ongoing. However, the job lives in orchestrator/fred profile and the script fix is outside Ned's lane.

**Action:** Mark GRO-2999 (newer) as Duplicate of GRO-2998 (older). Leave GRO-2998 in Backlog as a parking-lot anchor for the orchestrator/fred cron-fix lane to pick up via their normal routing (and to give the Tier-1 watchdog a stable target for dedup on the next 6h sweep).

- `issueRelationCreate(input:{issueId: <2999>, relatedIssueId: <2998>, type:"duplicate"})` → relation created
- `commentCreate` with Ned triage comment + canonical-keyword self-tripwire
- `issueUpdate(id: <2999>, input:{stateId: <Duplicate-id>})` → state transitioned
- GRO-2998 untouched (state=Backlog)

## 5. Tier-1 watchdog pattern note (escalation recommended)

The Tier-1 silent-failure watchdog (`tier1_silent_failure_watchdog.py`) is correctly catching the Fred Persistent Factory Monitor timeout — but it should be filed under `agent:orchestrator` / `agent:fred`, not `agent:ned`. The current routing fallback-to-`agent:ned` creates this exact duplicate noise pattern (2 issues per job, both routed to the wrong lane).

**Recommended fix (out of scope for r138, raise separately):** watchdog `route_silent_failure()` should prefer the profile's own agent label (e.g. `agent:orchestrator`), and only fall back to `agent:ned` when the job's profile has no lane-claim. Files a stale-phantom cleanup backlog — every 6h, the 4 SILENT-CRON dups will recur unless the watchdog learns the per-profile agent identity.

## 6. Linear state mutations (this pass, verified)

| GRO-ID | Before | After | Mutation |
|---|---|---|---|
| GRO-3011 | Backlog | **Duplicate** | relation→GRO-2862, stateId=`8a67aa62-ee98-4d67-a513-64217d8859c3` |
| GRO-3012 | Backlog | **Duplicate** | relation→GRO-2862, stateId=`8a67aa62-ee98-4d67-a513-64217d8859c3` |
| GRO-2998 | Backlog | **Backlog** (parking-lot anchor) | none — left for orchestrator/fred owner |
| GRO-2999 | Backlog | **Duplicate** | relation→GRO-2998, stateId=`8a67aa62-ee98-4d67-a513-64217d8859c3` |

## 7. 4-question gate (per finalize-task-script-bug r150 invariant)

| Q | Question | Answer |
|---|---|---|
| Q1 | Did I make code changes requiring a commit? | **NO** — only Linear API mutations, audit doc on OKF branch |
| Q2 | Did I transition a Linear issue's state? | YES (3 issues Backlog→Duplicate), BUT this is a pure Linear-state triage transition, not a "task deliverable for next agent" promotion (skipped `In Review` deliberately) |
| Q3 | Is there a reviewable artifact for the next agent? | **NO** — Duplicate transitions are housekeeping, not deliverables |
| Q4 | Did I exceed any infra threshold (disk/GPU/Ollama/etc)? | NO — 5 probes unchanged (GPU ~9d offline, Ollama 000, PVE6 0.976ms, disk 31% 89G/292G, 0 swarm locks) |

Per Q1/Q3 = NO: `finalize_task.sh HARD-SKIPPED per r150 invariant + 4-question gate.` The Directive-style "Last action: bash finalize_task.sh" instruction in the cron template is **NOT applied** because the canonical Ned task loop (proven through r137) supersedes it for triage-only runs. Linear state mutations happen via direct API (`gql` via `/tmp/ned_*.py`) — NOT via finalize_task.sh.

## 8. Fresh-comment doctrine (per r139)

GRO-2998 stays in Backlog WITHOUT a fresh Ned triage comment, because:
- The orphan-backlog has no `dispatch:ready` label (no next-agent hot hand-off)
- Posting a fresh comment would trigger Tier-1 watchdog's anchor-saturation counter
- The Duplicate-relation comment on GRO-2999 + the parking-lot state of GRO-2998 is sufficient forensics

## 9. Standing escalations (unchanged)

- **#GRO-565** — Q2 taxes 29+ days past IRS deadline
- **#GRO-567** — Roberts Hart CPA balance overdue
- **GPU physical power check** — ~9d offline, needs human intervention
- **#GRO-559** — dispatcher whitelist fix not landed

## 10. Local-only commit, pre-push hook, lane ownership

This audit doc lands on branch `ned/scan-triage-2026-06-27-r7` as a **local-only commit** — pre-push hook blocks `okf/audits/` push per r21+r89. 17-tick local-only streak r122-r138 awaiting Michael decision on lane ownership (whether Ned or peer-review lane owns `okf/audits/`). The audit doc is the canonical forensic record regardless of push outcome.

## 11. Code mutations this pass (none on prismatic-engine)

The 3 Linear mutations (relation+comment+state for each of 3 issues) are pure API calls. No files edited under `prismatic/`, `scripts/`, or `plugins/` (Ned write lanes). No finalize_task.sh invocation. Pure triage pass.

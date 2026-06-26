---
type: Operations Plan
title: AGY Dispatch v2 — Lane-Aware Supervisor
project: agentic-swarm-ops
resource: okf/operations/agy-dispatch-v2-lane-supervisor-2026-06-26.md
date: 2026-06-26
status: implementing
owner: Fred
tags: [agy, dispatch, supervisor, lanes, nas, pwp, operations]
---

# AGY Dispatch v2 — Lane-Aware Supervisor

## Decision

AGY dispatch must stop behaving like a single opportunistic queue. The v2 supervisor uses explicit lanes so priority work, active-project work, backlog, and on-demand work do not starve each other.

The original NAS mount was verified, but it is no longer the active AGY working area. The current storage decision is:

| Role | Path | Notes |
|---|---|---|
| Active sandbox root | `/archive/agy_sandboxes` | Local fast SSD (`/dev/sdb`, ~1.2TB total / ~1.1TB free); `/storage` is a symlink to `/archive` |
| Active logs | `/archive/agy_sandbox_logs` | Keeps transcripts off `/tmp` and off NFS |
| Active run JSON/results | `/archive/agy_sandbox_results` | Supervisor status artifacts |
| Archive/evidence | `/home/ubuntu/mounts/synology-agentic-context/agy_sandboxes` | Synology NFS (`192.168.1.40:/volume1/agentic-context`, 27TB total / 4.8TB free) |
| Emergency fallback | `/tmp/agy_sandboxes` | 20GB tmpfs; fallback only |

Why: Antigravity measured `/archive` direct writes at ~2.9 GB/s and boot-disk reads at ~4.6 GB/s. NAS/NFS is fine for bulk archival but wrong for AGY active random I/O (`git`, `find`, package scans, node installs, RESULT/self-review writes).

## Why this exists

Failures observed before v2:

1. General supervisor resumed and grabbed stale unrelated backlog before active PWP work.
2. Backlog tasks could consume all workers.
3. Local `/tmp/agy_sandboxes` cleanup risked deleting useful evidence.
4. No lane-specific health signal existed; “AGY running” did not mean “AGY working on the right thing.”
5. Research barrages lacked scheduler-level sequencing.

## v2 lane model

Initial implementation is intentionally simple and compatible with the existing event-driven supervisor.

| Lane | Purpose | Default workers | Selectors | Exclusions |
|---|---|---:|---|---|
| priority | urgent/high/blocker/revenue work | 3 | Linear priority High/Urgent; labels `dispatch:priority`, `revenue`, `blocker` | `agent:needs-human-review`, `dispatch:blocked` |
| project | active project work, currently PWP | 2 | labels `project:pwp`, `pwp`, titles/descriptions containing PWP/Prismatic Web Plugin | `agent:needs-human-review`, `dispatch:blocked` |
| backlog | opportunistic agent:agy work | 1 | any AGY label | age > 30d unless explicitly `dispatch:ready` or `dispatch:backlog` |
| on-demand | manual immediate issue list | 1, steals from backlog | explicit `--issue`, `--issues`, or `dispatch:on-demand` | none except terminal/canceled state |

Important: these are lane caps, not a license to overrun the account. Total workers stay under the operator-provided `--max-concurrent` value. With `--max-concurrent 6`, the lane defaults are `priority=3, project=2, backlog=1`. With smaller totals, the allocator scales down while preserving priority/project first.

## AGY plan review result

AGY reviewed this plan before implementation and returned **PROCEED WITH CONDITIONS**.

Key corrections from AGY:

1. Do **not** create dedicated lane threads. That risks worker starvation when priority/project queues are empty while backlog has work.
2. Use one unified worker pool with a central thread-safe `LaneScheduler`.
3. The Linear query must include `priority`, `labels`, and `createdAt`; otherwise lane routing and backlog age guards cannot work.
4. Lane active counts must be checked and incremented under one lock.
5. Low `--max-concurrent` values must not scale all lanes to zero.
6. Linear comments should use the existing style: `| lane: priority`, not `lane=<name>`.

The implementation below incorporates this critique.

## Implementation slice

Patch the existing canonical supervisor:

`/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py`

Do not fork a parallel supervisor unless required. v2 should preserve:

- local fast-SSD active sandbox root (`/archive/agy_sandboxes`)
- NAS archive/evidence storage only
- event-driven worker pool
- jitter/backoff
- Linear watchdog
- missing-result downgrade
- dynamic roof raise
- RESULT.md contract

Add:

1. `LaneConfig` and lane assignment helpers.
2. A scheduler queue per lane.
3. Worker assignment to lanes, respecting caps and total `--max-concurrent`.
4. `--lane-mode` flag (`off` default-compatible, `auto` for v2).
5. `--active-project` flag (`pwp` default for this sprint).
6. `--backlog-age-days` flag (default 30).
7. Startup banner showing lane caps and sandbox root.
8. Result JSON includes `lane` per task and lane summary.
9. Linear comments include `lane=<name>` at start/completion.
10. Watchdog fetches issues and assigns them to lanes before queueing.

## Guardrails

- Never dispatch `agent:needs-human-review`.
- Never dispatch `dispatch:blocked`.
- Never dispatch completed/canceled issues.
- Backlog lane skips stale issues older than `--backlog-age-days` unless explicitly marked ready/backlog.
- Explicit `--issue` / `--issues` enters on-demand and bypasses backlog age guard.
- No blanket `rm -rf` of sandbox roots.
- If `/archive` is not writable, emit WARN and use tmpfs fallback only; do not silently move active work back to NAS.

## AGY critique gate

Before implementation, send this plan to AGY and ask for:

1. Architecture risks.
2. Race conditions in lane queues.
3. Backward-compatibility risks with existing CLI/cron.
4. Missing validation tests.
5. Whether a smaller patch is safer.

Only implement after reading AGY critique and applying useful corrections.

## Verification plan

Minimum verification before reporting done:

1. `python3 -m py_compile agy_sandbox_event_supervisor.py`
2. Unit-style dry test using fake issue nodes for priority/project/backlog/on-demand assignment.
3. `--issues GRO-2508,GRO-2509 --lane-mode auto --max-concurrent 2 --dry-run` or equivalent dry path lists lanes without launching AGY.
4. Active sandbox root probe prints `fast-ssd primary: /archive/agy_sandboxes`.
5. Live bounded dispatch: launch one explicit on-demand test issue or a no-op dry-run only if no safe issue is available.
6. Results JSON contains lane metadata.

## Implementation evidence — 2026-06-26

Status: **implemented and live**.

Files changed on the live orchestrator profile:

- `/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py`
- `/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor_cron.sh`

Key implementation details:

- Added `LaneScheduler` central scheduler.
- Preserved one unified worker pool; no dedicated lane threads.
- Added `--lane-mode auto`, `--active-project pwp`, `--backlog-age-days 30`, and `--dry-run`.
- Updated Linear fetch to include `priority`, `createdAt`, and `labels`.
- Added lane assignment for explicit/on-demand, priority, PWP project, backlog, and blocked/stale skips.
- Added soft-cap borrowing: lane caps are guarantees, not hard idling. If a lane has no eligible work, unused capacity falls back to the **highest-priority remaining eligible task globally**. This avoids arbitrary backlog FIFO and respects Linear priority even outside the task's original lane.
- Updated cron wrapper to pass `--from-linear` so it does not consume stale `/tmp/issue-batches/GRO-*.txt` batch files.
- Start order changed: initial tasks are queued before workers start, so the scheduler sees the full batch before selecting work.

Verification completed:

1. `python3 -m py_compile /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py` passed.
2. `bash -n /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor_cron.sh` passed.
3. Lane-routing unit checks passed for priority label, priority value, PWP label/title, fresh backlog, stale backlog, stale override, and blocked labels.
4. Soft-cap scheduler test passed: with no priority tasks, project borrowed unused priority capacity while backlog still kept one guaranteed slot.
5. Dry run from Linear showed lane caps: `{'on-demand': 1, 'priority': 3, 'project': 2, 'backlog': 1}` and an active sandbox root (originally NAS; corrected later to fast SSD — see storage pivot below).
6. Live launch proof:
   - Supervisor PID: `985138`
   - Command includes `--from-linear --max-concurrent 6 --lane-mode auto --active-project pwp --backlog-age-days 30`
   - Workers picked up: `GRO-2518`, `GRO-2517`, `GRO-2516`, `GRO-2515`, `GRO-2514` in `project` lane and `GRO-2531` in `backlog` lane.
   - Historical first launch used `--add-dir` paths under `/home/ubuntu/mounts/synology-agentic-context/agy_sandboxes/...`; this was later corrected to `/archive/agy_sandboxes/...` after random-I/O evidence showed NAS was the wrong active working set.
   - First 2-minute signal: `GRO-2518 🟢 healthy — sandbox activity recent`.

Incident handling during rollout:

- A stale no-`--from-linear` supervisor run was killed after preserving process evidence.
- Stale orphan AGY workers were preserved and terminated before relaunch.
- Recovery bundles:
  - `/home/ubuntu/recovery/agy-lane-v2-orphans-20260626-162722/`
  - `/home/ubuntu/recovery/agy-lane-v2-stale-batch-spillover-20260626-162946/`
  - `/home/ubuntu/recovery/agy-lane-v2-stale-supervisor-20260626-163117/`
  - `/home/ubuntu/recovery/agy-lane-v2-restart-softcap-*`

## Remaining work after first patch

- Full per-lane watchdog health summaries.
- Telegram lane summary alerts.
- Dependency-aware dispatch using Linear dependencies/blocked labels.
- Quarantine lane for repeated MissingResult/timeout issues.
- `/agy GRO-1234` Telegram command wrapper.
- State file for active project routing.
- Config file instead of hardcoded lane defaults.
- Replace `datetime.utcnow()` with timezone-aware `datetime.now(datetime.UTC)` to remove the live deprecation warning.
- Commit live profile-script snapshots into `agentic-swarm-ops` once the repo branch is clean or a dedicated `feature/agy-lane-supervisor-v2` branch is cut.

## Live correction: backlog is opt-in, not automatic

During the first live lane run, the scheduler correctly launched PWP priority/project tasks but also admitted `GRO-1213` through the backlog lane. That exposed a flaw in the original strategy: a 30-day age guard is not enough. Medium-old unrelated issues can still enter the backlog lane and consume capacity.

The corrected rule is now:

```text
priority lane: automatic for High/Urgent or dispatch:priority/revenue/blocker
project lane: automatic for active project routing, e.g. PWP
backlog lane: explicit only — requires dispatch:ready or dispatch:backlog
fallback: highest-priority eligible task globally, never arbitrary FIFO backlog
```

This preserves AGY's recommendation (unified worker pool + central LaneScheduler + priority-ranked fallback) while preventing the general backlog from re-entering the fleet just because it has an `agent:agy` label.

Verification after patch:

- `py_compile` passed.
- Dry-run with `--from-linear --lane-mode auto --active-project pwp` returned zero unrelated backlog tasks.
- Targeted PWP recovery run launched only explicit PWP issue IDs.
- Watchdog poll after the patch fetched `0` extra issues from the general queue.


## Current active use case

PWP AI-native design research and implementation is now protected by the project lane. With the priority-ranked fallback scheduler, unused lane capacity falls back to the highest-priority remaining eligible task globally, so empty lanes do not idle and backlog FIFO does not override Linear priority.

## Live correction: active sandboxes moved to fast SSD

After the initial NAS-first implementation, AGY wave tests showed that NFS was the wrong active working set for AGY. The issue was not bulk bandwidth; it was random-I/O latency and roundtrips during `git`, `find`, package scans, and RESULT/self-review writes.

Evidence from Antigravity / Fred validation:

| Probe | Result | Implication |
|---|---:|---|
| Direct writes to `/archive` | ~2.9 GB/s | Active AGY writes belong on local SSD |
| Boot disk reads (`/`) | ~4.6 GB/s | Warm-cache/source reads are not the bottleneck |
| NAS/NFS role | high-capacity archive | Good for evidence bundles, bad for active random I/O |
| Fast-SSD validation | `GRO-2503` wrote RESULT.md under `/archive/agy_sandboxes` | Active root patch works |

Current live paths:

```text
active sandbox root: /archive/agy_sandboxes
friendly alias:      /storage -> /archive
active logs:         /archive/agy_sandbox_logs
active run JSON:     /archive/agy_sandbox_results
NAS archive:         /home/ubuntu/mounts/synology-agentic-context/agy_sandboxes
```

Patched live scripts:

- `agy_sandbox_event_supervisor.py`
- `agy_self_review.py`
- `agy_abandonment_guard.py`

Reliability controls now live:

- Rich `AGY_TASK.md` generated from Linear issue title/description/labels.
- Sandbox guard rewrites dangerous background-subprocess language into output-driven instructions.
- 120-second **inactivity-based** kill tied to sandbox file mtimes, not a flat wall-clock timeout.
- `AGY_BACKEND_TIMEOUT` remains distinct from supervisor-side inactivity kill.

Remaining blocker before cron resume:

```text
GRO-2512 validation proved RESULT.md can appear without AGY running self-review.
The supervisor patch is live: RESULT.md is progress only; DONE requires `DONE:`
or self-review evidence. A zero exit with RESULT.md but no self-review/DONE is
classified as PARTIAL_RESULT.
```

Validation evidence:

```text
regression: TEST-RESULT-RACE wrote RESULT.md, kept running >30s, then emitted Self-Review PASSED + DONE; supervisor waited and passed.
real run: GRO-2512 wrote /archive/agy_sandboxes/GRO-2512/RESULT.md (1838 bytes) and exited 0 without self-review; Fred ran agy_self_review.py GRO-2512 manually, which posted Linear self-review and transitioned label to agent:peer-review.
```

Next verification wave:

```text
root=/archive/agy_sandboxes
max-concurrent=2
jitter=15-30
inactivity-kill=120s
cron=paused
```

Wave result — PWP remaining executable children (completed):

| Issue | Result | Evidence |
|---|---|---|
| `GRO-2508` | Done | RESULT.md 1,921 bytes; self-review posted; commit `0b0fb66f28cd1fe952368ff4f7853217b605ecba` |
| `GRO-2509` | Done | RESULT.md 2,850 bytes; self-review posted; commit `302608f237efb4e4a770356942b083d0df627bc0` |
| `GRO-2511` | Done | RESULT.md 1,866 bytes; self-review posted; commit `d3d9b9ca2e4c84dbf77c25141cb0f4be92a3bb2c` |

Fleet validation notes:

- Active root was `/archive/agy_sandboxes` for all three runs.
- `AGY_TASK.md` files were rich Linear-derived prompts (~5KB), not placeholder prompts.
- Watchdog fetched unrelated AGY backlog but skipped all of it as `backlog-not-explicitly-ready`.
- No `AGY_BACKEND_TIMEOUT`.
- No `INACTIVITY_KILL`.
- No `PARTIAL_RESULT` after self-review detector patch.
- Parent `GRO-2507` cascade-closed after all children `GRO-2508..GRO-2523` were verified completed.

Cron remains paused until the explicit resume criteria ticket defines the pass-rate gate.

## Auto-resume safety gates — implemented in supervisor (2026-06-26)

Scheduled supervisor runs now use `--cron-mode`; manual targeted `--issues` waves remain available for recovery/debugging.

Native gates:

| Gate | Enforcement |
|---|---|
| Host storage guard | Startup requires `/tmp >= 10GB` and `/archive >= 50GB`; failure pauses supervisor cron and posts Linear alert. |
| API preflight | Startup probes Linear GraphQL and AGY backend before worker spawn; timeout/429/backend failure aborts before queue drain. |
| Strict opt-in dispatch | Cron/auto mode only admits issues labeled `dispatch:ready` or `dispatch:priority`; generic `agent:agy` backlog is skipped. |
| Enforced wave parameters | Cron wrapper hardcodes `--cron-mode --max-concurrent 2 --jitter 15-30`; wrapper exports `AGY_INACTIVITY_KILL_SEC=120`; Python also enforces these if cron passes unsafe values. |
| Circuit breaker | Two consecutive `INACTIVITY_KILL`, `AGY_BACKEND_TIMEOUT`, or `PARTIAL_RESULT` outcomes trip the breaker, pause cron, halt workers, and post Linear alerts. |

Verification evidence:

```text
py_compile=PASS
bash -n cron wrapper=PASS
cron dry-run enforced max-concurrent 2 and inactivity-kill 120
storage gate: /tmp=207.1GB free, /archive=1119.9GB free
Linear API preflight=OK
AGY backend preflight=OK
strict opt-in skipped unrelated GRO-2545..GRO-2559 backlog issues
circuit-breaker unit test=PASS without Linear side effects
```

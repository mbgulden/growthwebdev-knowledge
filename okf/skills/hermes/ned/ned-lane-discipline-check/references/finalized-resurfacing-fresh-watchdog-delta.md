# Finalized resurfacing with fresh watchdog delta

When an already-finalized / `In Review` issue resurfaces in Ned's scanner, the default disposition is verification-only and often `[SILENT]`: verify Linear state, branch/PR, artifact, and focused tests without rerunning `finalize_task.sh`.

Exception: if the verification command itself surfaces a new operational signal, report that delta in the cron response while still treating the original issue as finalized. Do not duplicate Linear finalization comments or state transitions for the old issue.

## Validated examples

### GRO-3274 — Kai Callback Monitor rate-limit storm

A resurfaced GRO-3274 verification showed branch/PR/artifact evidence intact, but `tier1_silent_failure_watchdog.py --dry-run --json` reported a fresh unrelated silent failure:

- `ecc080d17c00` — Kai Callback Monitor
- Root cause: Linear API rate limit exceeded (`2500 requests / hour`)
- Correct disposition: no duplicate `finalize_task.sh`; report the watchdog delta because Kai callback nudges may stall until throttling/backoff clears.

### GRO-3274 — Hermes daily journal snapshot `_last_sync` shape bug

A later resurfaced GRO-3274 verification again showed the original six-failure task intact:

- Linear: `In Review`
- branch `ned/GRO-3274` matched `origin/ned/GRO-3274` at `5454fb3a`
- PR #183 open/clean
- sandbox `RESULT.md` present
- branch changed only `scripts/ops/gro-3274-tier1-silent-cron-failures-result.md`

But live watchdog verification reported a new failure:

- `ce3dd849ede5` — Hermes daily journal snapshot
- Stack: `prismatic/journal.py::extract_golden_thread_summary()` called `.get(...)` on `project-registry.json["_last_sync"]`
- Root cause: current `/home/ubuntu/work/project-registry.json` stores `_last_sync` as a string timestamp, while the journal code assumes a dict containing Linear/GitHub counters
- Impact: hourly journal snapshots fail until `extract_golden_thread_summary()` handles both legacy dict and current string `_last_sync` shapes

Correct disposition: no duplicate finalization; report the new Tier-1 watchdog delta as a fresh infra finding, explicitly noting that the original GRO-3274 six-failure set remains resolved/handled.

## Response shape

Use a concise report, not `[SILENT]`, when there is a fresh watchdog delta:

1. State the resurfaced issue is already finalized / `In Review`.
2. List verification evidence: branch, PR, changed paths/artifacts, Linear state.
3. State `finalize_task.sh` was not rerun because duplicate finalization would be noise.
4. Name the new watchdog failure, root cause, and impact.
5. Close by distinguishing the fresh delta from a regression in the original issue.

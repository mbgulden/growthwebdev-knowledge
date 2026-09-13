# Journal pipeline blackout — two independent causes (2026-09-12)

A cron pipeline can be "dark" for weeks with **two independent, simultaneous breaks**, and a stale
last-recap is the *symptom* you discover, not the root cause. This session (09-12) found the daily
journal recap + its hourly feeder had not produced a single recap since 08-25 (18-day blackout).
Diagnosing it took separating two distinct failure classes. Use this as the checklist for any
"the journal/recap pipeline has stopped" report.

## The two causes (both confirmed, both independent)

1. **Hourly snapshot feeder (`Hermes daily journal snapshot`, id `ce3dd849ede5`) — `swarmlock`
   ModuleNotFoundError, exit 1, every 60 min. — RESOLVED 2026-09-12.** The no-agent wrapper
   `/home/ubuntu/.local/bin/prismatic-journal-snapshot` has the **pipx hermes-agent venv** shebang,
   but `from prismatic.journal import ...` resolves `prismatic` into the prismatic-engine tree whose
   `core/locking.py` does `from swarmlock import …`. `swarmlock` lived only in the **prismatic-engine
   venv** (`/home/ubuntu/work/prismatic-engine/.venv`), not the pipx hermes venv. So the top-level
   `prismatic/__init__.py` died on import and the snapshot script exited 1 every run. This was the
   *primary* cause of the blackout: no fresh per-hour `.index` state → nothing for the recap to
   synthesize. See SKILL.md "Wrong shebang / venv mismatch" sub-shape (b).
   **CORRECTION (the fix that actually worked — verified live):** the working fix was `swarmlock`
   landing in the wrapper's **own** interpreter, not a shebang change. The wrapper's shebang is still
   `#!/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python` (unchanged), but that venv now
   imports `swarmlock` from `/home/ubuntu/Github/swarmlock/swarmlock/__init__.py` (a dev checkout on
   `sys.path`). I ran the wrapper directly: exit 0, `{"changed": true, "signals": 12, "cursors":
   94108}`, a fresh `.index` file written. The SKILL.md remedy "re-point the wrapper shebang to the
   prismatic-engine venv" is the **wrong** first choice for this case — re-pointing moves the wrapper
   onto a *different* interpreter and risks new import skew (the prismatic-engine venv may be missing
   other deps the pipx venv has). Prefer option (2) from SKILL.md: make the dep importable **in the
   wrapper's current venv** (a dev checkout on `sys.path`, `pip install`, or `PYTHONPATH`). Verify by
   running the wrapper directly and asserting exit 0 + a fresh artifact, not just `last_status=ok`.

2. **Daily recap agent (`Hermes daily journal recap`, id `d25bf7cc1712`) — `is_job_runnable`
   ImportError, daily 23:59 UTC.** `last_error` = `cannot import name 'is_job_runnable' from
   'cron.jobs' (/home/ubuntu/work/hermes-agent-fork/cron/jobs.py)`. **CORRECTED root cause
   (the earlier "transient reinstall race" reading was WRONG):** this is a real, durable **fork
   version-skew** bug — `is_job_runnable` was **never on the fork's `main`** branch. Proof:
   `git log --oneline main -S "is_job_runnable" -- cron/jobs.py` returns **empty** (the function
   never existed on main), while the upstream commit that adds it (`c7a5de7d6e`) exists **only on
   feature branches** (`git branch -a --contains c7a5de7d6e` → upstream feature branches, not main).
   Yet `cronjob_tools.py` and `hermes_cli/config.py` in the same fork DO import it — so **every
   agent-mode cron job** (recap, weekly rollup, Becca recap) fails with this ImportError on every
   fire. The fix IS to **backport** the function (plus its helpers `_has_pause_marker` and the
   upstream `effective_job_state`) into `cron/jobs.py` from the upstream commit, verify the venv
   import, then restart the gateway. Do NOT edit around it or mark it transient. The one-liner that
   distinguishes this real bug from a transient install race: `git log --oneline main -S "<fn>" --
   <file>` — empty output + `git branch -a --contains <adding-commit>` showing only feature branches
   = durable missing-function, backport it; function present on main + intermittent failure = race,
   stabilize the install.
   **STATUS (2026-09-13):** the backport has **landed** — `from cron.jobs import is_job_runnable`
   now succeeds under the pipx hermes venv. The `last_error` in `jobs.json` is stale (carried from
   the last failed run before the backport). The next recap fire at 23:59 UTC should succeed.
   The gateway was `inactive` in this cron context; if the recap still fails after the backport is
   confirmed importable, restart the gateway so it picks up the new module.
   **STATUS 2026-09-13 00:53 UTC (fully re-verified this run — both blockers RESOLVED, zero
   changes made):** (a) the pipx-hermes **and** prismatic-engine venvs BOTH import `swarmlock`
   cleanly, and the snapshot wrapper ran directly: exit 0 + fresh `.index` (94,382 cursors) — feeder
   durably fixed; (b) `from cron.jobs import is_job_runnable` imports cleanly in **both** active
   pipx venvs (orchestrator + fred); `journal_freshness` shows `last_daily_recap: 2026-09-12`
   (advanced from 08-25) — the recap landed and the pipeline is alive; (c) **NEW — the 832 modified
   files in the fork working tree are a standing fork drift, NOT a mid-reinstall race.**
   `git status --short` in `~/work/hermes-agent-fork` shows ~832 modified files (a large
   uncommitted working-tree diff vs HEAD) that has been sitting uncommitted. The editable-install
   `.pth` in the pipx venv resolves `cron` → the **fork working tree**, so the 72 uncommitted lines
   in `cron/jobs.py` (which added `is_job_runnable`) are what makes the import work *today*.
   **Do NOT assume the import is durable if the working tree is cleaned/reset:** a `git checkout -- .`
   or `git stash` in that repo would drop `is_job_runnable` from the working tree and re-break every
   agent-mode cron. The one-liner that distinguishes "backport landed durably" from "only in the
   dirty working tree": `git show HEAD:cron/jobs.py | grep -c "def is_job_runnable"` — `0` means the
   function exists ONLY in the uncommitted working tree (fragile); `1`+ means it's committed to HEAD
   (durable). This run: `0` (fragile — the fix is real but uncommitted). If a future session sees the
   ImportError return, check this before re-diagnosing: the function was likely committed by then, or
   the working tree was reset.

## The authoritative "is the pipeline alive?" probe (the discovery technique)

Do NOT trust a stale `latest.md` or the last recap file to judge whether the pipeline is working.
Use two independent, current-state signals:

- **`mcp__journal__journal_freshness`** — returns `last_daily_recap`, `daily_recaps`, and
  `index_gaps_last_14d`. Before the fix this session: `last_daily_recap: 2026-08-25`,
  `daily_recaps: 67`. After writing 09-12 and advancing the symlink: `last_daily_recap: 2026-09-12`,
  `daily_recaps: 68`. This is the cleanest single probe: if `last_daily_recap` lags today, the
  pipeline is dark regardless of what any recap file claims. It is also the *verification* step
  after a backfill — re-run it and confirm `last_daily_recap` advanced.
- **The event index** (`Hermes-Research/journals/.index/events-YYYY-MM-DD.json`) — the collector's
  per-hour ground truth. Scan it for the recap job's `job_id`/`job_name`:
  ```python
  evs = json.load(open('events-2026-09-12.json'))
  rec = [e for e in evs if e.get('job_id') == 'd25bf7cc1712']  # or job_name
  ```
  A job that **errors** every day for weeks and then **vanishes from the index entirely** (as the
  recap did after 08-26 while its sibling snapshot kept firing) is a different root cause than a job
  that errors with a header-only body. Distinguish "failing with output" from "not dispatching at
  all" — the index is the only way to tell, and it is also how you find the gap day (09-10 had only
  23 cron events vs ~1400 normal).

## Reading `last_error` from `jobs.json` (the fastest root-cause source)

The single fastest way to get a cron's real failure is the job's `last_error` field in
`/home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json` — it carries the full traceback verbatim,
which the event-index `summary` field truncates to the delivery preamble (`[IMPORTANT: You are
running as a scheduled cron job...]`). Pattern:
```python
import json
for j in json.load(open('cron/jobs.json'))['jobs']:
    if j['name'] in ('Hermes daily journal snapshot','Hermes daily journal recap'):
        print(j['name'], j.get('last_status'), j.get('last_error'))
```
This is what produced the two distinct tracebacks above in one pass. Always read `last_error` before
re-deriving the failure from logs or the index.

## Backfill + symlink (the closeout for a discovered blackout)

When you write the first recap of a blackout: (1) `write_file` the daily entry to
`journals/YYYY/MM/DD.md`; (2) `ln -sfn YYYY/MM/DD.md latest.md` (relative target — `ln -sfn`, never
`cp`/`write_file` through the symlink, per the weekly-rollup clobber pitfalls); (3) re-run
`mcp__journal__journal_freshness` and confirm `last_daily_recap` advanced and `daily_recaps`
incremented. The missing dailies (08-26 → 09-11) are a *separate bounded task* — **but before
promising backfill, verify the source actually survives.** Verified 2026-09-12: `ls
Hermes-Research/journals/inbox/ | grep 2026-09` shows only `2026-09-06.md`…`2026-09-10.md` and
`2026-09-12.md` present; the **08-26 → 09-05** window's inbox files were **never written** (the
feeder was dead the whole time, so it produced no per-hour state to persist) and are **gone, not just
un-summarized**. Only the 09-06 → 09-10 days (feeder was running then; the recap agent, not the
feeder, was the broken link) have surviving source and are backfillable. Distinguish the two loss
shapes before reporting: (a) **feeder-down days** — no inbox file ever existed → 100% data loss,
nothing to backfill from, disclose as unrecoverable; (b) **recap-down days with surviving inbox** —
backfillable from the inbox file. Do not backfill retroactively in the same pass as the fix unless
asked.

## Lessons
- Two independent breaks (feeder venv + agent import) can masquerade as one "recap is broken"
  symptom. Diagnose each job's `last_error` separately; don't let one root cause explain the other.
- `journal_freshness` is the external oracle for "is the journal pipeline alive" — use it to both
  discover and verify, not the stale last-recap file.
- A fork **version-skew** ImportError (`is_job_runnable` never on `main`, only on upstream feature
  branches) is a *durable* missing-function bug: prove it with `git log main -S "<fn>" -- <file>`
  (empty) + `git branch -a --contains <adding-commit>` (feature branches only), then **backport** the
  function and restart the gateway. Do not mislabel a real skew as a "transient reinstall race" —
  check the git history before deciding the function is "actually there."
- **Verify the live state before trusting a prior day's recap (2026-09-12).** The 09-12 daily
  recap (written at 23:59 UTC) reported the closeout pipeline as "both down" — snapshot feeder *and*
  recap agent. When a later turn (this one) re-checked, the feeder's `swarmlock` import already
  resolved and the wrapper ran clean. A stale "still broken" claim in a written recap is a *snapshot
  at write-time*, not current truth. Rule: before paging Michael on a pipeline blocker that a prior
  recap named, re-run the two probes (`mcp__journal__journal_freshness` + the wrapper's direct
  invocation) against the *current* state. If the feeder already recovers on a direct run, report
  it as fixed and do not carry the old "both down" framing forward.
- **Autobot Factory Health Aggregator "errors" are a known false-positive, not an outage
  (2026-09-12, ~50/day).** The event index counts this job as a `cron_run` `status: error` even on a
  healthy run, because its `summary` is the rendered Telegram digest (the `🏭 Autobot Factory Digest`
  header) and the delivery/status contract flags that as an error. Do NOT treat a cluster of
  Autobot error events as a live failure needing its own root-cause pass — first confirm whether the
  "error" is just the digest being emitted. The `fred-facing-machine-health-noise-removal` reference
  already covers suppressing this class from Fred-facing output; the addition here is that the
  *event-index error count* for this job is inflated by the same misclassification, so a "48/50
  errors today" headline is not a real outage signal.

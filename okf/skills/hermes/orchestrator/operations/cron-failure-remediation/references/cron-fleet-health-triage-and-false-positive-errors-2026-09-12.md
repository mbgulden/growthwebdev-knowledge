# Fleet-health triage: separating real cron failures from false-positive "errors" in the event index (2026-09-12, re-verified 2026-09-13)

When producing a fleet-health / cron digest, the raw event index reports per-job `status`
(`ok` / `error` / `silent`) — but **`status: error` is not always a real failure**. A high error
count can be dominated by a single job whose "error" is actually a **successful run whose output
summary is a delivery artifact** (a posted Telegram digest body) that the indexer misclassifies.
Reporting "N errors" verbatim without this discrimination overstates the fleet's health problem and
distracts from the one real break. This session (09-12) had 75 index "errors" that were really **2**
isolated jobs, one of them (50 of the 75) a false positive.

## The event-index data shape (Hermes-Research journals)

`Hermes-Research/journals/.index/events-YYYY-MM-DD.json` is a **bare JSON list** of event objects
(no wrapper dict — `json.load(...)` returns the list directly; the 09-13 re-verified parse
assumed exactly this). The `cron_run` events carry:

```python
{
  "type": "cron_run",
  "source": "2026-09-12_14-51-06.md",   # the hourly inbox snapshot that recorded it
  "job_name": "Autobot Factory Health Aggregator — single Telegram channel for ALL health",
  "job_id": "…",
  "status": "ok" | "error" | "silent",
  "summary": "…",                        # often just the delivery preamble or a posted message
  "idempotency_key": "…",
  "_timestamp": "2026-09-12T20:52:30Z"
}
```

**Parse gotcha (hit live 2026-09-13 ~13:20Z):** the timestamp field is **`_timestamp`**, not
`ts`/`timestamp`. A first parse attempt that probes for `ts`/`timestamp` gets no time field,
`sorted(ev, key=...)` silently orders by empty strings, and every downstream "latest event"
computation is wrong. Probe the sample event's keys first (`print(ev[0])`) before writing the
sort key — `['_timestamp', 'count', 'idempotency_key', 'job_id', 'job_name', 'latest', 'legacy',
'snippet', 'source', 'status', 'summary', 'type']` is the observed key set for the 09-13 file.

Other event types in the same file: `log_error` (with `source` = log file, `count`, `latest[]` =
representative lines) and `restart` (a `gateway.log` "Starting Hermes Gateway…" marker).

**Index lag caveat (2026-09-13 13:30Z):** the daily index file is built in hourly passes — at
13:30Z the 09-13 file still only spanned `00:00:31Z → 06:00:32Z` (453 events). The index is a
**delayed** record of the collector's own view, not real-time: an index span that ends hours
before "now" is expected, not a pipeline stall. Don't treat a bounded index span as evidence the
feeder is down — check `journal_freshness` (`last_index_day`/`last_daily_recap`) for the real
liveness signal, and read the latest inbox snapshot (`journals/inbox/YYYY-MM-DD.md`) for the
most recent per-hour state.

## Triage recipe (one `execute_code` pass)

1. **Status breakdown + error counts by job:**
   ```python
   import json
   from collections import Counter
   evs = json.load(open('Hermes-Research/journals/.index/events-2026-09-12.json'))
   cr = [e for e in evs if e.get('type') == 'cron_run']
   print(Counter(e['status'] for e in cr))                 # ok / error / silent
   errs = [e for e in cr if e['status'] == 'error']
   for jn, c in Counter(e['job_name'] for e in errs).most_common():
       print(f'{c:3d}  {jn}')
   ```
   This immediately tells you which job(s) own the error count. If ONE job is the overwhelming
   majority (e.g. 50 of 75), investigate THAT job first — the rest of the fleet is probably fine.

   09-13 re-run shape (453 events, 00:00–06:00 UTC): 392 `cron_run` = 309 ok / 48 error / 35
   silent, plus 28 `restart` + 33 `log_error`. All 48 errors + the majority of the silent runs
   were the three mangled 5-min jobs `s`/`c`/`t` (12+18+18 errors respectively; the 4th mangled
   job `o` had zero indexed runs that day). By-job grouping on single-letter `job_name` values
   works directly — `job_name` is the single letter, not a full description, for debris jobs.

2. **Discriminate false-positive vs real for the dominant job.** Read the job's `summary` field(s)
   and cross-check the inbox file. A job whose `summary` is a **success-looking delivery artifact**
   (e.g. `🏭 <b>Autobot Factory Digest</b>` — the text of the Telegram message it *successfully
   posted*) is a **false-positive error**: the run succeeded and delivered; the indexer just counted
   the non-empty stdout / delivery as a failure. Confirm by grepping the hourly inbox
   (`journals/inbox/YYYY-MM-DD.md`) — the same job will appear as `✅` in healthy snapshots and `❌`
   in error snapshots, with the *identical* summary text in both. If the summary is a success
   message in a `❌` line, it is a measurement artifact, not an outage.

3. **Report the real vs false split explicitly.** Lead the digest with the honest number: "320/323
   healthy; the only two failing jobs are X (real, venv mismatch) and Y (false-positive — the digest
   posts fine, the indexer miscounts it)." Do NOT let a false-positive job's inflated count set the
   tone of the whole digest.

## What a false-positive error cost here

The Autobot Factory Health Aggregator reported **50 errors** this pass (the highest of any job). Its
sole "error summary" was `🏭 <b>Autobot Factory Digest</b>` — the digest it successfully delivered.
Naively reporting "Autobot: 50 errors, needs investigation" would have sent a future session chasing
a non-bug. The correct call: healthy; optionally flag the **indexer** (the component that counts a
successful digest delivery as `status: error`) for a small fix so the count stops inflating — that
indexer fix is low-priority and separate from the fleet's actual health.

## Distinct from the 18-day blackout

Do not conflate this with the journal-pipeline blackout (`references/journal-pipeline-blackout-two-causes-2026-09-12.md`).
That was a **real** break (feeder `swarmlock` venv mismatch + recap `is_job_runnable` fork skew).
This reference is about the **measurement** layer: the same event index that *proves* the blackout was
real also over-counts a healthy digest job as "error." Read both sides of the index — the real
failures and the false ones — before you report a number.

## Pitfalls
- Do not report a raw "N errors" total without the by-job breakdown + false-positive check. A single
  healthy digest job can manufacture most of the count.
- A `❌` line whose summary is a success/delivery message is a false positive; a `❌` line whose
  summary is a traceback/`ModuleNotFoundError`/`ImportError` (or empty with a `last_error` in
  `jobs.json`) is real. When in doubt, read `last_error` in `cron/jobs.json` — it carries the full
  traceback the index `summary` truncates.
- The event index is the **collector's** per-hour record; a job that "errors" there but whose
  `last_status` in `cron/jobs.json` is `ok` (or vice versa) means the two sources disagree about the
  run's outcome — reconcile against `jobs.json` `last_error` before reporting.
- Don't trust a naive `ts`/`timestamp` field probe — the field is `_timestamp`. A wrong sort key
  fails silently (no error, just an empty-key sort), so the bug is invisible until someone notices
  the "latest event" is stale.

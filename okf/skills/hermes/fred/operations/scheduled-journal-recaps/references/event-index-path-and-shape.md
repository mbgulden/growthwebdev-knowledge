# Event-index path + shape (ad-hoc verification scans)

For a quiet-cycle / no-agent cron pass that needs to scan "what happened in the
journal event index since last pass," this is the working location and shape.
Discovered 2026-09-13 (a cron pass first mis-guessed
`~/.hermes/profiles/orchestrator/events/events-YYYY-MM-DD.json` — that dir does
NOT exist — then `find` located the real file).

## Location

```
/home/ubuntu/work/Hermes-Research/journals/.index/events-YYYY-MM-DD.json
```

- One file per day, UTC.
- NOT under the Hermes profile dir. The `journals/` root is
  `/home/ubuntu/work/Hermes-Research/journals/` (same root the daily recap
  `.md` files live under — e.g. `journals/2026/09/13.md`). The `.index/` subdir
  is the event stream the recap pipeline consumes.

## Shape

- Top level is a **bare JSON list** (array), not an object.
- Each event has a **`_timestamp`** field (ISO-8601 UTC, e.g.
  `2026-09-13T06:00:32Z`). The field is `_timestamp`, **not** `ts`.
- `type` values observed 2026-09-13: `cron_run`, `log_error`, `restart`.
- `cron_run` events: the outcome status has varied by run — read it from the
  first event before asserting a count (`status` at top level in some runs,
  `data.status` in others). Do not hardcode the path.
- `log_error` events carry a `count` and a `latest` list of snippets.
- `restart` events carry a `snippet`.

## Quiet-cycle scan recipe (verified 2026-09-13)

```python
import json
events = json.load(open(
    "/home/ubuntu/work/Hermes-Research/journals/.index/events-2026-09-13.json"))
print(len(events), events[0]["_timestamp"], events[-1]["_timestamp"])
# "no new events since last pass" is valid when events[-1]._timestamp <= last-pass time
```

The index is written in **batches**, so on a quiet-cycle pass the last event
often predates your run (e.g. last event 06:00:32Z at a 06:30Z check). That is a
normal finding ("index not yet advanced"), not a pipeline stall. Pair with
`mcp__journal__journal_freshness` to confirm `last_index_day` /
`last_daily_recap` still equal today.

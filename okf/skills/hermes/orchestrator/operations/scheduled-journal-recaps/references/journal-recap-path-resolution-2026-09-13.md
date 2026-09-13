# Journal / Recap Path Resolution (cold-start re-verify)

Class-level recipe for reading a freshly-landed daily recap or event index during a
cold-start cron re-verification pass. The failure mode this captures was hit live
**2026-09-13 (Fred / orchestrator cold-start cron)**: three different path styles
failed where a plain absolute path worked, and each false failure burned a tool call
before the real file was read.

## The failure (observed)

Goal: read `/home/ubuntu/work/Hermes-Research/journals/2026/09/13.md` (today's recap).

1. **Relative `read_file`.** `read_file("state/current.json")` and
   `read_file("<rel>/13.md")` returned **File not found** — the CWD was not the
   journals/profile root. Same class as the relative-vs-absolute bug for
   `state/current.json` (see `session-state-handoff` → "Where the file lives").
2. **`readlink -f` + `tail`.**
   `L=$(readlink -f .../journals/latest.md)` then `tail -c N "$L"` resolved
   `latest.md` → `.../journals/13.md` and `tail` failed
   **"cannot open `.../journals/13.md`"** in the same shell, even though
   `ls .../2026/09/` showed the real file at `2026/09/13.md`. The `readlink -f`
   target was not the file the shell would open.
3. **`find -name '13.md'`.** Returned **four** hits across year dirs
   (`2026/07/13.md`, `2026/08/13.md`, `2026/06/13.md`, `2026/09/13.md`) — a bare
   day-name match is ambiguous unless you constrain the year+month.

The file existed the whole time at the explicit absolute path. Every failed path
style was a *path* bug, not an *existence* bug.

## Durable rule

The daily recap lives at the **explicit absolute** path:

```
<journals-root>/<YYYY>/<MM>/<DD>.md
# e.g. /home/ubuntu/work/Hermes-Research/journals/2026/09/13.md
```

- **Read/tail/grep it directly** by that absolute path.
- **Do NOT** chase the `latest.md` / `latest-inbox.md` / `latest-weekly.md`
  symlinks with `readlink -f` + `tail` as the primary path. Use them only to
  *discover* which day is current, then switch to the absolute `<YYYY>/<MM>/<DD>.md`.
- When a read fails **"File not found"** but a sibling read in the same command
  succeeds, the **path** (not the file) is the bug — re-derive the absolute path
  from year/month/day rather than retrying the relative/symlink form.
- The **event index** for a given day is at
  `<journals-root>/.index/events-<YYYY-MM-DD>.json` (hidden dir — `ls` of the
  journal root does not show it; `find ... -maxdepth 3 -iname '*events*<YYYY-MM-DD>*'`
  locates it). Read it as JSON; the per-event timestamp field is `_timestamp`
  (not `ts`/`timestamp`/`time`), ISO-8601 UTC.

## Why it matters on a cold-start re-verify

The FIRST-REPLY REQUIREMENT for a cron cold-start is to surface
`current_state.one_line`, `next_action.title`, every `in_flight[]`, and every
`pending_decisions_for_human[]` **before anything else** — and the skill's own
"live-recheck" step means you re-read the journal + event index + Linear before
trusting the handoff. A path-resolution false-failure here does not change the
*content* of what you report, but it (a) burns tool calls, (b) can make a healthy
pipeline look broken for a turn, and (c) tempts a "journal missing / pipeline
stale" overclaim if you don't re-derive the absolute path. Verify the path, not
the pipeline, before surfacing any "freshness" problem.

## Quick one-liner (known-good)

```bash
# Today's recap (UTC) by absolute path:
D=$(date -u +%Y); M=$(date -u +m); Dd=$(date -u +d)
J="/home/ubuntu/work/Hermes-Research/journals/$D/$M/$Dd.md"
[ -f "$J" ] && tail -c 1200 "$J"

# Today's event index:
E="/home/ubuntu/work/Hermes-Research/journals/.index/events-$(date -u +%F).json"
[ -f "$E" ] && echo "$E ok"
```

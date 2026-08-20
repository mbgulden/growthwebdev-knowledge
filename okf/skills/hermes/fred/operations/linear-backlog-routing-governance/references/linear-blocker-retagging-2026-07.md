# Linear blocker retagging pattern — July 2026

## Situation

A Nightly Autonomous Backlog Worker reported six `dispatch:ready` issues that were blocked by unresolved prerequisites. Some blockers were actually already complete, some remained true blockers, and Linear became rate-limited during live remediation.

Representative blocker graph:

| Downstream | Prerequisites | Correct routing after verification |
|---|---|---|
| GRO-3306 | GRO-3304, GRO-3305 | Release when both prerequisites are complete |
| GRO-3357 | GRO-3325, GRO-3328 | Release when both prerequisites are complete |
| GRO-3367 | GRO-3366 | Release when prerequisite is complete |
| GRO-3299 | GRO-3298 | Hold while prerequisite remains incomplete |
| GRO-3354 | GRO-3337, GRO-3348 | Hold while any prerequisite remains incomplete |
| GRO-1554 | GRO-711 | Hold while prerequisite remains incomplete/unknown |

## Durable technique

### 1. Model the blocker graph explicitly

Use a map like:

```python
BLOCKER_GRAPH = {
    "GRO-3299": ["GRO-3298"],
    "GRO-3306": ["GRO-3304", "GRO-3305"],
    "GRO-3354": ["GRO-3337", "GRO-3348"],
    "GRO-3357": ["GRO-3325", "GRO-3328"],
    "GRO-3367": ["GRO-3366"],
    "GRO-1554": ["GRO-711"],
}
```

Then classify each downstream by live prerequisite state:

- `all(prereq.state.type == "completed")` → release downstream as `dispatch:ready`.
- any incomplete prerequisite → remove downstream `dispatch:ready`, add hold label, comment with exact unmet blocker(s).

### 2. Clean completed prerequisites

For prerequisites already completed in Linear:

- remove `dispatch:ready`
- remove `agent:peer-review`
- remove `agent:needs-human-review`
- add/keep `agent:done`

This prevents completed foundation tickets from being reprocessed and re-reported as blockers.

### 3. Avoid false completion

Never mark a prerequisite Done based only on a downstream issue needing it. Completion requires direct exit evidence. If the state is unknown or Linear cannot be queried, leave the issue alone and schedule a retry.

### 4. Linear rate-limit handling

If Linear returns `RATELIMITED` / `Rate limit exceeded`:

1. Stop live mutation attempts.
2. Keep the deterministic retag script ready.
3. Schedule a one-shot cron after the current one-hour window resets.
4. Report that live mutation is pending due to rate limit, not that the work is complete.

Example cron shape:

```python
cronjob(
    action="create",
    name="One-shot Linear blocker retag after rate-limit reset",
    no_agent=True,
    repeat=1,
    schedule="<ISO timestamp after reset>",
    script="linear_blocker_unblocker_YYYYMMDD.py",
    deliver="origin",
)
```

## Ad-hoc verification shape

When the retagger is a script, verify without touching live Linear:

1. Create a temp verifier under `/tmp` using `mktemp /tmp/hermes-verify-linear-blocker-unblocker-XXXXXX.py` or Python `tempfile`.
2. Import the retagging script with `importlib.util.spec_from_file_location`.
3. Monkeypatch:
   - `issue_query`
   - `update_labels`
   - `comment`
4. Feed mocked issues covering:
   - completed prerequisite with stale `dispatch:ready`
   - completed prerequisite with stale `agent:peer-review`
   - downstream with all prerequisites complete
   - downstream with one incomplete prerequisite
5. Assert:
   - completed prerequisites end with `agent:done` and no dispatch/review/hold labels
   - complete chains get `dispatch:ready`
   - incomplete chains lose `dispatch:ready` and get hold labels
   - explanatory comments are produced for every downstream routing decision
6. Remove the verifier and report the path plus cleanup result.

Expected output style:

```text
AD_HOC_VERIFY_PASS Linear blocker retag behavior: cleans completed prereqs, releases ready chains, holds unmet chains
cleanup=removed /tmp/hermes-verify-linear-blocker-unblocker-XXXXXX.py
cleanup_exists=false
```

Label the result **ad-hoc targeted verification**, not full-suite green.

## User preference reinforced

Michael wants blocker handling to end with exact owner/exit-criteria state in Linear, not vague backlog statements. Report remaining blockers bluntly and only release downstream work when prerequisites are actually satisfied.

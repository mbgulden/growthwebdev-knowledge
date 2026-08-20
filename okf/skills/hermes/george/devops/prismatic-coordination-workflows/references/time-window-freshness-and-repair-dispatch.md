# Time-window freshness review and same-head repair dispatch

Use this when a Prismatic PR claims recent-log, journal, queue, heartbeat, lease, or timestamp freshness behavior.

## Session-derived trigger

A PR can have exact-base, clean mergeability, and green hosted CI while still being semantically blocked if freshness tests are tied to today's date or if the implementation checks only the lower bound of a time window.

## Review probes

1. Bind the exact candidate first: base SHA, head SHA, tree SHA, changed paths, PR URL, hosted CI state.
2. Inspect tests for wall-clock coupling:
   - hard-coded current dates;
   - no frozen clock or injected `now`;
   - tests that pass only during the session day/week.
3. Probe both sides of the intended time window:
   - `seen < now - window` must be stale;
   - `seen == now - window` must match the documented cutoff policy;
   - `now - window < seen <= now` must be fresh;
   - `seen > now` must be rejected unless a bounded future-skew policy is documented and tested.
4. Prefer one captured UTC `now` per function call/test fixture. Avoid computing `now` repeatedly inside loops when boundary precision matters.
5. Add deterministic frozen-time coverage for tail freshness, future-line rejection, and exact cutoff behavior before accepting the PR.

## Dispatch/coordination pitfall

If George posts a GitHub repair packet and also schedules a Telegram lane prompt, do not treat a forced scheduler `run` as delivery proof unless the job record shows the intended target and successful delivery. A malformed/manual run can consume a one-shot locally. If that happens:

1. mark the failed run as discarded;
2. create a fresh one-shot delivery with the exact bot mention;
3. update handoff/control-state to the live retry job id;
4. keep the GitHub PR comment as the authoritative durable dispatch packet if chat delivery is unproven.

## Proof packet

```text
PR=<url>
BASE=<sha>
HEAD=<sha>
TREE=<sha>
PATHS=<allowed paths>
HOSTED_CI=<state, but note if invalidated>
SEMANTIC_PROBES=<future rejected, stale rejected, cutoff, fresh accepted>
FROZEN_TIME_TESTS=<PASS|FAIL|MISSING>
GEORGE_VERDICT=<CLEAN|REPAIR>
DISPATCH_PACKET=<GitHub comment or durable prompt path>
CHAT_DELIVERY=<verified|scheduled|failed_not_claimed>
NOT_CLAIMING=<merge/deploy/Linear/cap/etc.>
```

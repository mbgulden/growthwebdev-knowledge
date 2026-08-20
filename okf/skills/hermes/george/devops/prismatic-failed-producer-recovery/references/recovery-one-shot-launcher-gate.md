# Recovery one-shot launcher gate

Use this reference after a failed-producer recovery contract/envelope has passed and the next operational step is a one-shot event launcher.

## Why this exists

A `CLEAN/PASS` recovery contract or deployed admission envelope does not prove the executable launcher is safe. The launcher can still fail or mutate live state because of control-flow bugs, mismatched helper interfaces, cleanup variables scoped inside failing helpers, timestamp collisions, or verifier-only assumptions.

## Required launcher review before live POST

Freeze and hash the launcher script and proof log, then require exact-artifact review of:

- exact task id, task file hash, base commit/tree, worktree, idempotency key, producer identity, and report paths;
- live zero-state checks before any credential read, policy/control replacement, event POST, consumer run, or producer launch;
- replay rejection / one-event behavior;
- narrowed policy/private config and whether schema/policy validation uses actual deployed parser/policy objects;
- durable event reconciliation after POST and consumer/no-retry behavior;
- token handling: hash-only output, no raw token/report leak;
- restoration and cleanup on every exception path.

If a delegated review ignores the artifact/hash or returns unrelated project guidance, record it as `INVALID_NOT_A_REVIEW`; it is not a partial pass.

## Control-flow failure-injection checklist

Use isolated temporary paths or monkeypatch module constants so tests do not touch live policy/control/database/network.

1. Compile/import the launcher.
2. Assert exact payload fields and stable idempotency key.
3. Force a `prepare()` failure after partial artifact creation, e.g. invalid private JSON after report/window/policy temp paths exist.
4. Assert return code/error path is fail-closed and live-equivalent policy/control bytes are unchanged.
5. Assert window/private temp artifacts are removed even after partial preparation.
6. Stub validation only after a successful isolated preparation and run preflight-only.
7. Assert preflight-only returns success, restores policy/control, removes window/private temp artifacts, and does not POST/run consumer/producer.
8. Run two immediate preflight/error paths and prove report directories are unique; prefer microsecond timestamps or a deterministic uniqueness suffix.
9. Re-scan source for stale predecessor identities and impossible helper interfaces, especially changed return values/unpack sites.

## Implementation lessons captured from CRONRUNNERREPD-1

- If `prepare()` returns six values but `run()` unpacks four, the script can pass payload/static checks while failing immediately after creating temp files.
- Cleanup paths assigned inside `prepare()` are not available if `prepare()` raises early. Precompute `window`, `policy_temp`, `private_path`, `outer_path`, and original policy/control bytes in `run()` before entering `try`, then pass them into `prepare()`.
- Second-resolution stamps can collide during fast failure-injection tests; one-shot report directories should include microseconds or another uniqueness component.
- For high-risk execution gates, dispatch two focused reviews: one full exact-launcher review and one exception/finalization/control-flow review.

## Proof packet additions

```text
LAUNCHER_SCRIPT=<path>;sha256=<sha>
LAUNCHER_PROOF=<path>;sha256=<sha>
ENVELOPE_REVIEW=<delegation>:CLEAN/PASS
LAUNCHER_REVIEW=<delegation>:pending|CLEAN/PASS|BLOCKED|INVALID_NOT_A_REVIEW
PARTIAL_PREP_FAILURE_TEST=<PASS|FAIL|NOT_RUN>
SUCCESS_PREFLIGHT_TEST=<PASS|FAIL|NOT_RUN>
UNIQUE_REPORT_DIRS=<PASS|FAIL|NOT_RUN>
LIVE_PATHS_TOUCHED=false
POST=false
CONSUMER=false
PRODUCER=false
NOT_CLAIMING=launcher acceptance,event,consumer,producer,source repair,commit,candidate,push,PR,merge,deploy,or Linear write
```

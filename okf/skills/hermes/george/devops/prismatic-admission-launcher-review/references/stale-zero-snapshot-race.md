# Stale zero-snapshot race in one-shot admission launchers

## Durable lesson

A zero-state snapshot taken before a long sequence of live checks is not sufficient proof that it is safe to open temporary credentials or controls. The live event-log state can change after the initial snapshot and before mutation authority opens.

## Correct pattern

1. Run the normal live identity checks: gateway/process/listener/health, Git head/tree/status, task-copy hashes, and payload/envelope bindings.
2. Immediately before token generation or any control/policy/credential write, resample the canonical admission counts.
3. Store the fresh snapshot in the result object for receipt visibility.
4. Fail closed before any mutation if any value is nonzero.
5. Rerun `--preflight-only`, bind the fresh receipt hash, and freeze a superseding envelope.

Example launcher shape:

```python
pre_control_counts = event_counts()
result["pre_control_counts"] = pre_control_counts
if any(value != 0 for value in pre_control_counts.values()):
    raise RuntimeError("live_state_nonzero_before_control_open")

token = secrets.token_urlsafe(48)
```

## Review discipline

If one reviewer passes the broad launcher but another flags stale pre-control counts, the stale-count blocker wins. Preserve the blocked artifact hash, patch narrowly, and send both corrected launcher and superseding envelope back through exact-byte review.

## What not to persist

Do not encode the specific task id, commit, receipt path, or timestamp as reusable skill logic. Those belong in the session handoff/proof packet, not the skill.

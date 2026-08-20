# AGY Golden Thread scratchpad + Linear routing cleanup (2026-07-13)

## Trigger

AGY Golden Thread Project Review delivered a noisy but successful no-agent cron message:

```text
[AGY-GT-REVIEW] Project state changed
[AGY-GT-REVIEW] AGY exit: 0
I am waiting for the background task to complete and print the analysis of the projects.
Gaps Detected
Remediation Paths
```

The important lesson: `AGY exit: 0` plus headings is **not evidence** when AGY also says it is waiting for a background task. Treat this as a trigger to recover rows and verify live state, not as a reliable report.

## Procedure

1. Recover the latest real output file from the cron output directory:

```text
~/.hermes/profiles/orchestrator/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
```

For `AGY Golden Thread Project Review`, compare the latest small/noisy output against prior larger/full row outputs for context. Do not act from digest headings alone.

2. Extract all issue identifiers from the latest and prior relevant rows.

3. Query Linear live before mutating anything. The cron can be stale or hallucinated. Classify each issue by live state:

- completed but still has `dispatch:ready` / agent routing labels → remove stale routing labels, do not reopen.
- intentionally deferred → move to Backlog if needed, add `dispatch:paused`, remove active agent routing.
- awaiting human review/approval → remove `dispatch:ready`, add `dispatch:paused` and/or `agent:needs-human-review`.
- valid active work → assign/reassign to the real owner and keep only appropriate execution labels.
- cited local artifact missing (for example `RESULT.md`) → say the remediation is stale; do not pretend it exists.

4. Comment on each touched Linear issue with the reason for the routing/state change.

5. Patch the no-agent wrapper if it accepted AGY scratchpad as valid evidence.

## Sanitizer pattern

Add a small sanitizer that removes AGY waiting/progress chatter while preserving evidence tables:

```python
def sanitize_agy_output(output: str) -> str:
    if not output:
        return ""
    scratchpad_prefixes = (
        "i am waiting for the background task",
        "i'm waiting for the background task",
        "i will wait for the background task",
        "waiting for the background task",
        "let me wait for the background task",
    )
    kept = []
    for line in output.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            if kept and kept[-1] != "":
                kept.append("")
            continue
        if any(lower.startswith(prefix) for prefix in scratchpad_prefixes):
            continue
        kept.append(line)

    cleaned = "\n".join(kept).strip()
    if not cleaned:
        return ""

    allowed_markers = (
        "### Gaps Detected",
        "### Security/Credential Bleeds",
        "### Remediation Paths",
    )
    if any(marker in cleaned for marker in allowed_markers):
        return cleaned

    if "background task" in cleaned.lower():
        return ""
    return cleaned
```

If sanitized output becomes empty, fall back to deterministic local review rather than delivering AGY scratchpad.

## Verification pattern

Use a focused `/tmp/hermes-verify-*` script created with `tempfile.mkstemp(...)` that checks:

- `py_compile` passes for the changed wrapper.
- pure background-task prose sanitizes to empty.
- mixed scratchpad + real tables removes waiting chatter but preserves:
  - `### Gaps Detected`
  - `### Security/Credential Bleeds`
  - `### Remediation Paths`
  - ticket identifiers such as `GRO-3425`
- live Linear readback matches intended state/label/assignee outcomes.

Report as ad hoc targeted verification, not suite green.

## Pitfalls

- Do not send `/approve` or approve paused orchestration blindly from a cron row. Live-check whether the issue is actually blocked on human review and whether the project should still be active.
- Do not leave `dispatch:ready` on completed issues; it causes completed work to resurface as blockers.
- Do not keep agent labels on deferred work; use `dispatch:paused` instead.
- Do not trust paths like `/archive/agy_sandboxes/<issue>/RESULT.md` unless the file exists now.
- Do not let no-agent crons deliver all-clear/progress/scratchpad prose to Michael; deliver only compact actionable findings or stay silent.

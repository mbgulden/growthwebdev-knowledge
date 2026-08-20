# Needs-human-review scanner brake

## When to use

Use this when a Ned-lane Linear issue is correctly parked in `Todo` with `agent:needs-human-review` (or `requires:human-approval`) but the Ned cron scanner still emits it as `TASK:GRO-XXXX`.

This is the code-level companion to the blocked external-capability requeue brake: adding the label in Linear is not sufficient if the scanner query only filters by Ned ownership labels.

## Durable lesson

A human-review blocker label must be honored in the scanner's autonomous-task selection, not only in the issue's labels. Otherwise the issue remains visible as open Ned work and repeats every cron wakeup.

## Confirmed pattern

1. Verify Linear shows the blocked issue in `Todo` with:
   - `agent:ned-infra` / other Ned owner label still present
   - `agent:needs-human-review` or `requires:human-approval`
2. Run the Ned scanner:
   - `cd /home/ubuntu/.hermes/profiles/ned/scripts`
   - `python3 prismatic/lanes/ned/scan_tasks.py >/tmp/scan.txt 2>&1`
3. If output still contains `TASK:<blocked issue>`, patch scanner selection logic rather than re-running `finalize_task.sh`.

## Patch shape

In `prismatic/lanes/ned/scan_tasks.py`, keep the Linear query broad enough to list open Ned-owned issues, but filter before dispatch/task emission:

```python
BLOCKING_LABELS = {"agent:needs-human-review", "requires:human-approval"}


def is_autonomous_task(issue: dict) -> bool:
    labels = {l.get("name") for l in issue.get("labels", {}).get("nodes", [])}
    return not (labels & BLOCKING_LABELS)


def fetch_ned_issues() -> list:
    result = linear_gql(QUERY_OPEN_NED_ISSUES)
    nodes = result["data"]["team"]["issues"]["nodes"]
    return [issue for issue in nodes if is_autonomous_task(issue)]
```

## Verification

After patching:

```bash
python3 -m py_compile /home/ubuntu/.hermes/profiles/ned/scripts/prismatic/lanes/ned/scan_tasks.py
cd /home/ubuntu/.hermes/profiles/ned/scripts
python3 prismatic/lanes/ned/scan_tasks.py >/tmp/scan-after.txt 2>&1
```

Check:

```text
mentions_<blocked_issue>=False
emits_TASK_<blocked_issue>=False
```

It is acceptable for the scanner to emit a different open task; the required fix is that the human-review-blocked issue is no longer selected as the active autonomous `TASK:`.

## Pitfalls

- Do not remove the Ned ownership label from genuinely in-lane blocked work just to silence the scanner. Preserve owner labels and add the human-review blocker label.
- Do not run `finalize_task.sh` on a blocked issue merely because the cron prompt says to execute it. That promotes an unsatisfied external-capability task to review.
- Do not rely on Linear label state alone as proof the cron loop is braked. Re-run the actual scanner and inspect `TASK:` output.

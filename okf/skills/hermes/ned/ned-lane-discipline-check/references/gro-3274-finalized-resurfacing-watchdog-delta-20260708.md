# GRO-3274 finalized-resurfacing watchdog delta — 2026-07-08

## Trigger

A cron pickup resurfaced `GRO-3274` even though the issue was already finalized:

- Linear state previously verified as `In Review`
- Labels previously verified as `agent:ned`, `agent:peer-review`
- Branch: `ned/GRO-3274`
- Branch HEAD matched `origin/ned/GRO-3274`
- Open clean PR existed
- Prior `## Ned finalization report` + repair comment existed
- Artifact and archived `RESULT.md` existed

## Correct disposition

Do **not** rerun `finalize_task.sh` and do **not** post duplicate Linear comments for the old issue. Treat the pickup as finalized-resurfacing verification noise **unless** the focused verification command itself returns a fresh operational signal.

If Linear API rate limiting prevents a fresh issue re-query during this resurfacing check, do not mark the old issue blocked when branch/PR/artifact/local issue-batch evidence is enough to prove completion. Report the API exhaustion as part of the fresh operational delta instead.

## Validated verification sequence

1. Query Linear issue state/labels/comments when the API allows it. If the API is exhausted, use the local `/tmp/issue-batches/GRO-3274.txt` task spec plus existing branch/PR/artifact evidence and say the Linear re-query was rate-limited.
2. Verify branch/remote/PR:
   - `git ls-remote --heads origin ned/GRO-3274`
   - `gh pr list --head ned/GRO-3274 --json number,state,isDraft,mergeStateStatus,headRefOid,url,title`
3. Verify artifact paths:
   - `scripts/ops/gro-3274-tier1-silent-cron-failures-result.md`
   - `/archive/agy_sandboxes/GRO-3274/RESULT.md`
4. Rerun focused checks named in the artifact, including:
   - `python3 -m py_compile ...`
   - `bash -n .../gpt_oss_quota_probe.sh`
   - `python3 .../tier1_silent_failure_watchdog.py --dry-run --json`

Use a detached temporary worktree from `origin/ned/GRO-3274` for this verification so the dirty shared checkout is not touched. Remove the worktree afterward.

## Fresh delta variant A — single Linear API rate-limit failure

The old GRO-3274 completion evidence stayed intact, but the watchdog dry-run returned a new active silent failure:

```json
{
  "total_jobs": 92,
  "silent_failures": 1,
  "new_failures": 0,
  "failures": [
    {
      "job_id": "ce3dd849ede5",
      "name": "Hermes daily journal snapshot",
      "profile": "orchestrator",
      "root_cause": "linear (linear-api: endpoint or token issue, check graphQL response)"
    }
  ]
}
```

Cron state/root cause confirmed:

```text
/home/ubuntu/work/prismatic-engine/prismatic/journal.py:474
sync = reg.get("_last_sync", {})
sync.get(...)
AttributeError: 'str' object has no attribute 'get'
```

Live registry shape:

```text
/home/ubuntu/work/project-registry.json
_last_sync = "2026-07-07T20:08:56.803386+00:00"
```

## Fresh delta variant B — 3-failure Linear-rate-limit storm

A later resurfacing pass verified the same branch/PR/artifacts, but Linear itself was exhausted:

```text
Linear API: rate-limited, remaining=0 / limit=2500 per hour
```

The focused watchdog dry-run then returned:

```json
{
  "total_jobs": 93,
  "silent_failures": 3,
  "new_failures": 2,
  "failures": [
    {
      "job_id": "ce3dd849ede5",
      "name": "Hermes daily journal snapshot",
      "profile": "orchestrator",
      "root_cause": "linear (linear-api: endpoint or token issue, check graphQL response)"
    },
    {
      "job_id": "ecc080d17c00",
      "name": "Kai Callback Monitor — nudge Kai when sub-agents complete",
      "profile": "orchestrator",
      "root_cause": "linear (linear-api: endpoint or token issue, check graphQL response)"
    },
    {
      "job_id": "a9087254f1bc",
      "name": "AGY Completion Pinger",
      "profile": "orchestrator",
      "root_cause": "linear (linear-api: endpoint or token issue, check graphQL response)"
    }
  ]
}
```

Job-specific confirmation:

- `ce3dd849ede5` (`Hermes daily journal snapshot`) still crashes in `prismatic/journal.py::extract_golden_thread_summary()` because `_last_sync` is a string but the code assumes a dict.
- `ecc080d17c00` (`Kai Callback Monitor`) fails through `linear_api_compat.py` / `prismatic.dispatcher.gql()` with Linear API `RATELIMITED`.
- `a9087254f1bc` (`AGY Completion Pinger`) fails with `Failed to query Linear: HTTP Error 400: Bad Request`; in the same verification window the API quota was confirmed exhausted.

## Response rule

For finalized resurfacing:

- If verification is clean and produces no new operational signal: final response exactly `[SILENT]`.
- If verification produces a fresh unrelated watchdog/infra signal: send a concise cron report naming the new job/root cause/impact, while explicitly stating no duplicate finalize/comment was run for the already-finalized issue.
- If Linear API rate limiting blocks only the confirmation query but branch/PR/artifact evidence is intact, do not escalate the old issue as blocked. Include the API exhaustion in the watchdog delta because it is operationally relevant and may itself be causing fresh silent failures.

This is a cron-channel operational delta, not a reason to mutate the resurfaced Linear issue.
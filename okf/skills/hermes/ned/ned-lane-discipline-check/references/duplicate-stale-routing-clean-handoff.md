# Duplicate stale-routing clean handoff

Session anchor: GRO-2438 reappeared in Ned's scanner after prior clean handoff comments had already removed it from Ned's lane.

## Trigger
Use this when a single issue is routed to Ned, but the issue thread already contains a recent Ned clean-handoff / stale-routing cleanup comment and the fresh source check still matches that prior owner-lane condition.

Typical signals:
- Current labels include `agent:ned` + `dispatch:ready` again after a prior comment said `agent:ned` was removed.
- Prior comments explicitly say "clean handoff", "owner-level", "not a Ned code fix", or name another owner label such as `agent:orchestrator`.
- The underlying artifact is in another profile's cron/job ledger (`fred` or `orchestrator`), not Ned's ledger.
- Fresh evidence confirms the same state rather than a new Ned-lane implementation task.

## Required source checks before disposal
Do not conclude "wrong lane" from labels alone. Verify all accessible primary sources first:
1. Read the Linear issue including comment thread.
2. Inspect the named source artifact directly when present (cron `jobs.json`, latest cron output, process/log state, repo file, etc.).
3. Search OKF integration docs and relevant `.env` files if access/credential/source ownership is part of the question.
4. Use `session_search` if the prior handoff or recovery story may exist only in session history.

## Disposition
If the fresh source check matches the prior clean handoff:
- Do **not** call `finalize_task.sh`. That script would commit/transition a real but wrong-lane issue and can recreate the Pass-N+41 wrong-issue finalize failure mode.
- Do **not** edit another profile's cron/config from Ned unless explicitly directed.
- Apply a pinned-state Linear label mutation: remove `agent:ned`, keep the dispatch marker if the owner still needs pickup, add the correct owner label, and pin state to `Todo` in the same mutation to avoid Linear workflow side effects.
- Post a concise evidence comment explaining: what was checked, current live state, why this remains owner-lane work, and exactly which labels/state were set.
- Return `[SILENT]` for cron delivery unless the finding needs Michael's explicit decision.

## Safe mutation shape
Use file-backed Python or `linear_api.py` helpers; avoid inline shell Markdown when comments contain backticks.

For raw GraphQL, the safe shape is:

```graphql
mutation($id:String!, $input:IssueUpdateInput!) {
  issueUpdate(id:$id, input:$input) {
    success
    issue { identifier state { name } labels { nodes { name } } }
  }
}
```

Variables:

```json
{
  "id": "GRO-XXXX",
  "input": {
    "stateId": "<Todo state UUID>",
    "labelIds": ["<dispatch:ready label UUID>", "<correct owner label UUID>"]
  }
}
```

Then post `commentCreate(input:{issueId:<issue UUID>, body:<file-backed Markdown>})`.

## GRO-2438 concrete example
Fresh evidence showed:
- Job `faf8d91da716` existed in `fred` + mirrored `orchestrator` cron ledgers, not Ned's.
- Both ledgers were paused with `paused_reason="Storage gate failed: /tmp or /archive free space below threshold."`
- Live disk was healthy, and a long-run orchestrator `agy_sandbox_event_supervisor.py --long-run --cron-mode` process was alive.
- Therefore the task was owner-level scheduler/cron-state review, not a Ned repo implementation.

Action taken: `agent:ned` removed, `dispatch:ready` kept, `agent:orchestrator` added, state pinned to `Todo`, evidence comment posted, final response `[SILENT]`.
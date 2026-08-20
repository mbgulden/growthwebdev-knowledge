# Stale-Phantom Duplicate Disposition — standalone triage workflow

> **Companion to:** `finalize-task-script-bug` (Modes A, C, D, G, H cover `finalize_task.sh` failure modes — those are *script interactions*). This file covers a **standalone Linear-API-only workflow** that is broader than just finalize_script failures: when a scanner re-files duplicates of canonical issues and you need to consolidate them without writing any code.

## TL;DR — the three-step workflow

When the scanner hands you a batch of duplicate Linear issues (typically 2-10 items, all filed by the same auto-sweep watchdog, all `Backlog`, all `agent:ned` because of a routing fallback):

1. **Classify** — for each issue, determine: (a) is a canonical issue already filed by a human/scheduler? (b) if not, which sibling in this batch is the oldest?
2. **Link + comment + transition** — for each NOT-canonical issue:
   - `issueRelationCreate(input:{issueId, relatedIssueId, type:"duplicate"})`
   - `commentCreate(input:{issueId, body:<Ned-triage-with-canonical-keywords>})`
   - `issueUpdate(id, input:{stateId: <Duplicate-id>})` — only after step 1 succeeds
3. **Skip `finalize_task.sh` entirely** — write an audit doc to the OKF branch, commit locally, **do not invoke `finalize_task.sh`**.

The reasoning for skipping finalize at step 3 is the same as Mode C proper fix: Backlog + no code + no reviewable artifact = no task deliverable. The script's only reason to exist is to commit code and transition a real issue to In Review. Neither applies here.

## Proven: 2026-06-30 SILENT-CRON batch (4 issues, all duplicates)

The Tier-1 silent-failure watchdog filed 4 SILENT-CRON issues on 2026-06-30:

- **GRO-3011** (orchestrator profile) + **GRO-3012** (fred profile) — both AGY Sandbox Supervisor silent-failing
- **GRO-2998** (orchestrator) + **GRO-2999** (fred) — both Fred Persistent Factory Monitor silent-failing

Action taken (verified at 13:57Z):

| GRO-ID | Disposition | Reason |
|---|---|---|
| GRO-3011 | Duplicate → GRO-2862 | Canonical anchor (state=In Progress, agent:fred dispatch:ready) already exists |
| GRO-3012 | Duplicate → GRO-2862 | Same |
| GRO-2998 | **Left in Backlog** (parking-lot anchor) | No canonical exists; 2998 is older of the 2 dups (created 0.019s before 2999) |
| GRO-2999 | Duplicate → GRO-2998 | 2999 is newer of the 2 Fred Persistent dups; parked on 2998 so the watchdog's next sweep dedups against a stable target |

All 3 transitioned issues are now state=Duplicate. GRO-2998 stays Backlog awaiting the orchestrator/fred cron-fix lane to claim it. Comment thread on each carries canonical-keyword self-tripwire language per `references/dry-run-as-guard-verification.md` §"Ned triage comment as a self-tripwire".

## Step 1: Classify — finding the canonical anchor

For each duplicate in the batch, query Linear for canonical anchors:

```bash
# Search by title fragment (the watchdog uses identical titles across re-fires)
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ issues(filter:{or:[{title:{contains:\"sandbox supervisor\"}},{title:{contains:\"Fred Persistent Factory\"}}]}, state:{name:{in:[\"Backlog\",\"Todo\",\"In Progress\",\"In Review\",\"Done\",\"Canceled\"]}}, first:50) { nodes { identifier title state { name } labels { nodes { name } } } } }"}'
```

Classify each scanned issue by:

1. **Canonical present?** Look for an issue that:
   - Has the same title fragment
   - Has a `dispatch:ready` label
   - Has `agent:<some-agent>` label (where `<some-agent>` is NOT `agent:ned`, since the routing bug routes fallback to ned)
   - Is in state `In Progress` or `In Review` (an actively-owned canonical)
   - Optionally, was created *before* this batch's first issue (you can compare `createdAt` — the canonical will typically be days/weeks older because the watchdog re-fires every 6h)

2. **No canonical present?** Pick the OLDEST issue in the batch (by `createdAt`). Use it as the "parking-lot anchor" — leave in Backlog, mark all newer siblings as Duplicate of it.

3. **Multiple canonicals?** (rare) Pick the one with `agent:<owner>` label matching the job's actual profile owner (e.g. `agent:orchestrator` or `agent:fred` for cron jobs). If tie, pick the one with the most recent `updatedAt`.

## Step 2: Three-Linear-API-call sequence per duplicate

For each duplicate issue (NOT the parking-lot anchor):

### 2a. `issueRelationCreate` — must come BEFORE state transition

```graphql
mutation($issueId: String!, $relatedIssueId: String!) {
  issueRelationCreate(
    input: {
      issueId: $issueId
      relatedIssueId: $relatedIssueId
      type: duplicate
    }
  ) {
    success
    issueRelation { id type relatedIssue { identifier } }
  }
}
```

**Why this MUST come first:** Linear rejects `issueUpdate(stateId: <Duplicate-id>)` without an existing duplicate relation. The error message is unhelpful (something about workflow state guards). Cost: ~30s to discover this from scratch; ~2s with idempotency check.

**Idempotency check before mutation:**

```graphql
query($id: String!) {
  issue(id: $id) {
    relations { nodes { id type relatedIssue { identifier } } }
  }
}
```

If a relation of `type:"duplicate"` to the canonical already exists, skip the create.

### 2b. `commentCreate` — Ned triage comment with canonical-keyword self-tripwire

The comment MUST include at least one of these canonical keywords (for the BLOCKED_COMMENT guard to trip on subsequent `finalize_task.sh` runs):

- `out[- ]of[- ]lane`
- `\bdequeued\b`
- `\brelabel\b`
- `wrong[- ]agent`
- `lane[- ]violation`
- `\bmisroute\b`
- `not an? (infrastructure|infra) task`
- `outside (ned|my) lane`

Canonical template (proven 2026-06-30):

```
[Ned triage — <DATE>]

This is a stale-phantom duplicate of <CANONICAL-ID>. The Tier-1 silent-failure
watchdog (tier1_silent_failure_watchdog.py) filed this issue on <FILED-AT>
when it detected the underlying job in error state. A canonical tracking
issue already exists and is being actively worked (<CANONICAL-ID>: state
<CANONICAL-STATE>, <AGENT-LABEL>, <DISPATCH-LABEL>).

Underlying job status (verified at <VERIFY-AT>):
- `<JOB-ID>`: state=<JOB-STATE>, enabled=<JOB-ENABLED>
- Last run: <JOB-LAST-RUN>
- Original failure: <JOB-FAILURE-SUMMARY>

Action taken: marking this issue as Duplicate of <CANONICAL-ID> via
`issueRelationCreate(type:duplicate)` + `issueUpdate(stateId: Duplicate)`.
No code change is required (job ownership and fix work lives with the
<PROFILE-OWNER> profile owner).

— Ned autonomous triage run
```

The phrase "stale-phantom duplicate" trips `\bdequeued\b` (via "duplica") — wait, no, it does NOT. The regex is `\bdequeued\b`, exact word match. The actual tripwires are `duplicate of`, `marking this issue as Duplicate`, or any explicit mention of "dequeue" / "out-of-lane" / "relabel". Verify with the grep recipe in `references/dry-run-as-guard-verification.md` §"Detection recipe" before posting.

### 2c. `issueUpdate` — transition to Duplicate state

```graphql
mutation($id: String!, $stateId: String!) {
  issueUpdate(id: $id, input: { stateId: $stateId }) {
    success
    issue { identifier state { name } }
  }
}
```

**Shape pitfall (already covered in `references/linear-api-gotchas.md` §"`issueUpdate`"):**

- `id` is TOP-LEVEL (NOT inside `input`)
- `stateId` is INSIDE `input` (NOT `state: <name>`)
- `IssueUpdateInput` does NOT accept `id` or `state` fields directly

State ID for `Duplicate` on the GRO team: `8a67aa62-ee98-4d67-a513-64217d8859c3` (verified 2026-06-30). Cache all workflow state IDs in `/tmp/linear-states.json` weekly — see `references/linear-api-gotchas.md` §"Workflow state UUIDs are stable per team" for the recipe.

### Why the comment goes between relation+state, not before

If you post the comment FIRST, the issue has no Duplicate relation yet, so:
- A subsequent `finalize_task.sh` call (somebody else's scan-triage cron fires before yours) will see the issue in Backlog + your fresh "duplicate" comment, but the BLOCKED_COMMENT guard won't recognize "duplicate" as a tripwire phrase — only the canonical keywords.
- The state transition can still fail without the relation.

Relation FIRST → comment second → state transition last is the only order that works cleanly.

## Step 3: Why skip `finalize_task.sh` for this workflow

`finalize_task.sh` assumes:

1. You wrote code and need it committed + pushed (Step 1 of the script)
2. You acquired a lane lock and need it released (Step 2)
3. The issue's In Review transition is what the next agent needs to see (Step 3)
4. A "finalization report" comment is informational for human reviewers (Step 4)

For stale-phantom duplicate disposition:

| Assumption | Holds? | Why |
|---|---|---|
| Code committed | NO | Pure API mutations, no code |
| Lock release needed | NO | `swarm_locks.json` is `[]` (empty) at scan-triage time — no Ned lock to release |
| In Review transition | NO | The whole point is to *avoid* In Review promotion (the issue is misrouted/redundant) |
| Finalization comment useful | NO | The Ned triage comment already documents everything; the script's finalization report would be noise |

Even if you call `bash finalize_task.sh --dry-run <issue-id>`, the script will print:

```
[finalize]   nothing to commit (working tree clean)
```

…at Step 1 and then proceed to attempt Step 3 — which would promote the already-marked-Duplicate issue (now state=Duplicate) to In Review (a workflow guard will reject this, but the dry-run wouldn't tell you that). Skipping finalize entirely is faster and cleaner.

## The 4-question gate for this workflow

Per Ned canonical task loop (r150 invariant + `references/dry-run-as-guard-verification.md` §"Detection recipe — when does the guard fail to fire?"):

| Q | Question | Answer for stale-phantom dup |
|---|---|---|
| Q1 | Code changes requiring commit? | NO |
| Q2 | Issue state transition? | YES — but `Backlog → Duplicate`, NOT `Backlog → In Review`. Different category. |
| Q3 | Reviewable artifact for next agent? | NO |
| Q4 | Infra threshold exceeded? | NO (always NO unless something else fired) |

Q1 + Q3 = NO ⇒ `finalize_task.sh HARD-SKIPPED`. The directive-style "Last action: bash finalize_task.sh" in the cron template is overridden by Q1+Q3 evidence — exactly per Mode C proper fix + r150 invariant.

## Parking-lot anchor pattern — when no canonical exists

For 2+ sibling duplicates with NO external canonical:

1. Sort by `createdAt` ascending
2. Pick the OLDEST as the parking-lot anchor
3. Leave it in `Backlog` (do NOT transition it)
4. Transition ALL newer siblings to `state=Duplicate` pointing at the parking-lot anchor

**Why the parking-lot anchor must be untouched:**

The Tier-1 watchdog's dedup logic keys on a stable target per job. If you transition ALL siblings to Duplicate and the next 6h sweep fires, the watchdog will see "no Backlog issue for this job" and:
- Either silently suppress the re-fire (best case — but you lose observability)
- Or, worse, re-file a fresh watch-dog-phantom because it has nothing to dedup against

By leaving ONE issue in Backlog as a stable target, the next sweep's dedup correctly classifies it as "already filed — do not re-issue" and you don't get new phantoms. The parking-lot stays until:
- A canonical is filed (then parking-lot → Duplicate of canonical, canonical stays)
- The cron is actually fixed (then parking-lot auto-resolves when the watchdog sees recovery)
- A human archive pass (then parking-lot → Canceled with a `[human]` label)

## Escalation note (recommended but out-of-scope for r138)

The Tier-1 silent-failure watchdog (`tier1_silent_failure_watchdog.py`, every 6h) has a routing bug: when the failing job has no `dispatch:ready` label, the watchdog falls back to `agent:ned` regardless of the job's profile owner. This produces the exact noise pattern seen on 2026-06-30 — every 6h, 2 dups per `orchestrator`/`fred` cron, both routed to Ned.

**Recommended fix (file separately, not as part of stale-phantom disposition):** patch `route_silent_failure()` in `tier1_silent_failure_watchdog.py` to:

1. Inspect the job's `profile` field (`orchestrator`/`fred`/`ned`/etc)
2. Map profile → agent label (`agent:orchestrator`/`agent:fred`/`agent:ned`)
3. Use that as the default assignee, with `agent:ned` only as last-resort fallback

Estimated fix size: 5-10 lines in `route_silent_failure()`, plus a unit test for the 4 profile cases. Out of scope for Ned's stale-phantom disposition because (a) the script lives in orchestrator's `scripts/` dir, not Ned's, (b) the change is to watchdog routing logic which is owned by the orchestrator/fred CRON-FIX lane.

## Operational recipe — copy/paste template

When a future Ned cron pass hands you a SILENT-CRON batch (or any scanner re-fire batch):

```bash
# 1. Verify the duplicate's underlying job state (per `hermes-cron-script-security`
#    §"Triage: stale detector issues" — don't trust the issue title, verify jobs.json)
python3 -c "
import json
for profile in ['orchestrator', 'fred', 'kai']:
    try:
        data = json.load(open(f'/home/ubuntu/.hermes/profiles/{profile}/cron/jobs.json'))
        for j in data.get('jobs', []):
            if j.get('id') in ['<JOB-ID>']:
                print(f'{profile}/{j[\"name\"]}: state={j.get(\"state\")}, enabled={j.get(\"enabled\")}, last_status={j.get(\"last_status\")}, last_run={j.get(\"last_run_at\")}')
    except FileNotFoundError:
        pass
"

# 2. If ALL underlying jobs are paused/healthy → these are stale phantoms. Apply the
#    three-step workflow above. Skip finalize entirely.
# 3. If any underlying job is still actively failing → file separate canonical
#    issue (or escalate to the profile owner), do NOT mark anything Duplicate
#    without a real fix plan.
```

## Cross-references

- `references/linear-api-gotchas.md` §"`commentCreate` lag" + §"Workflow state UUIDs"
- `references/dry-run-as-guard-verification.md` §"Ned triage comment as a self-tripwire"
- `hermes-cron-script-security` skill §"Triage: stale detector issues (silent_cron_detector can lag)"
- `finalize-task-script-bug` SKILL.md Mode C (Backlog detection), Mode C-refinement (BLOCKED_COMMENT guard), Mode H (curl+heredoc JSON escape avoidance — write your mutations to `/tmp/<one-off>.py`)

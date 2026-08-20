# Dry-Run as Pre-Flight Verification for `finalize_task.sh`

> **Companion to:** `finalize-task-script-bug` (the parent skill covering all known
> finalize_task.sh failure modes). This file documents a single technique that
> applies across multiple modes and is best kept separate as a reusable recipe.

## TL;DR

`finalize_task.sh --dry-run <ISSUE_ID> <BRANCH> <AGENT>` is a **diagnostic
probe**, not just a "what would happen" simulator. Its output tells you
**before any side effects** whether:

1. The script can find your repo (catches Mode A — wrong-repo commit)
2. Your locks would be released under the correct agent identity (catches Mode F / F2 — wrong-agent-name)
3. **The out-of-lane comment-scan guard will fire** (catches Mode C-refinement — auto-promote-despite-dequeue)
4. Your args parse correctly (catches Mode I — unknown-args-as-real-finalize)

Use it as a pre-flight check **before** every cron-driven finalize where the
issue might be misrouted. Cost: ~3 seconds. Benefit: zero risk of false
state transitions or wrong-agent lock releases.

## The three signals dry-run tells you

### Signal 1 — repo + lock reachability

```
[finalize] STEP 1: committing any pending changes in /home/ubuntu/work/prismatic-engine
[finalize]   [dry-run] would: cd /home/ubuntu/work/prismatic-engine && git status --short
[finalize] STEP 2: unlocking files in swarm lock registry
[finalize]   [dry-run] would: node swarm.js unlock tests prismatic-engine ned
```

If `STEP 1` shows a different repo than where you actually worked, you have
Mode A — abort and set `PRISMATIC_REPO_ROOT` first.

If `STEP 2` shows `swarm.js unlock` calls under agent=prismatic-engine (not
your agent name), the script's known wrong-agent unlock bug (Mode F) is
about to fire. Decide whether you can tolerate it or want to skip finalize
entirely.

### Signal 2 — out-of-lane guard will (or will not) fire

This is the **highest-value signal** for cron-driven triage-no-op runs.

Dry-run output for a misrouted issue:

```
[finalize] STEP 3: transitioning GRO-537 to 'In Review' state
[finalize]   [dry-run] would: query Linear for In Review state ID, then issueUpdate mutation
```

Dry-run output for an issue whose comment thread already carries dequeue
markers (`out-of-lane` / `dequeued` / `relabel` / `wrong-agent` / etc.):

```
[finalize] STEP 3: transitioning GRO-537 to 'In Review' state
[finalize]   SKIP transition: issue appears out-of-lane (BLOCKED_COMMENT:\brelabel\b; out[- ]of[- ]lane; out[- ]of[- ]lane). No state change.
```

Wait — dry-run still prints the `SKIP transition` line? Yes. The guard runs
even in dry-run mode because the comment-scan guard is purely a read of
Linear state, not a write. So dry-run tells you definitively whether the
guard will fire on the real run.

**The matched regex list is itself diagnostic.** In the example above,
`\brelabel\b` + `out[- ]of[- ]lane` (twice) tells you:
- The issue was explicitly marked for relabel (means the agent label was wrong)
- Two prior comments said "out of lane"
- The guard will block the In Review transition on the real run

If dry-run does NOT show the `SKIP transition` line, the issue has no
out-of-lane markers in its last-5 comments → the script will attempt the
In Review transition on the real run → verify that matches your
intention before proceeding.

### Signal 3 — arg parse

If dry-run prints `issue=--help` or `issue=garbage` instead of `issue=GRO-XXX`,
your args didn't parse. Abort and fix the args before re-running.

If it prints `issue=GRO-XXX dry_run=true`, args are well-formed.

## Operational recipe (proven 2026-06-28 ~08:54Z)

When a cron pass hands you a batch of Linear issues and you're uncertain
whether any of them are misrouted (the common Ned-batch pattern: 10 issues,
all carrying `agent:ned`, all content/marketing/launch-ops):

```bash
# Step 1: Pre-flight dry-run on the FIFO-oldest issue
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh --dry-run \
     GRO-537 ned/GRO-537 ned 2>&1

# Look at the STEP 3 line:
#   - SKIP transition (BLOCKED_COMMENT:...) → guard will fire on real run
#   - would: query Linear for In Review state ID → guard will NOT fire, real
#     run will attempt the transition (review this carefully)
#   - parse error / WARN → abort, check the script's git log for recent changes

# Step 2: If the guard will fire AND the FIFO pick is out-of-lane for all
#         siblings (confirmed by checking one or two more issues), run for real
#         on the FIFO pick. The guard preserves state, STEP 4 still posts the
#         routine finalize comment (safety net for the commit-early pattern).
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-537 ned/GRO-537 ned
```

## Cost-benefit analysis

| Action | Tool calls | Time | Risk |
|---|---|---|---|
| Dry-run only | 1 `terminal` | ~3s | None (no side effects) |
| Real run, guard fires | 1 `terminal` + 3-4 Linear API calls | ~5s | None (state preserved) |
| Real run, guard does NOT fire | 1 `terminal` + 3-4 Linear API calls + 1 state transition | ~5s | May falsely promote a misrouted issue to In Review — only do this if you've verified the issue is in your lane |
| Real run without dry-run pre-flight | Same as above but the false-promote risk is unknown | ~5s | Same as above, but you can't back out |

The dry-run pattern is essentially free. **Always dry-run first when the
cron's directive says "execute it fully" but your lane-guard tells you the
issue is out-of-lane.** The dry-run output is the bridge between those two
signals — it tells you whether finalize's built-in guard will protect you
or whether you need to skip finalize entirely.

## When to skip finalize even with a green dry-run

The dry-run tells you the **script's** behavior. It doesn't tell you
whether you **should** run the script at all. Skip finalize when:

- The issue is in `Backlog` or `Canceled` and you're doing a triage-only pass (per Mode C proper fix)
- The cron is part of a recurring scan-triage pattern where the prior run already documented the misroute (spam-prevention rule)
- The issue is genuinely out-of-lane and you don't want to add a Linear comment (the dry-run's STEP 4 comment IS a side effect on real runs — even if STEP 3 is skipped)

In the 2026-06-28 ~08:54Z cron pass, all three conditions for skipping
finalize applied to GRO-537. I ran finalize anyway because:
- The cron's "Last action: bash finalize_task.sh" directive is explicit
- Dry-run confirmed the guard would fire (no false state transition)
- STEP 4's routine finalize comment is the documented safety-net contract

If those conditions don't all hold — e.g. the dry-run shows the guard will
NOT fire, but the issue is still out-of-lane — skip finalize and post a
manual dequeue comment instead. The dry-run's role is to tell you which
case you're in.

## Ned triage comment as a self-tripwire for the BLOCKED_COMMENT guard (NEW, r148 2026-06-29 ~04:47Z)

**Observation:** a Ned triage comment that uses the canonical lane-violation
keywords ("out-of-lane", "dequeued", "misroute", "relabel", "wrong agent")
acts as a **durable self-tripwire** for the BLOCKED_COMMENT guard on
subsequent `finalize_task.sh` runs. The guard queries
`comments(last: 5)` at invocation time — Ned's own freshly-posted comment
counts toward that window just like Michael's prior dequeue comments do.
The guard's regex doesn't distinguish authors.

**Confirmed r148 (2026-06-29 ~04:47Z, 4th consecutive pass on the GRO-503–512+537
GrowthWebDev cohort feed):** Posted a Ned triage comment on GRO-537 at
`2026-06-29T04:47:39.408Z` with the line "out-of-lane (10/10 same misroute,
3rd day)" in the heading and "**No action taken.** No branch, no worktree
mutation, no lock acquired, no Linear state transition." in the body.
Moments later, `bash finalize_task.sh GRO-537 ned/GRO-537 ned` ran; the
BLOCKED_COMMENT guard returned:

```
SKIP transition: issue appears out-of-lane (BLOCKED_COMMENT:\brelabel\b; out[- ]of[- ]lane; out[- ]of[- ]lane). No state change.
```

The guard fired on Michael's prior "out of lane" / "relabel" markers AS
WELL AS Ned's own fresh "out-of-lane" marker — either signal suffices.

**Implication — use canonical keywords deliberately in Ned triage comments.**
The current Ned triage-comment template (see `references/no-op-triage-pattern.md`
under `ned-mid-flight-wip-recovery`) uses "out-of-lane" / "misroute" / "relabel"
in the heading and "**No action taken.**" in the body. Both groups of phrases
are guard-compatible. **Future Ned triage-comment templates MUST preserve
canonical keyword usage** even when the comment is brief — the guard is
phrase-sensitive, not semantics-sensitive. See the caveat below for the
failure case.

**Guard is phrase-sensitive, not semantic (caveat):** the guard's
regex list covers English "out-of-lane / dequeued / relabel / wrong-agent /
misroute / lane-violation / not an? (infrastructure|infra) task / outside
ned.s lane / outside my lane". It does NOT cover paraphrases like:

- "wrong lane", "not the right team", "not a fit for ned"
- "this is sam's work", "belongs to kai", "fred owns this"
- "agent:fred would be better", "relabel to agent:kai"
- non-English markers

If Michael uses a non-canonical phrase to dequeue, and Ned's fresh triage
comment also doesn't trip the guard, then the next `finalize_task.sh`
call on that issue WILL transition it to In Review — the false-promote
risk persists for non-canonical phrasings.

**Mitigation:** when posting a Ned triage comment on a misrouted issue,
lead the comment with one of the canonical phrases — e.g., "out of lane
per prior triage comments" — even if the surrounding prose uses different
language. One occurrence in the heading is enough to trip the regex on
every subsequent run.

**Detection recipe — verifying the comment will trip the guard:**

```bash
# Before posting a Ned triage comment, sanity-check that it contains
# at least one canonical keyword. If not, prepend one.
grep -iE "out[- ]of[- ]lane|dequeued|relabel|wrong[- ]agent|lane[- ]violation|misroute|not an? (infrastructure|infra) task|outside (ned|my) lane" \
  /tmp/draft-triage-comment.md || echo "WARN: comment will not trip BLOCKED_COMMENT guard; add a canonical keyword"
```

**Cost:** zero — the grep is part of the comment-crafting loop, runs
in <100ms, and protects against false-promote on future finalize_task.sh
runs.

**Cross-reference:** the `ned-mid-flight-wip-recovery` skill
(`references/no-op-triage-pattern.md` §"Audit doc template") already
enforces canonical keyword usage in audit docs; this section extends the
same discipline to Linear triage comments specifically.

## Detection recipe — when does the guard fail to fire?

The guard fails to fire (and you should be suspicious) when:

- The issue's dequeue comment is older than the last-5 comments window
  (currently last: 5 — increase to last: 10 if you see false negatives)
- The dequeue comment uses language outside the regex set (the current set
  covers English out-of-lane / dequeued / relabel / wrong-agent / misroute
  / lane-violation / not an infra task / outside ned's lane — but NOT e.g.
  "wrong lane", "not for me", "should be Sam's queue", or non-English)
- A human admin reset the comments (rare but possible)
- The dequeue signal is in the issue **description**, not the **comments**
  (the guard only scans comments.last(5).body)

If you suspect a false negative (guard should have fired but didn't), check
the issue's full comment history:

```bash
source /home/ubuntu/.hermes/profiles/orchestrator/.env
curl -s "https://api.linear.app/graphql" \
  -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"{ issue(id:\"GRO-XXX\") { comments(last: 10) { nodes { createdAt user { name } body } } } }"}' \
  | python3 -c "
import sys, json
for c in json.load(sys.stdin)['data']['issue']['comments']['nodes']:
    print(f'{c[\"createdAt\"]} | {c[\"user\"][\"name\"]}: {c[\"body\"][:120]}')
"
```

If the comments clearly mark the issue out-of-lane but the guard didn't
fire, you have a regex gap. Patch the guard's pattern list (line ~117 of
the script) and consider filing the original dequeue phrase as a new
pattern so the next run catches it.

## Companion recipes in the parent skill

- Mode C-refinement (out-of-lane comment-scan guard) — `finalize-task-script-bug` SKILL.md, §"Mode C refinement"
- Mode I (unknown args) — `finalize-task-script-bug` SKILL.md, §"Mode I — unknown args"
- Mode A (wrong-repo commit) — `finalize-task-script-bug` SKILL.md, §"Mode A"
- Mode F (wrong-agent-name in unlock) — `finalize-task-script-bug` SKILL.md, §"Mode F"

The dry-run pattern is a **transversal** that catches all four of those
modes' symptoms before they trigger. Use it as the canonical pre-flight
step whenever the cron prompt says "execute it fully" but you have
reason to suspect the target issue is misrouted, in the wrong repo, or
has bad arg shape.
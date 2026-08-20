# `agent:needs-human-review` sludge cleanup pattern

Use this when Michael approves cleanup of a noisy `agent:needs-human-review` queue where many issues are not real human blockers.

## Trigger

- A backlog/factory/Linear audit shows many open issues carrying `agent:needs-human-review`.
- Michael says to remove stale human-review labels where no explicit blocker exists and route work to AGY / Jules / Fred / peer-review by task type.

## Operating rule

Treat `agent:needs-human-review` as a triage signal, not proof Michael is needed.

Keep it only for explicit blockers:

- manual send / publish / outbound email / LinkedIn profile publishing
- recording, interview, audio, voice input
- credentials, billing, Stripe/FareHarbor/payment access
- explicit approval/decision/confirmation
- named Michael/Becca/Ella feedback blocker
- explicit “Michael only”, “requires Michael”, “do not send”, or consent language

Everything else should be routed to the correct executable lane and made dispatchable.

## Recommended workflow

1. Query live open Linear issues with `agent:needs-human-review` and non-completed/non-canceled states.
2. Classify into:
   - `KEEP_TRUE_HUMAN_BLOCKER`
   - `CLEAN_EXISTING_AGY`
   - `CLEAN_EXISTING_OTHER_AGENT`
   - `ROUTE_AGY`
   - `ROUTE_JULES` or implementation fallback label if Jules is unavailable
   - `ROUTE_FRED`
   - `ROUTE_PEER_REVIEW`
   - `ROUTE_FRED_TRIAGE`
3. For true blockers:
   - keep `agent:needs-human-review`
   - add `dispatch:paused`
   - remove `dispatch:ready`
4. For non-blockers:
   - remove `agent:needs-human-review`
   - remove stale `agent:peer-review` / `dispatch:paused`
   - add `dispatch:ready`
   - keep or set exactly one operational owner (`agent:agy`, `agent:jules`/`agent:codex`, `agent:fred`, etc.)
5. Run a live readback.
6. If automation/dispatch reattaches NHR or new NHR issues appear mid-cleanup, run a second classification/mutation pass against the current remaining NHR set.
7. Verify until the only remaining open NHR issues are true blockers with `dispatch:paused` and without `dispatch:ready`.
8. Write Markdown/CSV artifacts with counts, remaining blockers, and full processed rows.
9. Run a fresh `/tmp/hermes-verify-*` script that checks live Linear state, artifact row counts, and secret/token smoke.

## Verification contract

The cleanup is not done until a live verifier confirms:

- remaining open NHR count equals true blocker count;
- every remaining NHR issue is blocker-shaped and has `dispatch:paused`;
- no remaining NHR issue has `dispatch:ready`;
- every cleared target has no `agent:needs-human-review`, has `dispatch:ready`, and has some executable `agent:*` label;
- artifact row counts match the processed target set;
- report artifacts pass a token/secret smoke scan.

## Pitfalls

- Do not trust the first mutation pass. Dispatchers can immediately move routed issues to In Progress and reattach or retain stale NHR.
- Do not route real manual-send/recording/credential/approval blockers to agents.
- Do not let `agent:needs-human-review + dispatch:ready` remain on an issue: that is contradictory and keeps the queue noisy.
- Do not call the run clean from mutation results alone; read live Linear afterward.
- If the verifier itself fails due to a query/string/counter bug, fix the verifier and rerun rather than treating the failed verifier as product evidence.

# Event-gated artifact repair after producer overclaim

Session lesson from the DASHQA dashboard truth-proof sequence.

## Trigger

An event-admitted producer reaches a terminal `PASS`, but independent artifact review finds contradictions inside the producer's own evidence, such as:

- summary claims `0` non-2xx responses while raw browser proof contains 404s;
- unexplained aborted network requests;
- unsupported source classifications;
- incomplete rendered/mobile screenshots;
- worktree or cleanup overclaims.

## Durable pattern

1. Reject the producer `PASS` provisionally; do not treat the terminal exit code or `RESULT.md` as acceptance.
2. Preserve the exact terminal run artifacts unchanged. Clean only dead run anchors or undeclared markers after the harness/runtime proves the producer is terminal and process cleanup is complete.
3. Use independent exact-release/artifact review to classify the evidence. Do not admit a successor while review is active.
4. If the verdict is `BLOCKED` because the evidence packet is bad but no source defect is proven, freeze a separate **artifact-repair/reproduction** task. Keep it explicitly no-product-edit/no-source-change unless independent evidence later proves a product defect.
5. Before one-time admission, prove:
   - dependency verdict is final (`BLOCKED` for the prior run);
   - task contract hash matches the repository-local copy and agent-bus copy;
   - worktree is at the exact deployed release head/tree and clean;
   - event outbox has no selectable pending work;
   - writer leases are empty;
   - active slot and stale tmux anchor from the prior run are absent;
   - consumer/watchdog stay disabled/masked except for the single ordinary invocation.
6. Open only one bounded admission window: temporary policy/auth/launcher eligibility, one HTTP POST, one ordinary consumer invocation, then immediate restoration. No duplicate retry if wrapper assertions mismatch but DB proves `processed`/`completed` attempt `1`.
7. Update the durable handoff immediately after launch with event id, claim id, attempt, launch id, current run status, restored controls, and explicit no-retry/no-successor/no-merge/no-deploy boundaries.
8. Run a focused `/tmp/hermes-verify-*` ad-hoc verifier over the exact task/event binding, restored controls, clean worktree, cap containment, and handoff text. Label it ad-hoc, not suite green.

## Reporting boundary

While the repair producer runs, report only exceptions and authorization points. There is no authorization point until terminal completion plus independent review. If review proves a product defect, source repair must be a new frozen task with exact-head review; merge and deployment remain separately authorized.

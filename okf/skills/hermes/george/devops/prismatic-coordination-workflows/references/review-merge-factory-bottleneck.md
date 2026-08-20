# Review/Merge Factory bottleneck lesson

## Trigger

Use this when Michael asks whether Prismatic Engine review is too slow, whether George is the bottleneck, how to process many Ned/AGY candidates, or what infrastructure is missing between completed-work intake and merge-ready/deploy-ready decisions.

## Durable lesson

Do not defend manual George-centered review as the normal path. If George is hand-building candidate-specific prompts, verifier scripts, proof packets, and merge/deploy boundaries for ordinary candidates, the workflow has regressed into a serial bottleneck.

The scalable pattern is a durable, event-driven Review/Merge Factory:

```text
producer result packet
  -> completed-work row
  -> deterministic intake validation
  -> risk classification + policy-driven test plan
  -> immutable verification job + machine-readable receipt
  -> reviewer queue
  -> AGY/Jules exact-artifact review decision
  -> merge-ready queue
  -> explicit merge authorization + one-shot merge executor
  -> post-merge verification
```

Keep the cap on mutable writers/producers, not on read-only immutable reviewers. Initial reviewer concurrency can be greater than one when reviewers only consume immutable archives/receipts and cannot mutate, merge, deploy, write Linear, or admit successors.

## Coordination stance

When Michael expresses frustration that PE is stalled by verification:

1. Acknowledge directly if George is the bottleneck.
2. Separate safety standards from the slow implementation of those standards.
3. Propose infrastructure that removes George from the ordinary path rather than asking George to work faster.
4. Identify which existing PE pieces should be reused, especially completed-work intake, exact commit/tree/result binding, immutable archive reproduction, provider-neutral receipts, and event-driven dashboard projections.
5. Recommend class-level implementation slices, not another one-off review prompt.

## Suggested slices

- RF-1: review job queue/state machine wired exactly once from accepted completed-work rows; no worker/merge/deploy.
- RF-2: deterministic verification worker with immutable archive runner, risk/path policy, parallel safe checks, and durable receipts/log digests.
- RF-3: portable reviewer capability for AGY/Jules/George with exact-artifact decision schema and adversarial fixtures.
- RF-4: merge-ready policy and explicit merge executor; review completion never implies merge authorization.
- RF-5: existing canonical dashboard integration for queue age/depth, receipts, blockers, leases, reviewer utilization, and authorization states.
- RF-6: backlog importer that deduplicates by repository + candidate tree + task identity and routes under-bound candidates to needs-materialization rather than manual investigation.

## Pitfalls

- Do not create a new fallback dashboard for review throughput; attach to the existing canonical dashboard.
- Do not copy George's large accumulated coordination skill into every reviewer. Build a concise portable review capability pack.
- Do not require two expensive independent reviews for every ordinary candidate. Use risk tiers: deterministic-only/sample for low-risk docs/fixtures, one reviewer for ordinary source, two/specialist for sensitive authority paths, explicit George/policy authorization for production authority.
- Do not let a merge executor deploy or admit successors implicitly.
- Do not call GitHub CI, targeted proof, browser proof, production proof, merge, or canonical full-suite green by the wrong name.

## Reporting template

```text
STATUS=<PASS|PARTIAL|BLOCKED>
EVIDENCE=<existing infrastructure inspected; artifact/path if created>
BOUNDARY=<not claiming implementation/merge/deploy/canonical green unless proven>
NEXT_ACTION=<first infrastructure slice, usually RF-1>
```

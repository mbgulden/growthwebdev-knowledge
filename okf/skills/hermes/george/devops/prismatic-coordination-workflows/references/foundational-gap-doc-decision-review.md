# Foundational gap document decision review

Use this reference when Michael asks George to review a Fred/Ned/AGY planning document, answer questions at the end, and then ask for approval.

## Pattern

1. Preserve the submitted document as an artifact and hash it before analysis.
2. Separate three authorities:
   - the submitted document hash;
   - the last independently reviewed/approved plan hash;
   - current live source authority such as `origin/main`.
3. Check for stale citations and authority drift. A planning doc that references an older reviewed-plan hash or a non-advertised source commit can still be useful, but it is not itself write-authoritative until corrected or explicitly superseded.
4. Answer each requested decision explicitly (`APPROVE`, `HOLD`, `APPROVE AS POLICY ONLY`, etc.), rather than only summarizing the document.
5. For any held item, provide the corrected approvable version in the same decision packet.
6. Treat counts as approval-sensitive: distinguish “up to N candidate slices total” from an approved issue count, and state composition clearly (for example, `16 PE-parent candidates + 2 profile-hygiene packet candidates = up to 18 total`).
7. Keep read-only preparation separate from mutation authority. Linear writes, profile deletion, cron mutation, source implementation, login/auth changes, deploy/restart, and retention execution each require a later exact manifest and separate authorization unless Michael explicitly grants them. A writer cap is only a safety limit; it does not appoint the capped agent as an authorized mutator.
8. If a document claims Michael already approved decisions, cite external evidence or restate them as choices for Michael to confirm; do not let a source document self-authorize its own approval state.
9. After drafting the packet, run an ad-hoc consistency verifier that asserts source hashes, decision headings, boundary/non-claim text, and any corrected architecture markers.
10. Deliver a Telegram-downloadable Markdown packet plus a compact chat digest.

## Cron/offline wakeup authority pitfall

Do not approve a plan that claims opportunistic local wakeups guarantee timely scheduled execution while all devices/hosts are offline. Correct it to a one-runner durable authority model:

- semantic trigger kinds: `scheduled`, `catch_up`, `manual`, `external_event`;
- transports separate from authority: `system_cron`, `gateway_startup`, `webhook`, `push`, `operator_api`;
- immutable thin hook such as `pe-cron-trigger` submits idempotent trigger requests only;
- canonical gateway/runner owns eligibility, leases, receipts, and terminal success;
- dashboard/mobile wake may render state or submit authorized requests, but never decides schedule eligibility;
- trigger kind and transport are provenance only, not execution uniqueness. Use a deterministic uniqueness key such as `(cron_id, registry_generation, schedule_bucket, command_digest)` so different transports cannot execute the same bucket twice;
- shared durable authority needs transactional compare-and-set/unique claims, fenced runner lease, timezone/DST-aware bucket calculation, last-completed-sweep watermark, and durable missed/orphan/terminal receipts. Writer cap 1 alone does not prevent duplicate admission;
- catch-up defaults should be bounded per cron, usually `window=24h`, `mode=coalesce_latest`, `max_auto_executions_per_cron_per_recovery=1`, with older buckets recorded as missed;
- high-impact or non-idempotent catch-up should become `awaiting_operator_approval`;
- validate any proposed crontab/CLI examples against the current CLI before preserving them. Crontab `%` must be escaped or avoided, and if the current command only accepts positional `cron_id`, proposed `--trigger`, `--session`, or `--cron-id` flags are future contract work, not existing behavior;
- runtime admission must reject paused/deactivated jobs, not only deleted jobs.

## Approval request shape

End by asking for the smallest safe approval scope, for example:

```text
Approve bounded planning authority for decisions 1-4 plus corrected decision 5, and read-only Linear dedupe as the immediate next action. This does not authorize Linear writes, profile deletion, cron mutation, source implementation, auth/login, deploy/restart, or retention execution.
```

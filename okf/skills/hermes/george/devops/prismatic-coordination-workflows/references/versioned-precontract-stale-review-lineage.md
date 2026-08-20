# Versioned precontract stale-review and admission-ready lineage

Session-derived addendum for Prismatic coordination when asynchronous reviews return after newer contract versions already exist.

## Trigger

Use when an async review completes for a frozen contract/precontract artifact but the conversation has since produced newer V2/V3/V4 artifacts, repaired machine identity, or moved from contract review to envelope review.

## Rules

1. **Bind every review to exact artifact SHA/version before acting.** A `CLEAN/PASS` on V1 does not bless V2/V3/V4, even when the textual topic is the same.
2. **Treat valid stale findings as bounded blockers, not as broad rewrites.** Preserve the reviewed artifact as `BLOCKED/preserved`, then create the next immutable version with the minimum correction.
3. **Repair machine-readable identity separately from substantive contract text.** If title/header says V3 but marker or `CONTRACT_VERSION` says V2, create V4 with only version identity/marker repairs when possible.
4. **Keep version lineage explicit in handoff.** Include V1/V2/V3 states, review IDs, exact SHA prefixes, and which version is current. Avoid duplicate keys; if bookkeeping patches corrupt historical lines, restore the complete lineage block before continuing.
5. **Contract `CLEAN/PASS` is not admission-ready.** Admission readiness also requires exact task copies/envelope coordinates, branch/worktree identity, zero-event/readiness proof, and independent envelope review.
6. **Zero-event boundary stays live until explicit admission authorization.** Creating a task copy or reviewing an envelope is not permission to POST or launch a producer.
7. **Do not reuse dirty or orchestration-artifact worktrees for production task envelopes.** Create the contract-declared clean branch/worktree at the exact base/tree and copy frozen bytes verbatim.

## Minimal proof packet

```text
ARTIFACT=<contract/precontract/envelope>
VERSION=<Vn>
SHA256=<exact>
REVIEW=<deleg_id:PASS|BLOCKED>
LINEAGE=<V1 state; V2 state; V3 state; current Vn>
ZERO_EVENTS=<PASS|FAIL>
TASK_COPY=<not created|sha/path>
ENVELOPE_REVIEW=<pending|deleg_id:PASS|BLOCKED>
ADMISSION_STATE=<not-ready|admission-ready-awaiting-explicit-authorization>
NOT_CLAIMING=<event posted, producer launched, upstream issue complete, public proof>
```

## Pitfalls

- A stale `CLEAN/PASS` is still useful historical evidence, but it must not be promoted across artifact hashes.
- A reviewer-proposed replacement can itself become stale before it is acted on; rebase the *finding*, not the exact proposed text, onto current lineage.
- Handoff patching can introduce duplicate version keys or delete historical detail. Verify uniqueness of review keys and restore the full lineage before reporting.

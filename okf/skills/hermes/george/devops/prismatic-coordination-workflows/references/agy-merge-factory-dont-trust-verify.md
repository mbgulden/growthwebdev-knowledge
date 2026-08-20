# AGY Merge Factory — Don't Trust, Verify Review Gate

Session-derived pattern for graduating AGY producer concurrency and reviewing AGY candidates before merge workflow integration.

## Governing principle

Treat every producer artifact as an untrusted input until George independently verifies it against the exact candidate commit and retained artifacts:

- `RESULT.md` is a claim, not proof.
- Self-review is advisory, not merge authorization.
- Passing producer test output must be reproduced or independently inspected.
- Logs/screenshots/manifests must bind to the exact commit/artifact digest.
- Any post-verification code change invalidates prior approval.
- Missing, mutable, stale, producer-only, or revision-mismatched evidence fails closed.

## Graduated concurrency workflow

1. Keep generic AGY backlog dispatch paused while testing the merge factory; exact-ID launches are the only allowed producer wakes.
2. Start with one exact issue ID and `--max-concurrent 1`. Maintain only one active producer/repair for that ID.
3. Do not queue the next issue merely because the AGY process says `DONE`; first inspect candidate commit, changed paths, `RESULT.md`, provenance, test claims, and security-sensitive paths.
4. If legacy automation or self-review prematurely moves Linear to Done or restores `dispatch:ready`, revoke that state before review. Producer completion is not merge completion.
5. If independent review finds blockers, keep the same issue active and issue a focused repair prompt. Do not advance to the next payload.
6. Only after a clean George merge-judge packet, current-main port, PR head verification, CI, merge, and post-merge source/package proof may the sequencer move to the next issue.
7. Promote to cap 2 only after at least three consecutive single-task merge-complete successes plus stale-recovery and rollback drills.
8. Promote to cap 3 only after at least three clean cap-2 waves, exact lease/path-overlap proof, serialized George merge locks, and recovery proof.

## Bounded controller pattern

For a multi-hour merge-factory run, prefer a finite attached controller over a forever sequencer:

- Schedule a bounded cron job with a fixed repeat count and `attach_to_session=true` so Michael can reply in the same lane.
- Each tick must read actual processes, Linear labels/status, source/result files, repo state, GitHub PR/check state, and a durable control-state/handoff file before taking action.
- If an exact approved producer process is active, do not launch another. Report only material changes, or a single compact `NO_CHANGE` line.
- On `REPAIR`, preserve the exact failed source under a unique archive path, write a durable George review, update the same issue with a narrow prompt, and launch at most one same-issue repair per tick.
- On `PASS`, port minimum paths to a clean current-main worktree rather than merging stale sandbox lineage; re-run revision-bound proof before PR/merge.
- Never let the controller schedule more cron jobs, resume generic `--from-linear`, deploy/restart production, or launch the next issue until merge-complete verification exists.

## AGY admission/lease/security candidate review checklist

For merge-factory/admission-control candidates, independently verify these classes before merge or promotion:

- Real simultaneous contention tests using independent SQLite connections/processes/threads, not sequential acquisition loops.
- Cap 1 proves exactly one winner from three contenders; cap 2 proves exactly two winners and one denial.
- Lease heartbeat/release are fenced by exact current `lease_id` or equivalent monotonic generation.
- `acquire_lease()` or equivalent acquisition must not renew/mutate an existing active lease merely because `issue_id` and principal match. Re-acquisition/renewal must fail closed or require the exact current lease token.
- Stale holders cannot heartbeat/release a replacement lease held by the same principal after expiry/reacquisition; also test that stale same-principal actors cannot mutate lease B through the acquire path.
- Release/heartbeat check affected rows and fail closed on wrong owner or wrong lease ID.
- Stage cap is read inside the same exclusive transaction that prunes/counts/inserts leases.
- Cap-change/acquire races cannot oversubscribe the committed cap.
- Cohort replay is idempotent and preserves original timestamps; destructive restaging/reset while actively leased is rejected.
- External credential mappings parse strictly and fail closed on malformed entries, duplicates, empty identity/scope, unknown/empty scopes, and weak/short keys.
- Credential scanner findings never include matched values or source-line contents; high-confidence seeded findings exit nonzero and omit the synthetic value from stdout, stderr, and retained logs.
- High-confidence credential scanners must not suppress findings because values contain words such as `env`, `config`, `test`, `mock`, `dummy`, or `example`; add parametrized bypass-word tests and keep raw synthetic values out of all outputs.
- Scanner/source comments must not retain raw known default credential strings. Keep only generic rule IDs and digests.
- Generated scan logs are not committed mutable evidence; retain logs outside Git and bind SHA-256 in the result packet.
- Evidence log paths and content should self-identify the exact reviewed candidate and parent. A parent-named log or candidate-agnostic content is not enough for final approval.

## Repair prompt shape

When a candidate fails independent review, send a same-issue repair prompt with:

```text
START_FROM=<candidate sha>
WORKDIR=<retained exact-source sandbox>
DECISION=REPAIR
MAX_CONCURRENT=1
DO_NOT_ADVANCE_NEXT_ISSUE=true
DO_NOT_MERGE_DEPLOY_RESTART=true
REQUIRED_PROOF=<adversarial checks and log digests>
MARKER=<issue-specific marker>
```

Retain the failed source snapshot separately before repair so future review can compare producer claims to the exact inspected candidate.

## Proof packet fields

```text
COMMAND=<commit/diff review; exact tests/probes reproduced or inspected>
RESULT=<PASS|FAIL|REPAIR|BLOCKED>
LOG=<external immutable log path + sha256 when applicable>
SCOPE=<issue/candidate sha/components reviewed>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|GitHub CI|canonical suite>
NOT_CLAIMING=<merge approval, CI, deploy, production proof, next-stage promotion unless separately proven>
MARKER=<AGY merge-factory marker>
```

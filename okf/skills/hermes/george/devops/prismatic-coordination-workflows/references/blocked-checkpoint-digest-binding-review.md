# Blocked checkpoint: digest-binding review and repair prompt pattern

Use this when an assigned-agent candidate passes local tests but an independent exact-head review finds that the tests validate a detached helper or shape check rather than the production/classifier path required by the contract.

## Trigger

- Candidate has exact commit/tree and local archive reproduction proof.
- Independent review returns a precise `BLOCKED` finding that a required binding is not tested on the actual classification/generation path.
- Example class: digest proof tests a local SHA-256 helper against arbitrary sample bytes while the export classifier never parses/recomputes/compares `release_digest` / `config_digest` against canonical manifest/config bytes.

## Required response pattern

1. **Accept as potentially valid, then reproduce read-only.** Inspect the exact candidate bytes at the reported lines and the relevant contract clauses. Do not repair first.
2. **Preserve the candidate as a BLOCKED checkpoint.** Record exact commit/tree and the first precise blocker. Do not amend, reset, or rewrite that checkpoint.
3. **Separate local reproduction from acceptance.** Local suite green and archive reproduction can remain true while exact-head review is `BLOCKED`.
4. **Update handoff immediately.** Mark status as blocked, record reviewer handle, finding, reproduced=true, repair_launched=false, and non-claims.
5. **Freeze a bounded repair prompt instead of self-launching.** The prompt should specify allowed path families, forbidden mutations, exact blocked base, required semantic repair, verification commands, and completion packet. It is not authorization by itself.
6. **Prove no successor launch.** Use an ad-hoc detector for no pending/selectable events, no writer leases, no active slots, and stable worktree status.

## Repair-prompt requirements for digest-binding gaps

The repair should require the actual classifier/generator path under test to:

- parse lowercase 64-hex binding fields;
- recompute SHA-256 from exact canonical manifest/config bytes;
- compare recomputed bytes to parsed bindings;
- bind full manifest merge commit to the full release-directory component;
- reject malformed, uppercase, wrong-length, placeholder, alias/short-SHA, missing-byte, and mismatch cases;
- include a fixture that would have passed the old shape-only/helper test but fails after recomputation;
- keep zero admitted production lines when the real hook/manifest/config pair remains absent;
- avoid implementing unrelated production hooks, installers, runtime classifiers, or deployment behavior if the task is test/fixture-only.

## Proof packet shape

```text
COMMAND=<exact read-only reproduction + post-edit detector>
RESULT=PASS
STATE=EXACT_HEAD_REVIEW_BLOCKED
CHECKPOINT=<sha>
TREE=<tree>
FINDING_REPRODUCED=true
REPAIR_PROMPT=<path>
REPAIR_PROMPT_SHA256=<sha256>
REPAIR_EVENT_COUNT=0
ACTIVE_SLOT_COUNT=0
SELECTABLE_EVENTS=0
WRITER_LEASES=0
TRACKED_STATUS_CLEAN=true
AD_HOC_OR_CANONICAL=ad-hoc targeted blocked-checkpoint detector
NOT_CLAIMING=repair authorization, repair launch, candidate acceptance, PR, merge, deployment, Linear write, cron/timer mutation, or canonical full-suite green
MARKER=<BLOCKED_MARKER>
```

## Pitfalls

- Do not let a local helper test satisfy a contract that requires the actual classifier/generator path to bind bytes.
- Do not treat `CLEAN` local reproduction as overriding a semantic review blocker.
- Do not mutate or relaunch from a blocked checkpoint without a new finite authorization.
- Do not record the repair prompt as if it were an admitted task; freeze and hash it as a proposed next gate only.

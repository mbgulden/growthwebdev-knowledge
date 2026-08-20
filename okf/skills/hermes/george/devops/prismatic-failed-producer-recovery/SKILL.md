---
name: prismatic-failed-producer-recovery
description: Preserve failed-producer truth while reviewing exact candidates and freezing bounded recovery contracts before any second Prismatic event or producer.
---

# Prismatic Failed-Producer Recovery

Use this skill when an admitted Prismatic producer exits, is terminated, or overclaims, but leaves a candidate branch/worktree/artifact that might be salvageable.

This skill exists because producer completion, candidate review, and recovery admission are separate gates. Do not collapse them.

## Trigger conditions

Load this skill when any of these appear:

- `producer_completed=false`, harness `failed` / `failed/review_pending`, signal/exit ambiguity, or passive wait completion;
- a producer `RESULT` claims tests pass but independent reproduction disagrees;
- an exact candidate HEAD/tree needs independent review after a failed or terminated producer;
- a blocked candidate needs a same-worktree recovery contract before further source mutation;
- a producer exits without a committed candidate/`RESULT.md` but leaves dirty checkpoint bytes that must be preserved and freshly reproduced;
- dirty-checkpoint integrity passes but implementation review blocks on migration ordering, old-schema compatibility, foreign-key pragma timing, or missing true prior-version fixtures;
- a future repair task/event identity is being reserved but not yet authorized.

## Core rules

1. **Producer truth stays terminal**
   - Preserve exact run id, event id, exit code, deadline/automatic-kill flags, cleanup/survivor proof, active-slot state, and `producer_completed=false`.
   - A passing focused test, candidate artifact, or review result never converts a failed producer into producer success.

2. **Do not replay the original admission**
   - No repost, consumer rerun, cap increase, second event, second producer, PR, merge, deploy, cron/timer, production DB, or Linear mutation unless Michael explicitly authorizes that exact next gate.

3. **Review the candidate independently**
   - Freeze exact `HEAD`, tree, parent/base, tracked cleanliness, changed paths, and archive digest.
   - Reproduce from `git archive` in a disposable directory, not the mutable worktree.
   - Run focused tests, compile, `git diff --check`, lint, format, static no-spawn checks, and task-specific authority invariants.
   - Canonical-suite green is separate from ad-hoc/focused green. If full suite fails, classify repaired-head regressions vs baseline only after reproducing the baseline under the same command/environment.

4. **If candidate is blocked, freeze a repair contract before source mutation**
   - Base it on the exact blocked `HEAD`/tree.
   - Require normal descendant commits only: no reset, rebase, amend, clean, stash, force-update, or worktree replacement.
   - Preserve existing untracked operational files unless the contract explicitly says otherwise.
   - Include a tracked path allowlist and a `BLOCKED_OUT_OF_SCOPE` rule.
   - Enumerate each independent-review blocker as a required repair, not broad advice.
   - Include required verification commands, invariance checks, and hard non-claims.

4a. **If there is no committed candidate/result, freeze a dirty-checkpoint artifact first**
   - Do not promote an interrupted dirty worktree to candidate status.
   - Reconcile receipt/ledger terminal truth, then preserve HEAD/tree, commits-from-base, tracked diff hash, new module hashes, checkpoint patch hash, and allowed paths.
   - Distinguish timeout sources: if `runtime_deadline=null` but stderr shows a CLI/producer wait timeout (for example `timeout waiting for response`), record it as producer/CLI terminal failure, not an admission-runtime deadline. Still do not retry automatically.
   - Reproduce from exact base in a `.git`-free disposable directory by applying only the current tracked diff and copying any new/untracked implementation module bytes; prove byte equality before running tests.
   - If compile/focused tests pass but lint, format, authority invariants, or canonical scope fail, classify as `BLOCKED_TERMINAL_FAILED_DIRTY_CHECKPOINT`, not repair-ready.
   - If the checkpoint canonical suite fails, run the exact base under the same interpreter/command and compare failed node IDs. Identical baseline-only canonical failures can support dirty-byte viability review, but they are still not canonical green and never promote the checkpoint to candidate.
   - Historical recovery-ready reviews become stale when a fresh terminal checkpoint is requested; update the handoff to the new checkpoint-review gate before any recovery event.

4b. **If a failed producer leaves both a `RESULT.md` and dirty bytes, audit the result as an overclaim candidate**
   - Terminal/harness truth remains controlling: `producer_completed=false`, failed/review-pending state, exit signal/code, cancellation/deadline flags, process cleanup, and active-slot count.
   - A `RESULT.md` that claims success is rejected when HEAD did not advance, descendant commit count is zero, tracked files are dirty, or its commands did not cover uncommitted work.
   - Preserve the exact dirty patch/blobs and reproduce in a `.git`-free archive. If the first verifier attempt fails from setup (missing executable, invalid diff command), record it as setup-only and rerun the whole sequence with established product bindings.
   - Compare canonical failures to the immutable baseline. If dirty bytes add a repair-surface failure, classify `BLOCKED_DIRTY_CHECKPOINT_REPAIR_SPECIFIC_REGRESSION`, freeze a no-authority checkpoint manifest, and dispatch read-only triage for minimum repair scope only.

5. **Review the repair contract as an artifact**
   - Verify SHA-256, line count, byte count, and exact marker.
   - Prove it does not create a task file, event, credential window, producer, or source mutation.
   - Dispatch fresh independent artifact review for sufficiency, finite scope, fail-closed behavior, and coverage of every blocker.
   - If review blocks version `Vn`, preserve that artifact byte-for-byte, record the first precise blocker, and create a new frozen `Vn+1` artifact. Do not silently edit the reviewed file or overwrite the old hash.
   - For authority/security contracts, require concrete named trust roots: source id, storage object, schema id/version, canonical encoding, digest domain, immutable retrieval/install interfaces, provenance/authentication boundary, and equality checks at every decision/finalization boundary. Reject vague phrases like “trusted authority” unless the artifact defines what object is trusted and how it is pinned.
   - Keep schema identity and digest-domain identity distinct. If code/accepted prior contract uses `SCHEMA_ID=prismatic.cron.registry-snapshot` and `DIGEST_DOMAIN=prismatic.cron.registry-snapshot.v1`, do not copy the `.v1` suffix into `schema_id`. Verify both against source constants and accepted artifacts before freezing.
   - When review blocks `Vn` on a first precise defect, `Vn+1` may carry the minimum correction, but the next reviewer must perform a fresh full review of the whole artifact. Do not treat the unreviewed tail of `Vn` as implicitly accepted.

6. **Reserve identities, don’t launch**
   - A future repair `TASK_ID` may be reserved in the contract, but reservation is not authorization.
   - Only after contract `CLEAN/PASS` should task-file copies and deployed-schema admission envelope be prepared for their own review.
   - Copied task files must be byte-identical to the reviewed repair contract and bound to the same blocked base HEAD/tree.
   - The deployed admission envelope is its own artifact/review gate. Freeze all authority-bearing fields and validate it with the actual deployed parser/validator against disposable storage before any live POST.
   - If the repaired worktree is no longer allowlisted because production policy was restored after the original launch, validate schema/Git/task-hash admissibility with a disposable mode-600 policy that narrows only `producer` and `worktree`; prove production policy hash unchanged before/after and do **not** claim live admission authorization from that disposable validation.
   - Internal repair task IDs may differ from the Linear issue ID when the gateway schema needs a fresh event identity; label them explicitly as `internal_repair_event_identity`, bind the real Linear issue separately, and prove original event count remains unchanged plus repair event count is zero.
   - If deployed admission freshness makes `created_at` time-sensitive, make `created_at` the only late-bound field; keep idempotency stable, rerun full zero-mutation preflight after substituting it, and regenerate only `created_at` if the freshness window expires.
   - Stop again for explicit one-event/cap-1 recovery authorization.

7. **Treat one-shot launchers as their own executable artifact gate**
   - A contract/envelope `CLEAN/PASS` is not launcher acceptance. Freeze the exact launcher script, hash it, and review it before any live POST/consumer/producer action.
   - Review executable control flow, not only payload fields: live zero-state checks must happen before credentials/policy/window/POST; `prepare()` and restoration must be inside the protected `try/finally`; cleanup paths must be owned by `finally` even when preparation fails halfway.
   - Use disposable or monkeypatched-path lifecycle tests for partial-prepare failure, preflight-only success, restoration, cleanup, and report-name uniqueness. Do not mutate live policy/control/DB while proving those paths.
   - If a delegated review ignores the exact artifact or returns unrelated handoff/foundational text, classify it as invalid non-acceptance and rerun a fresh exact-artifact review; do not treat silence or generic text as acceptance.

## Minimum proof packet

```text
COMMAND=<terminal reconciliation / candidate review / repair-contract freeze>
RESULT=<BLOCKED|PARTIAL_REPAIR_CONTRACT_REVIEW_PENDING|PASS>
LOG=<path>
SCOPE=<exact producer/candidate/contract>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
PRODUCER_COMPLETED=false
ORIGINAL_EVENT_COUNT=<n>
BLOCKED_HEAD=<sha>
BLOCKED_TREE=<tree>
CANDIDATE_REVIEW=<delegation>:<verdict>
REPAIR_CONTRACT=<path>
REPAIR_CONTRACT_SHA256=<sha256>
FUTURE_EVENT_COUNT=0
SECOND_EVENT=false
SECOND_PRODUCER=false
NOT_CLAIMING=<producer success, candidate acceptance, canonical green, PR, merge, deploy, cron/timer, DB, Linear>
MARKER=<stable marker>
```

## Common pitfalls

- **Producer RESULT overclaim**: Treat a RESULT file as evidence to audit, not as producer success. If the producer failed, HEAD did not advance, tracked bytes are dirty, or the result's commands exclude uncommitted changes, reject its success claim and preserve a no-authority checkpoint before triage.
- **Focused-test tunnel vision**: lint/format and authority invariants can block even when focused tests pass.
- **Candidate acceptance drift**: exact-head review can be CLEAN/PASS while producer remains failed; keep both facts visible.
- **Mutable-worktree proof**: archive reproduction is required for candidate review; worktree state is only provenance/cleanliness evidence.
- **Dirty checkpoint promotion**: zero commits from base plus dirty bytes is not a candidate, even if compile/focused tests pass. Freeze a blocked checkpoint artifact and fresh review first; do not jump straight to recovery admission.
- **Verifier setup vs product result**: Missing executable bindings or invalid verifier command shape do not prove product failure. Record the failed attempt as setup-only, find the established product interpreter/tool bindings, and rerun the entire acceptance sequence from the beginning before classifying the checkpoint.
- **Recovery shortcut**: do not create a repair task file or event from a repair contract alone. Contract `CLEAN/PASS` permits copied-task/envelope preparation only; event admission remains a separate explicit authorization.
- **Subset convergence bug**: if a finalizer declares convergence by comparing only a small receipt tuple, review persisted semantic fields adversarially. Require unchanged-state, collision, altered immutable-field, and supplied-evidence-mismatch tests before accepting convergence repair. See `references/internal-repair-event-zero-state-gate.md`.
- **Disposable policy overclaim**: a disposable policy that temporarily allows a repaired worktree proves parser/schema/Git/task-hash compatibility only. It does not authorize a live event, does not prove production policy was widened, and must be paired with before/after production policy hash equality plus zero repair event/slot/lease proof.
- **Envelope freshness drift**: deployed admission windows can make `created_at` expire. Do not freeze a stale timestamp as permanent truth; freeze a template, late-bind only `created_at`, and rerun deployed zero-mutation preflight before POST.
- **Policy/schema overclaim**: distinguish what deployed policy actually narrows from what deployed schema/task binding validates. Do not invent policy keys for task ID or writer cap when the release only loads producer/worktree policy.
- **In-place artifact drift**: when an independent review blocks a frozen contract, the reviewed version remains evidence. Create `Vn+1` with a new hash and proof packet; never mutate `Vn` and keep calling it the same artifact.
- **Abstract authority language**: “trusted registry authority” is not enough. Security/authority repairs must identify the trusted object, schema, canonical bytes, digest domain, retrieval/install path, local provenance boundary, and exact equality checks.
- **Operator-exception acceptance drift**: an exact-byte operator commit exception turns reviewed dirty bytes into a clean candidate; it does not accept the candidate. Fresh exact-head review can still block on candidate-specific trust-boundary defects even when focused tests pass and canonical failures match baseline. Preserve the blocked commit, freeze a new versioned repair contract, prove future event count is zero, and stop for fresh artifact review.
- **Path-only blocker binding**: compatibility-deadlock/operator-exception artifacts must bind blocker identity by exact SHA-256 plus accepted review id/verdict before staging. A pathname-only blocker reference is mutable and should be blocked; preserve `Vn`, create `Vn+1`, and require a fresh full review of the new artifact before asking Michael for explicit one-commit authorization.
- **Migration integrity/technical split**: checkpoint integrity can be `CLEAN/PASS` while implementation safety is `BLOCKED`. If migration validates an old DB against new DDL before rebuild, lacks a true populated prior-version fixture, toggles SQLite `foreign_keys` after `BEGIN`, or has ambiguous BEGIN/COMMIT/ROLLBACK exception ownership, freeze that as a technical blocker and require a versioned repair contract; do not relaunch or treat focused green as migration acceptance. See `references/migration-prevalidation-blockers.md` for the transaction-lifecycle checklist.
- **SQLite FK readback uncertainty**: after issuing `PRAGMA foreign_keys = OFF`, treat the caller connection as unsafe until readback proves the intended state, and fail closed if disable or restore readback fails/lies. Mark unsafe immediately after the real `OFF`; on failed disable readback, close/invalidate before raising a stable bounded error. On restore readback failure after rollback, preserve the primary migration cause and close/invalidate; tests should prove actual OFF/ON calls, exactly one post-OFF readback/restoration attempt, no retry, and subsequent-use failure. See `references/sqlite-fk-readback-fail-closed.md`.
- **Post-commit FK restore failure is its own terminal branch**: if migration `COMMIT` succeeds but FK restoration/readback then fails or lies, do not let the general rollback/recovery handler retry `ON`, perform extra readbacks, or rewrap as a migration/rollback failure. Add a dedicated post-commit sentinel, close/invalidate the caller, raise stable `foreign_keys_restore_failed`, preserve the direct cause for exception cases, and test both non-enabled readback and readback-exception paths. Count any baseline pre-migration `ON` separately from the single post-`OFF` restoration attempt. See `references/sqlite-postcommit-fk-restore-fail-closed.md`.
- **Circular prior-schema fixtures**: a “true v2”/prior-version migration fixture that imports runtime-private DDL constants or runtime helper functions is not independent evidence. Preserve the blocked candidate, create `Vn+1`, embed the full prior-schema object set as test-local SQL literals with a fixed digest, assert no `_CREATE_*`/trigger/helper names remain in the fixture body, and rerun focused plus base-comparison proof before fresh full review. See `references/non-circular-migration-fixtures.md`.
- **Exact-byte checkpoint verifier drift**: when dirty bytes are explicitly authorized as one checkpoint commit, exact blob hashes outrank a first patch-hash mismatch until the diff command shape is confirmed. A frozen `git diff --binary --full-index` hash will not match an abbreviated diff serialization even when resulting blobs are identical. After commit, reproduce from a `.git`-free archive and, if dependencies changed, verify in a fresh venv installed from the archive rather than an older production venv. Compare canonical boundaries by exact base-vs-checkpoint error node IDs under the same interpreter, not by pass-count folklore.
- **Blocked exact-head proof-only follow-up**: when a permitted one-commit/operator-exception candidate is later blocked by exact-head review for insufficient tests or proof coverage, preserve that commit as immutable evidence. Do not amend/reset/rebase to fold in the missing proof. Freeze a new versioned contract for exactly one additive normal descendant commit, normally test-only, bind runtime source unchanged by SHA, compare broad-suite failures against the immutable base, and require fresh exact-head review before public/operational side effects. See `references/additive-descendant-proof-followup.md`.
- **Downstream Linear projection boundary drift**: when Michael authorizes a next slice such as cron Linear projection after a repair goes live, split build/test/review/merge/deploy authority from live Linear mutation authority. Unless explicitly granted, record `LIVE_LINEAR_COMMENTS_AUTHORIZED=false`, `LIVE_LINEAR_LABELS_AUTHORIZED=false`, and `LIVE_OUTCOME_PROJECTION_WRITES_AUTHORIZED=false`; prove projection idempotence with fake/disposable adapters first.
- **Permissive locator authority**: for trust-boundary repair contracts, wording like `accept or derive`, `locator/assertion`, or `caller content cannot override` is too weak. Specify the exact accepted locator fields, reject all caller-supplied snapshot/content/evidence/path/alias/helper authority at the API boundary, forbid deriving locator values from caller snapshot content, and require adversarial tests for those rejected inputs.
- **Schema/digest identity drift**: `.v1` can be correct in a digest domain while wrong in `schema_id`. Bind `schema_id`, schema version, and digest domain separately to source constants and accepted artifacts; a contract that conflates them should be blocked and revised as a new immutable version.
- **False-zero durable receipts**: after a claim exists, do not require zero adapter/spawn counts for every fail-closed outcome. Pre-invocation failures should prove zero counts; failures first detected after adapter invocation or during finalization must persist the actual counts plus claim/fence/phase/reason identity. A contract that forces zero counts after possible invocation should be blocked and revised as a new immutable version.
- **Minimum-correction tunnel vision**: after a reviewer returns the first artifact defect, fix only that defect in `Vn+1`, but require the next fresh review to re-check the entire contract. The first reviewer’s early stop is not acceptance of the remaining sections.
- **Launcher-interface drift**: after moving preparation/finalization logic, re-check function signatures, return values, unpack sites, and exception ownership. A script can pass static payload checks but still fail immediately if `prepare()` returns a different shape than `run()` expects.
- **Partial-prepare cleanup gap**: cleanup variables assigned inside `prepare()` are unavailable if `prepare()` raises early. Precompute report/window/policy/private/outer paths and original bytes before entering `try`, then pass them into `prepare()` so `finally` can clean and restore after partial failures.
- **Timestamp collision in proof runs**: second-resolution report directories can collide during back-to-back preflight/failure-injection tests. Use microsecond-resolution or another deterministic uniqueness component for one-shot launcher report directories.
- **Invalid delegated review as false gate-open**: if a delegated review does not inspect the named artifact/hash or returns unrelated project guidance, mark it `INVALID_NOT_A_REVIEW`, preserve that fact, and rerun exact read-only review. For high-risk launchers, use two targeted reviewers: one full artifact review and one focused control-flow/finalization review.

## Support references

- `references/failed-producer-recovery-contracts.md` — detailed session-derived pattern for candidate review, repair-contract freeze, iterative exact-artifact repair, and proof fields.
- `references/authority-contract-trust-roots.md` — checklist for making registry/authority repair contracts concrete instead of abstract.
- `references/deployed-recovery-admission-envelopes.md` — copied-task and deployed-schema envelope gate after contract CLEAN/PASS, including late-bound `created_at`, zero-mutation preflight, and policy/schema boundary handling.
- `references/dirty-checkpoint-terminal-reconciliation.md` — procedure for failed producers with no commit/RESULT but preserved dirty bytes: terminal receipt reconciliation, exact-base materialization, blocked-checkpoint artifact, and stale recovery-gate reset.
- `references/dirty-checkpoint-result-overclaim-regression.md` — procedure for failed producers with a success-claiming `RESULT.md` plus dirty bytes: reject overclaim, rerun correctly bound fresh-archive verification, compare baseline failures, and freeze a no-authority regression checkpoint.
- `references/operator-exception-dirty-recovery.md` — when deployed admission rejects an otherwise reviewed dirty same-worktree recovery, use an explicit human-authorized exact-byte operator commit exception: commit only reviewed bytes, reproduce exact head, dispatch fresh review, and stop before public/operational side effects.
- `references/operator-exception-candidate-trust-boundary-block.md` — when that exact-byte operator-exception candidate is later blocked by fresh exact-head review, preserve the commit and freeze a new contract for the specific authority/trust-boundary defect instead of treating the exception/focused green as acceptance.
- `references/repair-d-authority-checkpoint-contracts.md` — failed-producer dirty-checkpoint authority recovery pattern: descriptor-relative traversal, pinned adapter consumption, claim-bound canonical identities, schema-ID/digest-domain separation, and full-review iteration after first-defect corrections.
- `references/recovery-one-shot-launcher-gate.md` — executable launcher gate after envelope CLEAN/PASS: exact-script hash review, failure-injection cleanup tests, invalid-review classification, report uniqueness, and hard non-claims before live POST/consumer/producer.
- `references/terminal-timeout-dirty-checkpoint-baseline-comparison.md` — dirty-checkpoint pattern for producer/CLI timeout with `runtime_deadline=null`: freeze patch/manifest, reproduce from exact base, compare canonical failures against baseline, and dispatch read-only reviews before any recovery contract.
- `references/migration-prevalidation-blockers.md` — how to classify dirty-checkpoint implementation reviews that block on old-schema migration pre-validation, SQLite foreign-key pragma timing, or missing true prior-version fixtures while integrity proof remains clean.
- `references/sqlite-fk-readback-fail-closed.md` — concrete SQLite migration rule for fail-closing after FK disable/restore readback uncertainty and adversarial tests that prove no unsafe connection returns to callers.
- `references/sqlite-postcommit-fk-restore-fail-closed.md` — post-commit FK restoration/readback failure pattern: dedicated sentinel, caller invalidation, no retry/rewrap through general recovery, and adversarial nonzero/exception tests.
- `references/non-circular-migration-fixtures.md` — repair pattern for migration tests whose prior-version fixture imports runtime-private DDL: freeze complete test-local SQL literals, bind with a digest, assert no runtime DDL/helper references, and rerun focused plus base-comparison proof before fresh review.
- `references/exact-byte-checkpoint-archive-env.md` — exact-byte operator checkpoint verification pattern: confirm full-index diff serialization before rejecting patch hashes, commit only frozen bytes, reproduce from a Git-free archive, install changed dependencies into a fresh venv, and compare canonical base/checkpoint node IDs under the same interpreter.
- `references/additive-descendant-proof-followup.md` — when exact-head review blocks an already-authorized one-commit candidate for proof undercoverage, preserve the blocked commit and freeze a test-only additive descendant contract instead of amending/resetting; includes complete frozen migration-oracle escalation when tests prove stability but not conformance.
- `references/cron-status-repair-to-linear-projection-boundary.md` — standing authorization pattern for finishing a cron-status repair before downstream Linear projection work, including explicit no-live-comments/no-live-labels/no-live-projection-writes gates.
- `references/internal-repair-event-zero-state-gate.md` — blocked exact-head candidate pattern for freezing a same-worktree repair task under an internal event identity, validating deployed schema with disposable narrow policy, proving production policy unchanged and zero repair event/slot/lease, and stopping before one-event authorization. Pair with `prismatic-admission-control-gates/references/bootstrap-safe-repair-admission-envelopes.md` when turning the clean repair task into a one-shot envelope/launcher.

## Verification before reporting

Before final status, prove:

- original event count unchanged;
- future repair event count is zero;
- no future task file exists unless explicitly authorized;
- blocked candidate HEAD/tree unchanged and tracked-clean;
- repair artifact hash/lines/bytes match;
- handoff records pending review and non-claims.

# Provider-Neutral Verification — Review/Repair Lessons

Use this reference when a provider-neutral verification governance/schema slice receives independent review feedback or a producer encodes the wrong source/backend taxonomy.

## Core lesson

Keep two axes separate everywhere: docs, schemas, receipts, tests, Linear prompts, queue state, handoffs, and skill references.

| Axis | Meaning | Example classes |
|---|---|---|
| Source acquisition | How source material is obtained for verification | `provider_remote`, `local_bare_repository`, `offline_git_bundle` |
| Verifier execution backend | Where/how the verifier actually runs | `hosted_provider_runner`, `self_hosted_clean_room`, `supervised_clean_room` |

A local bare repository or offline Git bundle is source input. It is not a clean-room verifier backend and is not merge authority by itself.

## Review response protocol

1. Treat independent `REPAIR` as authoritative until disproven by exact-head reproduction.
2. Reproduce each finding directly on the exact reviewed head before editing.
3. If the architecture contract is wrong, stop or contain any active producer using that contract before it encodes the defect.
4. Preserve rejected producer candidates under a durable local ref/bundle before repair.
5. Repair the same task/PR head; do not skip to the next child issue.
6. Add validator-owned enforcement, not only prose. For OKF docs, enforce JSON Schema plus exact objective/system-of-record parity.
7. Scan authoritative prose for taxonomy ambiguity after schema repair. Accepted ADRs, documentation policy, and verification contracts must not contain slash forms such as `adapter/backend` or `adapters/backends`; those phrases can preserve the old conflation even when fixtures pass.
8. Ensure receipts bind both axes with minimum fields such as `source_kind` and `backend_class`; a receipt that identifies only provider/source information can accidentally treat acquisition as authority.
9. Add adversarial fixtures that prove one axis cannot substitute for the other.
10. After any repair commit, previous review/CI proof is stale. Dispatch a fresh exact-head independent review and hold merge/push/PR actions until it returns clean.

## Candidate lifecycle state

When a producer completes and the candidate awaits review:

```text
ACTIVE_PRODUCERS=0
ACTIVE_STATE=EXACT_HEAD_REVIEW_PENDING
WATCHER=<job> PAUSED
CANDIDATE_HEAD=<sha>
CANDIDATE_TREE=<tree>
REVIEW=<delegation id> pending
DOWNSTREAM=PAUSED
```

Do not keep a completed candidate watcher running as if work is still active. Pause or retarget it, refresh queue/control/handoff digests, and state that downstream remains paused.

## Receipt/evidence fields

For schema/receipt slices, bind source and backend separately:

```text
source_kind=<provider_remote|local_bare_repository|offline_git_bundle>
source_provider=<provider id or none/local>
source_locator=<remote URL/ref, local repo path, or bundle id>
source_acquisition_digest=<digest>
backend_class=<hosted_provider_runner|self_hosted_clean_room|supervised_clean_room>
backend_id=<runner identity>
verifier_id=<tool/version identity>
```

Invalid combinations should fail closed, including attempts to use `local`, `bundle`, or `offline_bundle` as backend classes.

## Fail-closed merge eligibility

A provider-neutral receipt must not be able to assert `status=pass` or `merge_eligible=true` unless every required command has a complete successful execution record:

```text
execution_state=executed
exit_state=completed
exit_code=0
```

Treat these as structural reject or forced non-pass/non-merge-eligible states:

- nonzero exit code;
- timeout/cancelled/failed/not-started/backend-not-executed;
- `exit_state=completed` with `exit_code=null`;
- unknown or revoked policy/revocation state;
- empty `changed_paths` for a merge candidate;
- incoherent source allowlists, for example `source_kind=provider_remote` with `source_provider=none`.

When a schema producer misses any of these, preserve the candidate, mark the review `REPAIR`, issue a same-task fail-closed repair contract, retarget/resume the watcher for the new execution, and update queue/control/handoff to `ACTIVE_PRODUCERS=1` only after bus claim/start proof.

## Non-claim language

Until fresh review is clean, report:

```text
NOT_CLAIMING=fresh independent review clean; merge-ready; pushed schema PR; provider-neutral runtime; production policy switch; canonical full-suite green
```

If canonical has an inherited exact-base clean-room failure, label it as inherited only after base-control reproduction and do not call it canonical full green.

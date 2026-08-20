# Exact PR-head confirmation after a clean candidate review

Use this pattern when a Prismatic repair/candidate has already received an independent exact-head `CLEAN` verdict before publication, then is pushed/opened as a PR.

## Trigger

- A local/branch candidate received independent exact-head `CLEAN`.
- The branch is then pushed and a focused PR is opened.
- Standing authorization allows merge only after exact-head independent/local proof.

## Required sequence

1. Before pushing, verify `origin/main`, local `HEAD`, and worktree cleanliness against the reviewed base/head.
2. Push the already-reviewed branch without amending or rebasing.
3. Open a focused PR whose body includes the problem, repair, verification, hashes/logs, and boundaries.
4. Immediately query the live PR and verify:
   - `headRefOid` equals the independently reviewed commit;
   - base is the expected branch/commit or drift is explicitly reported;
   - PR state is open;
   - no hidden PR-scope content changed.
5. Dispatch or perform a final read-only exact PR-head confirmation review. This can be narrow if the commit/tree exactly matches the already-clean artifact; rerun broad suites only if the revision drifted or the reviewer finds a reason.
6. Update handoff/control state with `PR`, `PR_HEAD`, `EXACT_PR_HEAD_REVIEW`, and the blocked next-task gate.
7. Only after `CLEAN_TO_MERGE`, merge under the applicable standing authorization. Then create an immutable release checkout and verify release state before admitting the next slice.

## Boundaries

- Hosted CI account/spending failures are not code evidence. Do not claim hosted CI green unless it ran and passed.
- Do not deploy, restart services, write Linear, close/delete PRs, or increase producer caps unless separately authorized.
- Do not admit the successor task while the current task is in `EXACT_PR_HEAD_REVIEW=PENDING`, `REPAIR`, or `STALE`.

## Verification-detector repeat warnings

If Hermes' edit detector repeats an "unverified" warning after a compliant `/tmp/hermes-verify-*` ad-hoc verifier and focused/canonical commands have already passed:

- rerun once with an explicit OS-safe `tempfile` verifier only if source files changed or the prior transcript did not include the required proof markers;
- include `AD_HOC_OR_CANONICAL=ad-hoc targeted` and `NOT_CLAIMING=canonical-suite proof` when the verifier is targeted;
- after two compliant same-content passes, classify it as detector non-recognition and do **not** loop identical verification again unless files change.

## Report skeleton

```text
PR=<url/number>
BASE=<expected base commit>
PR_HEAD=<live headRefOid>
TREE=<tree>
CANDIDATE_REVIEW=<delegation id> CLEAN
PR_HEAD_REVIEW=<delegation id> PENDING|CLEAN_TO_MERGE|REPAIR|STALE
NOT_CLAIMING=<no hosted CI/deploy/restart/Linear write unless proven/authorized>
NEXT=<merge release checkout verify | repair/re-review | wait>
```

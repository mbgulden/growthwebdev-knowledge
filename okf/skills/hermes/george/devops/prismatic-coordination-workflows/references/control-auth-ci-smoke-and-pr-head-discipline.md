# Control-auth CI smoke and PR-head discipline

Session-derived pattern for Prismatic central control-auth/RBAC slices where local exact-head proof and independent review pass, but GitHub CI exposes an older smoke/test assumption.

## Trigger

Use this reference when a gateway/control-plane authorization PR changes mutation auth and a release/public smoke, launch smoke, or CI readiness check starts failing with `401`/`403` on a mutation endpoint that previously assumed anonymous access.

## Pattern

1. Treat GitHub CI red as a real gate even after independent exact-head review returned `CLEAN`.
2. Bind the failing CI logs to the exact PR head and determine whether the failure is candidate-caused or baseline:
   - reproduce the smoke on the candidate;
   - compare untouched base when needed;
   - identify the exact request path, method, expected status, and actual status.
3. If the smoke is legitimately exercising a mutation under the new central auth boundary, repair the smoke rather than weakening product auth.
4. Give the smoke an explicit ephemeral test credential:
   - generate random token material at runtime;
   - store only a digest in the temporary credential file;
   - require strict file permissions such as mode `0600`;
   - send `Authorization: Bearer ...` only for the mutation call that needs it;
   - avoid hard-coded tokens and avoid logging the bearer value.
5. Add cleanup for credential/state files on both success and early failure, e.g. `try/finally` plus `atexit`, and verify no temp control-auth credential files remain.
6. Rerun the formerly failing release/readiness command in a clean environment matching CI as closely as possible, not only the direct smoke.
7. Any repair commit after a clean review invalidates that review and all prior exact-head evidence. Re-dispatch independent review against the new head before pushing/updating the PR.
8. If a PR already exists on the older red-CI head, preserve the boundary explicitly: `PR #... remains on older head until new exact-head review is CLEAN`. Do not force-push the repaired head before review.
9. Update proof packet, PR body draft, handoff, and control state to the new head/task/diff digests and changed-path scope; then run a final `/tmp/hermes-verify-*` ad-hoc state verifier.

## Proof packet fields

```text
COMMAND=<formerly failing smoke/release readiness command>
RESULT=PASS
LOG=<path>
SCOPE=public/release smoke under central control auth
AD_HOC_OR_CANONICAL=<GitHub CI reproduction|ad-hoc focused|canonical suite>
NOT_CLAIMING=production credential created, deploy, PR updated, merge, cap increase
MARKER=<slice-specific marker>
```

Also include:

```text
TEMP_CREDENTIAL_FILES_REMAINING=0
PR_HEAD_BOUNDARY=<existing PR still points to old head until clean review>
REVIEW_INVALIDATION=<new commit invalidates prior CLEAN review>
```

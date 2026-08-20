# Provider-neutral hosted-CI billing gate pattern

Use this reference when a Prismatic provider-neutral verification PR has independent exact-head `CLEAN` review, but live GitHub Actions checks fail before executing any workflow steps because of an account/control-plane billing or spending-limit issue.

## Trigger

- PR head is exact and independently reviewed `CLEAN`.
- GitHub checks are red/skipped, but annotations show the job never started, e.g. account payments failed or spending limit must be increased.
- No workflow step logs exist; `STEPS_EXECUTED=0` or equivalent API evidence confirms allocation failure.
- Current durable merge policy still requires hosted CI unless Michael explicitly authorizes a bounded exception.

## Required split verdict

```text
REVIEW=CLEAN
HOSTED_CI=BLOCKED_ACCOUNT_OR_SPENDING_LIMIT
MERGE=HOLD
POLICY_SWITCH=false
DOWNSTREAM_DISPATCH=false
```

Do not call this product-test failure, and do not silently waive it. The code may be independently clean while the current enforced gate is still blocked.

## Direct-source proof checklist

1. Read the live PR state and exact head from GitHub, not only local handoff/control files.
2. Read check-run annotations via GitHub API and bind the exact annotation text to the PR/check-run id.
3. Confirm no auto-merge is enabled and PRs remain open.
4. Confirm the independent review artifact is bound to the same exact head/tree.
5. Update PR comments, Linear, queue/control JSON, and handoff with the split verdict and non-claims.
6. If correcting stale taxonomy in Linear/docs, keep provider source/status adapters separate from verifier execution backends; avoid `adapter/backend` language.
7. Add a silent no-agent watcher only for material check/head changes; verify baseline silence before scheduling.

## Watcher pattern

Use a profile script that snapshots only JSON-native values for:

- PR number;
- head SHA;
- check conclusion/status;
- run/check ids;
- annotation category/message summary;
- auto-merge state.

Baseline it before scheduling:

```text
FIRST_STDOUT=0_BYTES
SECOND_STDOUT=0_BYTES
```

Schedule with `no_agent=True`, delivery to the origin chat, and record the cron job id in durable state. The watcher should stay silent while the billing gate remains unchanged and emit only when either exact head or hosted-CI state changes.

## Safe continuation options

Preferred path:

1. Michael repairs GitHub billing/spending-limit.
2. George reruns hosted CI on the exact heads.
3. Require real workflow steps to execute and pass.
4. Merge the predecessor PR first.
5. Refresh dependent PRs on the merged base.
6. Repeat exact-head review/CI proof before dependent merge.
7. Only then admit downstream provider-neutral verification children.

Exception path:

- Only proceed if Michael explicitly authorizes a bounded hosted-CI exception.
- Scope the exception to named PR(s), exact head(s), non-claims, and required post-merge proof.
- Never use an unmerged future provider-neutral policy to bypass the currently enforced policy.

## Proof packet

```text
COMMAND=<GitHub PR readback + check-run annotation API + queue/control/handoff verifier>
RESULT=PASS|BLOCKED
SCOPE=provider-neutral verification PR hosted-CI gate
AD_HOC_OR_CANONICAL=ad-hoc targeted operational/state verification
NOT_CLAIMING=hosted CI green, merge authorization, merge, deploy, policy switch, downstream dispatch, cap promotion
MARKER=PROVIDER_NEUTRAL_HOSTED_CI_BILLING_GATE_BOUND_OK
```

# Dashboard reconnect source audit + closeout pattern — 2026-07-17

Use this reference when Michael asks for a dashboard reconnect audit, Fred source map, or review of Fred's dashboard/source-integration PRs.

## Session lessons

1. A giant comprehensive audit is not enough. Michael explicitly pushed back that a huge blob is hard for Fred to use.
2. Produce two artifacts when auditing many branches/worktrees:
   - **Full appendix/report** for provenance and deep lookup.
   - **Small execution cheat sheet** for Fred first: do-first sequence, tiny A/B/C/D rubric, source buckets, exact commands, red flags, and pointer to the full report.
3. Deliver Markdown prompts/reports as Telegram-downloadable files using `MEDIA:/absolute/path.md`, not only local paths.
4. For Markdown handoff reports, run a fresh `/tmp/hermes-verify-*` script and remove it afterward. Verify headings, required source paths/markers, ranked rows, and absence of obvious secret assignment patterns.
5. When Fred reports a PR, independently verify before accepting:
   - `gh pr view <n> --json ...` for head/base/state/mergeability/files/CI.
   - Fetch the PR ref if needed and inspect the actual changed files.
   - Verify claimed artifact/doc content and source paths.
   - Run a fresh `/tmp/hermes-verify-*` ad-hoc verifier for the exact claim.
   - Report as ad-hoc targeted unless canonical suite/browser/production proof actually ran.
6. Good dashboard reconnect sequencing from this session:
   - PR #294 style: doc-only source map proving the current durable runtime/main dashboard shell is already correct; do **not** replace shell.
   - PR #295 style: port one small candidate (GRO-3355 Resources budget caps) into a clean branch, preserving current shell and `/api/gateway/...` conventions.
7. After a clean candidate PR is review-ready, do not keep assigning Fred more reconnect/source-mining by default. Pause for merge/deploy/prod proof decisions, then move Fred to the next workflow gap if appropriate.

## A/B/C/D cheat sheet pattern

Use this tiny rubric in the shareable digest:

| Label | Meaning | Fred action |
|---|---|---|
| A | likely dashboard preservation/integration source | inspect immediately |
| B | governance/workflow source | inspect after dashboard shell map |
| C | runtime/canonical comparison anchor | diff against, do not blindly overwrite |
| D | archive/cleanup source | fallback only |

Keep the digest around 1–2 pages when possible. The full audit can be 100+ rows, but Fred should receive the digest first.

## Closeout decision language

Use precise closure language:

- **PASS / review-ready**: PR exists, CI green, changed files match claim, local/focused proof passes.
- **PARTIAL / not fully closed out**: PR is not merged/deployed, browser/production proof not run, or canonical suite not run.
- **Ready for different work**: yes when the current PR is a review artifact and no immediate Fred action is needed until Michael decides merge/deploy.

Suggested next-work guidance after dashboard reconnect source map + first clean candidate:

```text
Do not start another dashboard reconnect/source-mining slice.
PRs are review-ready; pause for Michael merge/deploy decision.
Next workflow gap after dashboard stabilization: AGY_COMPLETED_WORK_INTEGRATION_GATE_OK.
Start with a doc/API contract slice unless runtime merge behavior is explicitly authorized.
```

## Verification packet example

```text
COMMAND=gh pr view <n> + git diff/static checks + fresh /tmp/hermes-verify-* behavior verifier
RESULT=PASS
LOG=/tmp/george-<topic>-review.log
SCOPE=<exact claim scope>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=merged, deployed, production/browser proof, canonical full-suite green
MARKER=<TOPIC>_REVIEW_OK
cleanup=PASS verifier_removed=/tmp/hermes-verify-<topic>.py
```

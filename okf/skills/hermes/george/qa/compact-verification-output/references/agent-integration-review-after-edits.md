# Agent Integration Review After Edits

Session lesson: when reviewing another agent's integration of your previous code/design changes, treat the review as its own verification task, not just a narrative code read.

## Pattern

1. Identify the integration commit/branch and changed paths.
2. Review the actual files for behavior, not just the commit title or report.
3. Create a temporary verifier with an OS-safe path and `hermes-verify-` prefix:
   - `VERIFY=$(mktemp /tmp/hermes-verify-<topic>-XXXXXX.py)`
   - `LOG=/tmp/<topic>-review.log`
4. Verify the exact integration behavior markers:
   - syntax/parse checks for edited code
   - expected routes/endpoints exist
   - important status/lifecycle fields are written and cleared in the right flows
   - public/semi-public page metadata and routing markers exist
   - lifecycle/cleanup scripts include the required state transitions
   - docs/governance artifacts mention the operational rules
5. Clean up the temporary verifier and report `VERIFIER_CLEANUP=PASS|FAIL`.
6. Label the result as `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the project canonical suite actually ran.
7. If the first verifier fails because the verifier itself used an over-specific or wrong marker, inspect the log, fix the verifier, rerun, and mention only the final valid proof plus the boundary. Do not claim the original failure was product failure unless confirmed.

## Review output shape

Lead with:

```text
COMMAND=<temp verifier command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<integration areas verified>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=<canonical/deploy/live-browser/live-container boundaries>
MARKER=<review marker>
VERIFIER_CLEANUP=<PASS|FAIL>
```

Then separate:

- **What is good / keep**
- **What I would add before production**
- **Blocking vs polish**
- **Exact next closeout slice**

## Production-closeout pitfall

A local integration can pass syntax and marker checks while still missing operationalization. For lifecycle/demo/access work, always look for:

- scheduler/timer actually installed for lifecycle scripts
- one-use/renewal governance for free trials
- PII/account deletion vs container/workspace deletion defined separately
- user-facing copy aligned with trial expiry and grace period
- live route/API/bot/container proof before claiming production readiness

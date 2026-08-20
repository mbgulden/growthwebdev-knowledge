# Cron post-final verification nudge — 2026-07-18

Context: after a cron task had already been finalized, pushed, PR-created, and reported, the platform emitted a follow-up verification warning:

- `Verification status: stale`
- named canonical command: `npm run build`
- changed paths included both repo files and `/tmp/issue-batches/<ISSUE>_RESULT.md`

## Durable pattern

Treat the nudge as a fresh verification contract, not as a request to defend prior output.

1. Run the exact named canonical command from the implementation worktree, even if the same command passed minutes earlier.
2. If changed paths include tool/source/docs plus a result artifact, add a small ad-hoc `/tmp/hermes-verify-*` verifier that checks the task-specific acceptance contract and the artifact/doc invariants.
3. The verifier should print:
   - `verifier_path=...`
   - `tested_command=...`
   - assertion summary
   - `verification_exit=0`
   - cleanup status after removing itself
4. Check `git status --short --branch` after verification to confirm generated build output did not dirty the branch.
5. Check the result artifact still exists and is non-empty if it was listed in changed paths.
6. Final response should be short: state the fresh command pass, ad-hoc verifier pass, clean workspace/result presence, and preserve any existing caveat that is still true.

## Example

```bash
npm run build
VERIFY=$(mktemp /tmp/hermes-verify-<issue>-fresh-XXXXXX.py)
python3 "$VERIFY"
rm -f "$VERIFY"
git status --short --branch
test -s /tmp/issue-batches/<ISSUE>_RESULT.md
```

## Pitfall

Do not re-open implementation scope or add unrelated fixes unless the fresh verification fails. A verification-only nudge is not permission to continue broad task work; it is a request for fresh detected evidence.
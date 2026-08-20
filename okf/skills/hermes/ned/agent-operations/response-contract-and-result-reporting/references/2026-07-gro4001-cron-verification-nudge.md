# GRO-4001 cron verification nudge: fresh evidence after finalization

## Trigger

A post-task Hermes/system nudge said verification was `stale` even though the implementation had already been committed, finalized, pushed, and summarized. The nudge named the canonical command: `npm run build`, and listed edited paths under `/tmp/hd-platform-gro4001`.

## Correct response pattern

Treat this as a verification-only task, not an invitation to resume implementation.

1. Re-run the exact canonical command from the active implementation worktree:
   ```bash
   cd /tmp/hd-platform-gro4001 && npm run build
   ```
2. Read and report the fresh result, including postbuild if present.
3. Add a fresh `/tmp/hermes-verify-*` ad-hoc verifier for the behavior the build does not directly assert. For GRO-4001 this checked generated HTML for:
   - `property="og:image"`
   - `property="og:image:secure_url"`
   - `property="og:image:alt"`
   - `name="twitter:image"`
   - `name="twitter:card" content="summary_large_image"`
   - absolute `https://humandesignengine.com/somatic_mandala.png`
4. Remove the temporary verifier and explicitly report cleanup.
5. Confirm git state if relevant.
6. Stop. Do not broaden scope, amend the already-pushed branch, or re-run finalize unless verification fails or Linear/PR state actually requires correction.

## Reporting shape

Lead with fresh verification status:

```md
✅ Fresh verification now passes.

**Verified just now**
- `npm run build` passed in `<worktree>`.
- Fresh ad-hoc verifier passed for `<specific behavior>`.
- Temporary verifier was removed.
- Worktree is clean.

Caveat: <external PR/deploy check still failing, if applicable>.
```

## Pitfall

Do not argue from the previous successful build transcript. The detector is asking for fresh evidence in the current turn. Rerun the named command and create a new verifier whose path starts with `/tmp/hermes-verify-`, then delete it.
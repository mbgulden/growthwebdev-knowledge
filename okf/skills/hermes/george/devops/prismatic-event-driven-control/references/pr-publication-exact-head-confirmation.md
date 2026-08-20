# Prismatic PR publication and exact-head confirmation

Use when a Prismatic candidate already has independent exact-head `CLEAN`, then gets pushed/opened as a PR.

## Checklist

1. Verify local `HEAD`, expected base, and clean worktree before push.
2. Push the reviewed branch without amending/rebasing.
3. Open a focused PR with problem, repair, proof, hashes/logs, and boundaries.
4. Query the live PR and verify `headRefOid` exactly equals the reviewed commit.
5. Dispatch or perform a final read-only PR-head confirmation review.
6. Keep successor tasks blocked until the PR-head review returns `CLEAN_TO_MERGE`.
7. After merge, verify immutable release checkout before admitting the next slice: fetch `origin/main`, confirm the merge tree equals the reviewed candidate tree, clone a non-local release checkout with no Git alternates, run `git fsck --full`, and perform focused release/package validation from that checkout.

## Boundaries

- Do not treat hosted CI account/spending failures as code evidence.
- Do not claim deployment/restart/Linear writes unless separately authorized and proven.
- Do not admit the next task while PR-head review is pending, stale, or repair-required.

## Repeated Hermes verification warnings

If the edit detector repeats an unverified warning after compliant `/tmp/hermes-verify-*` evidence:

- rerun once if files changed or proof markers were missing;
- label targeted checks as `AD_HOC_OR_CANONICAL=ad-hoc targeted`;
- after two compliant same-content passes, stop looping and report detector non-recognition rather than inventing canonical proof.

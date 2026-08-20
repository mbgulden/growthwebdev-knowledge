# Parent acceptance: clean consolidation candidate before review

Use when a parent issue is an acceptance gate over several child branches and the prior candidate PR is conflicting.

1. Query child states, the existing candidate PR, and its CI before locking or editing. Children merely being `In Review` is not whole-phase proof.
2. Preserve the old conflicting PR. Create a new `ned/<PARENT>` branch from the candidate, rebase it onto current `main`, and open a new PR rather than force-pushing/reusing the stale conflict path.
3. During rebase conflicts, treat current `main` as the compatibility baseline. Retain it for redundant/format-only/stale evidence conflicts; then inspect the resulting diff so required parent gates are still present. Do not blindly prefer an older extraction branch.
4. Commit documentation of the parent gate and every code/format repair before running verification.
5. Run the whole standalone acceptance proof from an isolated environment: literal `pytest -q`, lint/format, compile, sdist/wheel, installed-wheel resource lookup outside the checkout, and a bounded committed-secret scan. Wait for the new PR's CI; record exact green checks.
6. Run `finalize_task.sh` as governed, but do not trust its transcript. Re-query Linear state and actual lock ownership. If it reports `In Review` but readback is `In Progress`, explicitly `issueUpdate` to the review-state ID, post one evidence refresh with the PR/checks, re-query, and unlock with the same two-argument ownership shape used at acquisition.
7. Write `/tmp/issue-batches/<PARENT>_RESULT.md` only after the final state, evidence comment, PR state, and lock release are authoritative.

Do not merge the PR, mutate unrelated child branches, or claim monorepo cutover merely because the standalone parent candidate is ready for review.

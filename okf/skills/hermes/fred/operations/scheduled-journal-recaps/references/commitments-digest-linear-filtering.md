# Commitment Digest Linear Filtering — 2026-07-09

## Context
A morning briefing repeated `GRO-1905` as a Michael-owned Stripe blocker even though Michael corrected that Stripe had been configured long ago. Live Linear showed `GRO-1905` was already `Done`, while the local commitments JSON still had the item open.

## Durable Lesson
For commitment digests and morning briefings, local journal/commitment state is advisory. If a commitment has a Linear identifier, check live Linear state before surfacing it as a blocker. Completed Linear issues should be filtered out or the local commitment should be marked resolved.

## Workflow Pattern
1. Find the stale commitment in the local commitment store by `linear_issue_identifier`.
2. Query live Linear for the issue state.
3. If `state.type == completed`, mark the local commitment resolved with a note that Linear is canonical.
4. Patch the digest generator to best-effort filter completed Linear identifiers before grouping/reporting open commitments.
5. Verify with an ad-hoc `/tmp/hermes-verify-*` script that:
   - a fake completed issue is removed from digest output,
   - a fake open issue remains visible,
   - the changed module compiles,
   - the verifier file is cleaned up.

## Example Verification Shape
Use Python `tempfile.NamedTemporaryFile(prefix='hermes-verify-', suffix='-commitments-digest.py', dir='/tmp', delete=False)` and monkeypatch the digest module's `CommitmentStore` plus `_linear_completed_identifiers` function. Assert the completed identifier/text is absent and the open identifier/text is present.

Label the result as **ad-hoc targeted verification**, not suite-green.

## Pitfalls
- Do not report stale local commitments as current blockers when the linked Linear issue is already Done.
- Do not let an unavailable Linear API block the briefing entirely; the live filter should be best-effort and fail open.
- Do not claim full/canonical suite-green for a focused temporary verifier.

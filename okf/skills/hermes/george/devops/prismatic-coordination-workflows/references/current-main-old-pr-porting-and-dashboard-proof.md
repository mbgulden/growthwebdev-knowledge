# Current-main old-PR porting and dashboard proof checklist

Session-derived checklist from the PR #342/#343 sequence: port useful old Fred work onto current `main` without wholesale merging stale branches.

## When to use

Use when an old PR/branch has useful Prismatic governance/dashboard work but `main` has moved through other safety gates since the old branch was cut.

## Old PR porting workflow

1. Start from fresh current `origin/main` in a clean worktree.
2. Treat old PRs as source material only; do not cherry-pick/merge the whole branch unless explicitly authorized and independently proven safe.
3. Port path-by-path and preserve already-merged safety behavior from newer PRs.
4. Before opening a PR, verify the semantic contract against both:
   - Python/runtime behavior; and
   - JSON Schema/package or API-facing contract where applicable.
5. Specifically probe nested object/list/scalar malformed payloads, unknown properties, and secret-bearing strings. Python validators and JSON Schema must agree on rejection and must not echo secrets.
6. Keep the PR body explicit about old-PR provenance, evidence, and non-claims.

## Dashboard/card restoration workflow

1. Reconnect the card into the canonical dashboard shell; do not create a mini/fallback dashboard as the primary user experience.
2. Seed a browser-proof matrix for at least ready, blocked/partial, unavailable/historical, and API failure states.
3. Verify the card exists exactly once, leaves loading/checking, and reads state from the real API adapter.
4. For mobile proof, use rendered browser/CDP measurements, not only static CSS or screenshot inspection:
   - viewport/client width;
   - card left/right bounds;
   - card count;
   - visible badge/state;
   - document/body scroll width before and after the slice when the broader dashboard already has overflow.
5. If baseline mobile overflow already exists, report non-regression precisely: e.g. "new card is within the 390 client and did not increase existing scroll width". Do not claim the global dashboard overflow is fixed.

## Raw-output capture adapter gap

If a raw-output dashboard/API already exists, inspect the real dispatcher/result-writeback path before declaring the workflow complete. A repository may have `persist_raw_output(...)`, queue/API/dashboard tests, and manual insert paths while still lacking actual pre-normalization capture from assigned-agent runs.

Required adapter properties:

- capture once before packet extraction/normalization;
- use launch/run ID as idempotent source-event ID;
- preserve existing terminal reconciliation/latest-packet behavior;
- make capture failures observable without changing packet classification;
- bound payload size/retention;
- keep private directory/database permissions;
- do not expose raw text through API/dashboard;
- avoid persisting secret-like output verbatim;
- keep repair previews read-only and reruns operator-only/non-dispatching.

## Proof block fields

```text
COMMAND=<focused tests, schema agreement probes, dashboard JS/browser/CDP proof, GitHub checks>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
BROWSER_PROOF_DIR=<path if relevant>
SCOPE=current-main path port from old PR material
AD_HOC_OR_CANONICAL=ad-hoc targeted|browser proof|GitHub CI|canonical suite
NOT_CLAIMING=<merge/deploy/global mobile fix/real dispatch/etc.>
MARKER=<review marker>
```

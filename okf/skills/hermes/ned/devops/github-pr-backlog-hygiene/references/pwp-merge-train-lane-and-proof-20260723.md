# Merge-train lane split and superseded-proof pattern

## Situation
A clean, authorized PR merge train hit a conflict after an earlier documentation PR merged. The next PR contained both:
- an owned workflow change under `.github/workflows/ci.yml`; and
- a conflicting documentation update under `docs/REPOSITORY_GUARDRAILS.md`, outside Ned's write lane.

## Safe resolution
1. Merge only the reviewed, authorized PRs up to the first conflict.
2. Do not resolve the docs conflict from the code/infra lane.
3. Create a focused Linear child for the docs-only conflict, label the docs owner (`agent:agy`) and `dispatch:ready`, and attach exact paths, PRs, and the accepted policy decision.
4. Once the docs PR lands, rebase the workflow-only PR, verify it has no docs diff, rerun focused local checks, inspect GitHub checks and mergeability, then continue the explicitly authorized train.
5. Re-query mergeability before every next merge. `UNKNOWN` may settle to a mergeable state but a real `CONFLICTING`/`DIRTY` state must be handled first.

## Historical-proof PR cleanup
A later proof PR may be unrebaseable because its ancestry replays implementation commits that have already landed. Do not force-resolve broad conflicts just to preserve an old proof branch.

Instead:
1. Abort the rebase and release every acquired lock.
2. Run the full proof on current `main` from a fresh clone: new venv, non-editable wheel install outside the checkout, package-resource reads, tests, lint/format, compile, build, and bounded secret scan.
3. Close the old proof PR as superseded, with the exact verified `main` SHA and proof results in a PR comment.
4. Treat the final `main` CI run as authoritative; cancelled intermediate merge-train CI runs are expected under concurrency and are not failures if the final SHA is green.

## Authorization boundary
Do not infer permission to merge from “keep moving” where a source task explicitly says not to auto-merge. Ask for explicit merge-train authorization. Once granted, merge only the named ordered train; pause and route any lane conflict rather than broadening authority.

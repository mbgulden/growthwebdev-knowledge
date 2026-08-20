# Distribution portability clean-room wheel gate

Use this reference when a Prismatic source PR merges and source/editable CI is green, but an immutable standalone release must prove it is actually portable outside the repo checkout.

## Session-derived trigger

A dispatch-cursor source repair merged cleanly and passed GitHub CI plus release-local canonical/source tests, but the standalone non-editable installed package failed release readiness from a clean-room CWD because shipped plugin resources were still discovered via repository-root assumptions. The observed symptom was a policy/readiness response like `409 unknown plugin: example-plugin` despite source/editable tests passing.

## Correct classification

- `SOURCE_PASS_MERGED` if exact-head review, CI, and merge-SHA source proof pass.
- `STANDALONE_RELEASE_BLOCKED_DISTRIBUTION_PORTABILITY` if the installed wheel cannot discover shipped resources from arbitrary CWD.
- Do **not** call the release deployable, publishable, or runtime-converged until the clean-room installed-wheel gate passes.
- Treat this as a separate source slice from the already-merged feature/fix; do not reopen or muddy the closed PR unless the exact merge artifact is wrong.

## Immutable release proof sequence

1. Read back the authoritative GitHub merge SHA and remote `main` SHA.
2. Create a standalone detached release directory under `.prismatic/releases/<name>-<merge-prefix>` pinned to that merge SHA.
3. Verify release Git independence:
   - `git rev-parse HEAD` equals merge SHA.
   - `git rev-parse HEAD^{tree}` equals expected tree.
   - `git status --porcelain` is clean.
   - `.git/objects/info/alternates` is absent.
   - release does not depend on mutable repair/runtime checkouts.
4. Run release-local source proof: focused tests, canonical suite, static checks, package build, and isolated installed-wheel import.
5. Run the clean-room installed-wheel readiness proof from an arbitrary temporary CWD, not from the repository root and not editable/source install.
6. Assert known shipped resources/plugins are discoverable and unknown plugins remain blocked. Passing source tests alone is a false positive.
7. Write a receipt with exact command summaries, log paths, release path, SHAs, proof classes, non-claims, and blocker classification.

## Clean-room wheel acceptance requirements

A portability repair is not complete until all are true:

- Shipped plugin/resource discovery works from the installed wheel when CWD is outside the source checkout.
- Source checkout is not on `PYTHONPATH` and the server/import path resolves to the installed package.
- Discovery uses package data/resource APIs or another explicitly portable mechanism, not parent-directory walking back to the repo.
- Unknown-plugin requests still fail closed with the expected policy/readiness status.
- Auth, mutation guards, and policy checks are not weakened to make the smoke pass.
- Tests prove both source/editable and non-editable wheel behavior so CI cannot regress into source-only coverage.

## Producer contract for the follow-up slice

Use one cap-1 producer from the merge SHA with explicit boundaries:

```text
OBJECTIVE=portable shipped-plugin discovery and release readiness from non-editable installed wheel independent of source checkout or CWD
MUST_PROVE=clean-room wheel discovery; unknown-plugin blocking; release readiness; canonical suite; static checks; build; clean worktree; exact allowed paths
MUST_NOT=push; open PR; merge; deploy; restart; mutate live DB/cursor; write Linear; resume generic dispatch; raise cap; weaken auth/policy
```

Treat producer output as untrusted. If the producer begins editing, dirty paths are not evidence; classify parent/child process trees so a normal AGY shell+Python child is not counted as two producers, then wait for exit before candidate review.

## Distribution-portability candidate review addendum

When a producer repairs shipped-resource portability by moving bundled plugin assets into package data:

1. **Inspect source/package shape before trusting tests.** Confirm bundled plugin manifests/modules live under the package (for example `prismatic/shipped_plugins/...`), package metadata includes them in wheel and sdist, and any legacy top-level `plugins` path is a compatibility shim/symlink rather than a second source of truth.
2. **Probe archive contents directly.** Open both the built wheel and sdist and assert representative manifests/modules exist, including at least one legacy/example plugin and one real shipped plugin. Do not treat `python -m build` success as proof package data was included.
3. **Probe arbitrary-CWD behavior through the installed wheel.** Install the wheel into a temporary venv, `cd` to an empty directory outside every repo/worktree, import the package, list the plugin catalog, run a known allowed policy preview, and verify an unknown plugin still blocks.
4. **Review override semantics as authority boundaries.** Check explicit `plugins_dir` arguments and `PRISMATIC_PLUGINS_DIR` separately from bundled discovery. In Prismatic, these are operator override boundaries, not additive extension paths: when present, shipped plugins must not silently participate. Additive behavior creates ambiguous operator intent and can hide collisions.
5. **Fail closed on duplicate plugin names.** Within any effective discovery boundary, create two directories with the same manifest `name` and prove every duplicate entry is invalid and policy preview blocks the name. Never accept first-match/first-shipped wins as a safe collision policy.
6. **Prove source-vs-installed isolation with an import-prefix assertion.** Installed-wheel public launch/release smoke must run from the fresh venv interpreter, from an empty arbitrary CWD, with `PYTHONPATH` and source override variables stripped, and assert `prismatic.__file__` is under the expected installed prefix. Source harnesses may inject the checkout only when no installed-prefix assertion is active.
7. **Run public and release smoke from the installed wheel, not only catalog tests.** Clean-room wheel acceptance should exercise `public_launch_smoke.py`, `release_smoke.py`, and public-security readiness from the installed interpreter so FastAPI/resource/path assumptions are caught outside the source checkout.
8. **Check resource lifetime.** If the implementation uses `importlib.resources.as_file()` for directory resources, verify the returned path is consumed while the context is alive or materialized safely; do not retain temporary resource paths after context exit.
9. **Control unrelated live-network tests honestly.** If the canonical suite unexpectedly starts a live-network Lighthouse/SEO monitor unrelated to the slice, preserve process evidence, terminate the orphan group, rerun the suite with that test explicitly deselected, and label it `controlled canonical-minus-network`, not full canonical green. Full canonical remains a GitHub/exact-head gate later unless rerun without deselection.
10. **Dispatch independent review after local green and re-review after every repair commit.** Bind exact head/tree, clean status, changed-path summary, proof log hashes, zero task processes, and controlled-suite boundaries. Ask the reviewer to inspect symlink/archive portability, source-vs-installed false positives, collision/override behavior, unknown-plugin safety, package bloat/test-fixture leakage, and whether CI truly runs non-editable wheel proof. If review returns `REPAIR`, preserve/hash the rejected candidate review, repair the same task transparently, and dispatch a fresh exact-head re-review; prior `CLEAN`/local-green evidence does not carry forward across the new commit.
11. **Treat CI workflow repairs after a clean review as new exact-head candidates.** If PR CI fails because a newly added workflow installed too narrow a dependency set, repair the workflow narrowly, prove the dependency graph locally (for example `all -> gateway -> fastapi` when repository tests import FastAPI), and rerun the exact gate plus focused tests. Do not push the CI-only child merely because the product diff was already clean-reviewed; the child changes the PR head and needs a focused read-only re-review before push/merge. Add path triggers for moved package-data/resource boundaries (`prismatic/shipped_plugins/**` plus discovery/policy modules) so the gate reruns when shipped resources change.

## Release clone pitfall

If a local clone source cannot see GitHub's new merge object or sets `origin` to a local source during clone, do not accept partial release directories. Remove the unaccepted directory and recreate/fetch from the authoritative GitHub remote or explicitly set `origin` to GitHub before fetching the merge SHA.

## Report wording

Use split verdict language:

```text
RESULT=SOURCE_PASS_MERGED;STANDALONE_RELEASE_BLOCKED_DISTRIBUTION_PORTABILITY
AD_HOC_OR_CANONICAL=GitHub CI + release-local canonical/source proof + clean-room installed-wheel readiness
NOT_CLAIMING=deployment,restart,live DB/cursor mutation,runtime convergence,publishable distribution,cap increase
NEXT_GATE=focused distribution-portability source slice with clean-room wheel acceptance and fresh independent review
```

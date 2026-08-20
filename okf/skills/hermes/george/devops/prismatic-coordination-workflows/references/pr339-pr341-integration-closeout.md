# PR339–PR341 integration closeout patterns

Session-derived detail for George-style Prismatic integration work when multiple helper branches must be made real in production without breaking existing runtime state.

## Core lessons

1. **Subagent review is a lead, not proof.** Parallel read-only reviews are useful for finding old-branch overlap and hidden bypasses, but their self-reports must be verified by George with direct PR/API/file/readback before claiming success.
2. **Revalidate persisted legacy state, not only new writes.** A promotion gate can be correct for newly generated decisions while old persisted `decision_ready` records remain unsafe. List/get/operator paths must re-check current durable evidence and fail closed without mutating the production ledger unless explicitly authorized.
3. **Positive and negative evidence both matter.** A blocked-path proof alone is insufficient. Require unavailable evidence -> held, incomplete evidence -> held/no operator execution, complete retained evidence -> dry-run-ready only, and side-effect booleans false unless authorized.
4. **Package runtime contracts, then prove from the installed wheel.** Handoff/current-event schemas that pass from source may still fail in operational installs if package data is missing. Build a wheel in a temp venv and prove schema access outside the source checkout.
5. **Malformed nested payloads must fail closed.** For assigned-agent handoff/event gates, probe malformed nested object/list/scalar cases so bad inputs produce a hold/manual-review decision instead of a crash or pass.
6. **Minimal overlay can be safer than runtime reset.** If production contains unrelated dirty-but-good dashboard/governance files, preserve them, copy only the authorized modules from an immutable release, compile them in the stable venv, restart the service, and verify unrelated file hashes are unchanged.
7. **Pause completed change-only watchers.** Once a bounded slice is merged/deployed or repaired/green, pause its noisy watcher and retarget a new watcher for the next bounded task instead of leaving stale task monitors running.
8. **Verify the actual active service topology before restarts.** In Prismatic, the active Gateway may host dispatcher behavior while a standalone `prismatic-dispatcher.service` is inactive or has no configured runtime. Restart the service that actually imports/serves the changed modules, and explicitly report untouched inactive/irrelevant services so a future operator does not assume they were refreshed.
9. **Canary fixtures must match the assigned-agent route.** Handoff fixtures copied from Fred/AGY tests may declare `target.agent=agy`; if using them to prove a Kai launcher/preflight, adjust the fixture target to `kai` or choose a matching launcher. Otherwise the canary failure may only prove a target-agent mismatch, not a production bug.
10. **Narrow overlays are not always two modules.** Handoff-contract deploys may require docs, root schema, package schema, CLI script, `pyproject.toml`, and dispatcher modules together. Preserve the invariant “only authorized paths from the immutable release,” not the exact count from an earlier slice.

## Production-safe narrow-overlay checklist

Use when the deployed runtime checkout is dirty for unrelated reasons and the authorized PR only changes a narrow runtime/file set.

- Read back PR state, CI, head, and exact merge SHA from GitHub.
- Create immutable release checkout pinned to the merge SHA.
- Run release-local proof from the immutable checkout: py_compile, focused pytest, ruff/format, package build if packaging changed.
- Before touching runtime, save to `.prismatic/deployments/<slice>/`:
  - runtime HEAD/branch/status;
  - dirty patch and untracked manifest;
  - copies/checksums of target modules;
  - checksums of unrelated dirty/untracked deployed files to preserve;
  - service status/log excerpt;
  - pre-deploy API readbacks;
  - production ledger checksum/stat when ledger safety matters.
- Overlay only the authorized files from the immutable release.
- Compile overlaid files using the stable production venv.
- Restart the service only when authorized.
- Verify service active, health/dashboard/API status, expected new fields/behaviors, target module hashes match release, unrelated runtime files still match pre-deploy hashes, ledger checksum unchanged if non-mutation was required, and rollback doc exists.

## Compact proof fields to include

```text
PR=<number>
PR_STATE=MERGED|OPEN
MERGE_SHA=<sha>
RELEASE=<immutable checkout>
DEPLOYMENT=<deployment receipt dir>
AD_HOC_OR_CANONICAL=GitHub CI plus targeted release and production proof
RUNTIME_UNRELATED_PATHS_PRESERVED=true|false
PRODUCTION_LEDGER_MUTATED=false|true
ROLLBACK_READY=true|false
MARKER=<slice marker>
```

## Sequencing pattern for old branches/PRs

- Treat old PRs as asset sources, not merge candidates, after main has moved through related governance changes.
- Port unique value path-by-path onto current main and reconcile with already-merged semantics before opening a focused PR.
- Examples of classifications:
  - useful logic superseded by new PR -> do not merge wholesale;
  - unique raw-contract capture/validator assets -> fresh current-main port;
  - stale dispatcher/writeback semantics -> do not cherry-pick; rebuild narrow adapter preserving latest monitor semantics;
  - dashboard presentation over superseded backend -> port only evidence-aware UI card/fetch path after backend contract is current.

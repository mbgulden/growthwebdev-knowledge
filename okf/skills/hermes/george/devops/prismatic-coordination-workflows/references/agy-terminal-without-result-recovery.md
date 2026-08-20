# AGY terminal-without-result recovery pattern

## Trigger

Use this when a cap-1 AGY/assigned-agent producer reaches a terminal process state but does not produce an authoritative `RESULT.md`, canonical completed-work packet, or commit — especially after a timeout/SIGTERM while the task contract had no wall-clock cap.

## Durable sequence

1. **Do not launch a replacement producer automatically.** First prove the original event/run identity, process exit, cleanup receipt, cap-slot release, selectable-event count, and writer leases.
2. **Separate producer provenance from operator recovery.** Partial producer artifacts can be evidence, but they are not acceptance. If a producer packet was captured against the wrong isolated server/import path, label it provenance-only and regenerate proof from the exact candidate artifact.
3. **Recover only the same bounded task.** Preserve the original task/event id, base commit/tree, branch/worktree, and allowed changed-path set. Do not broaden scope while recovering.
4. **Freeze an exact candidate.** Commit only the allowed paths; record `HEAD`, `HEAD^{tree}`, parent, changed-path list, and `git status --porcelain == empty` before review.
5. **Rebuild from the exact candidate.** Build/install the wheel or equivalent immutable artifact and prove behavior from that installed artifact, not from a mutable source import.
6. **Create a stable recovery packet.** Copy only quiescent artifacts into a packet directory, exclude live append logs, write a receipt with producer/operator boundaries, and generate a `SHA256SUMS` ledger that excludes itself. Re-run `sha256sum -c SHA256SUMS` and record the ledger hash.
7. **Dispatch independent exact-head review before push/merge/deploy.** Reviewer context must include which artifacts are authoritative and which producer artifacts are non-authoritative/provenance-only.
8. **Update handoff to the true state.** Replace stale `ACTIVE_CAP1_PRODUCER`/`running` with terminal/review-pending, cleanup, slot, exact candidate, packet, and review ids. This coordination edit still needs post-edit ad-hoc verifier evidence.

## Proof block

```text
PROCESS_ALIVE=false
PROCESS_CLEANUP_VERIFIED=true
ACTIVE_SLOT_PRESENT=false
SELECTABLE_EVENTS=0
WRITER_LEASES=0
PRODUCER_RESULT_EXISTS=false
CANONICAL_STATE=review_pending
RECOVERED_CANDIDATE=<sha>
RECOVERED_TREE=<tree>
CHANGED_PATHS=<bounded list/count>
PACKET=<path>
LEDGER_SHA256=<sha256-of-SHA256SUMS>
INDEPENDENT_REVIEW=<delegation id/status>
NOT_CLAIMING=producer PASS, accepted, push, merge, deploy, live proof
```

## Pitfalls

- `runtime_deadline=null` does not guarantee the underlying CLI/harness will never terminate; classify the concrete launcher/CLI boundary without turning it into a generic environment prohibition.
- A partial browser packet can be structurally useful but invalid for route proof if it bound the wrong server. Verify request URL, page URL, response source, and installed-artifact identity explicitly.
- Mobile DPR proof can be a non-regression proof rather than an overflow fix. State the measured current-production and candidate `scrollWidth` values and the non-claim.

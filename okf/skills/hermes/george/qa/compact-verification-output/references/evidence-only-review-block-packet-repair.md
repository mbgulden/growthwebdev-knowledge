# Evidence-only review block packet repair

Use when independent review says the source candidate is acceptable or unchanged, but blocks because the proof packet is incomplete.

## Pattern

1. Preserve the review outcome exactly: `V<N>_REVIEW=BLOCKED evidence only`.
2. Do not rewrite the old packet as authoritative and do not recast the failed/terminated producer as completed.
3. Bind the repaired packet to the unchanged exact head/tree and explicitly prove `SOURCE_CHANGED_AFTER_REVIEW=false`.
4. Regenerate only the missing evidence, preferably from an installed artifact or exact candidate runtime.
5. Include machine-readable fields for what the reviewer could not reconstruct, such as:
   - untruncated DOM/text;
   - per-surface API requests;
   - response source values;
   - classifications;
   - request initiators;
   - route/page attribution;
   - screenshot dimensions and viewport/DPR.
6. Freeze a new stable packet directory with a self-excluding ledger.
7. Run a focused verifier that reads the frozen packet back and checks schema/ledger/nonclaims.
8. Dispatch independent re-review against the new packet; do not push, merge, deploy, or accept before `CLEAN`.

## Compact nonclaim block

```text
OLD_PACKET_REVIEW=BLOCKED evidence only
NEW_PACKET=<path>
SOURCE_CHANGED_AFTER_REVIEW=false
AD_HOC_OR_CANONICAL=ad-hoc focused evidence packet
NOT_CLAIMING=canonical rerun, independent clean review, merge, deploy, live acceptance
```

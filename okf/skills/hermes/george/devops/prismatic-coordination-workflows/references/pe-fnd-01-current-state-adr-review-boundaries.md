# PE-FND-01 current-state ADR review boundaries — 2026-07-27

Use this reference when producing or reviewing Prismatic current-state architecture/source-of-truth ADRs.

## Durable lessons

Independent review blocked an otherwise plausible ADR because it blurred three different authority classes:

1. **Candidate/evidence contract is not operational merge authority.** `MergeCandidateManifest` can validate/serialize candidate evidence and promotion-state fields, but it does not instantiate `MergeFactoryStore`, submit decisions, acquire locks, call GitHub, mutate Linear, merge, release, or deploy. Current-state maps must identify `prismatic/core/merge_factory.py` / `MergeFactoryStore` as operational merge control when present.
2. **Dashboard/projection state must be listed separately from control truth.** `merge-pipeline/state_v6.json` is a live dashboard/merge-status projection surface and belongs in the duplication/convergence inventory. Do not omit it just because it is not the canonical decision store.
3. **Deployment gaps must remain gaps.** If no single integrated in-repo deployment authority/receipt exists, say so. Do not imply that review/admission/merge receipts already imply deployment/activation, and do not draw a happy-path arrow to deployment without an explicit missing-boundary note.

## Review checklist for source-of-truth ADRs

Before accepting a current-state map, require exact source-grounding for these lanes when in scope:

- canonical AGY run state;
- event admission and EventBus path resolution;
- producer supervision (`scripts/agy_sandbox_event_supervisor.py`/raw subprocess paths when active);
- independent review and provider-neutral receipt storage;
- artifact provenance (`UniversalArtifactStore` or successors);
- dashboard projections (`merge-pipeline/state_v6.json`, JSON mirrors, UI state files);
- merge evidence vs candidate contract vs operational merge control vs merge execution;
- release/deployment authorization and receipts, explicitly separated from review/admission;
- remaining duplicate state stores and convergence/deletion disposition.

## Acceptance wording pattern

Prefer wording like:

```text
Merge evidence is recorded by <receipt store>. Candidate contract is represented by <manifest>. Operational merge decisions/locks are handled by <store>. Legacy merge execution still exists at <path> and is not yet uniformly fenced. No canonical deployment receipt currently exists in-repo; deployment remains a separately authorized boundary and is not implied by review/admission.
```

## Pitfalls

- Do not treat an `Accepted` ADR status as proof that convergence work is done; it can mean the current-state source-of-truth map is accepted while deletion/repair rows remain open.
- Do not let dashboard state disappear from architecture maps because it is "only projection"; projection drift is one of the workflow gaps Prismatic is trying to eliminate.
- When an independent reviewer returns `BLOCKED`, repair on a new exact head and request a fresh exact-head re-review. Do not reuse a stale `CLEAN`/`BLOCKED` judgment against a different commit/tree.

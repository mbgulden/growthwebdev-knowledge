# Exact executable Linear packet drafting

Use this reference after Michael approves a planning/relation architecture and explicitly authorizes drafting an executable Linear packet, but does **not** authorize Linear writes.

## Boundary

- Draft only; do not mutate Linear.
- Treat read-only exports as current-source evidence only for their timestamp/hash; include drift guards before any future write.
- Keep read-only exporters mutation-free. Do not add mutation code to the broker/exporter.
- Separate these scopes in reports: planning approval, read-only inspection authorization, executable-packet drafting, mutation authorization, and actual write execution.

## Required packet fields

For every touched issue include:

- identifier and Linear UUID if available;
- current title/state/labels/parent/relations/`updatedAt` from the export;
- action: `unchanged`, `patch`, `supersede`, `reparent`, `rewrite`, `create`, or `hold`;
- full final title when changed;
- full replacement description when changed;
- exact label add/remove set;
- exact state delta, with no closure unless explicitly authorized and state IDs are known;
- exact parent delta;
- exact relation additions/removals;
- per-issue drift guard on `updatedAt` plus packet-wide export hash guard;
- rollback/non-claims.

## Relation discipline

- Start from live relation baselines, not prose dependency notes embedded in descriptions.
- Prefer minimal direct `blockedBy` edges.
- Omit redundant transitive edges; if `C blockedBy B` and `B blockedBy A`, do not also add `C blockedBy A` unless there is a separate direct gate.
- Do not materialize malformed or cumulative prose chains as Linear relations.
- Preserve independently useful sibling tasks even if they initially appeared duplicative.

## Codex-family dedupe pattern

When `GRO-4304`/`GRO-4314`-`GRO-4316` already exists as a stale Codex epic family:

- do not create another Codex epic;
- supersede or hold the duplicate parent rather than reusing it as the canonical parent if another approved parent owns the lane;
- reparent useful children into the approved architecture instead of repurposing unrelated siblings;
- rewrite Codex work in the canonical harness path, not as Hermes-style persona files such as `SOUL.md`;
- keep `agent:codex` disabled or not dispatch-ready until capability/auth/cap-1 gates pass;
- minimal initial Codex chain is `Codex 02 blockedBy Codex 01`, then `Codex 03 blockedBy Codex 02`.

## Verification before asking for mutation approval

1. Freeze the packet to a mode-600 file if it contains full descriptions.
2. Compute and report SHA256 for packet and source exports.
3. Run local structural checks: every referenced issue exists or is explicitly marked `create`; no cycles; no redundant transitive edges; no relation to superseded-only nodes unless intentional; every changed issue has complete replacement payload.
4. Dispatch independent exact-hash review and require `CLEAN` before presenting mutation execution as ready.
5. If execution is authorized later, switch to the fail-closed writer pattern in `references/fail-closed-linear-writer.md`; do not mutate from the drafting/export scripts.

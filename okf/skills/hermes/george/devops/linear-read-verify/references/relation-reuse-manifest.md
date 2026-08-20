# Linear relation/reuse manifest pattern

Use this pattern when Michael asks for a proposed Linear relationship manifest after a bounded read-only export of parent/child issues.

## Trigger

- A Prismatic planning/export pass has current parent/child Linear descriptions, labels, and relation arrays.
- The next step is approval for dedupe, supersession, issue reuse, or `blockedBy` edges.
- Existing issues may be stale, duplicated, or described with prose dependency fields that are not live Linear relations.

## Workflow

1. **Start from the live export, not session memory.** Bind the manifest to the exact export path/hash, mode, allowlist, and `read_only=true` result.
2. **State the relation baseline first.** Count current parent relations and child relations. If relation arrays are empty, say there are no live edges to remove; do not treat prose `depends_on_siblings` fields as actual Linear relations.
3. **Classify every existing child before proposing new work.** Use dispositions such as:
   - `REUSE / PATCH`
   - `SUPERSede / already-present audit`
   - `HOLD / proposed cancel-supersede`
   - `CONSOLIDATE / SUPERSEDE INTO <issue>`
   - `REWRITE AS <new scope>`
4. **Prefer reuse over create.** If an existing issue family appears elsewhere but was outside the approved export, do not create duplicates. Propose a separately approved exact read before reparenting or patching.
5. **Separate issue text repair from relations.** Patch stale paths, authority claims, task names, parent umbrella wording, and dispatch readiness before adding edges. When parent/child descriptions encode bad dependency prose, repair the prose; do not copy the malformed prose into relation edges.
6. **Add only minimal direct relation edges.** Avoid redundant transitive edges. Use `blockedBy` only where the blocked issue truly cannot proceed without the prerequisite. If exact descriptions show a better candidate-level graph than the titles suggested, update the manifest before asking for approval.
7. **Call out superseded issues with no relation edge.** A superseded or consolidated task usually receives description/status repair, not new dependency edges.
8. **Include operational holds.** If a task implies mutation of cron, deletion, database cleanup, profile deletion, login, merge, deploy, or writer-cap increase, mark it out of scope until separately approved.
9. **End with a pre-write guard and write order.** Include: name one writer, remove `dispatch:ready` from rewritten/superseded issues, patch descriptions first, re-read content, add relations, re-read both ends/directions, and report receipt/non-claims.
10. **Get independent review of the exact manifest hash before asking for execution approval.** Do not ask Michael to approve mutations while review is still pending unless he explicitly asks for a provisional packet.

## Manifest sections

A good manifest includes:

```text
status / approval boundary
source export path + sha256 + read-only statement
current relation baseline
pre-write guard
per-parent issue action table
proposed direct relation operations table
missing/unresolved candidates
write order after approval
non-claims
```

## Pitfalls

- Do not add relation edges from prose dependency text without verifying current Linear relation arrays.
- Do not infer final reuse/cancel/create decisions from titles alone when exact descriptions are available; exact description review can flip dispositions.
- Do not cancel or repurpose a sibling merely because it is adjacent to stale work; preserve independently useful lanes unless exact implementation proof or scope overlap disproves them.
- Do not create a new issue when an existing sibling can be reparented and fully rewritten under the corrected parent.
- Do not materialize cumulative dependency chains from existing descriptions; use a corrected minimal candidate-level graph.
- Do not create new children for an existing issue family that was merely outside the current allowlist.
- Do not treat a stale task description as approval for implementation; classify and repair it first.
- Do not let `dispatch:ready` remain on issues being rewritten, superseded, or held.
- Do not add direct Linear-write capability to read-only exporters; prepare a separate write packet and approval scope.
- Do not ask for execution approval until exact-hash independent review is CLEAN, unless the user explicitly requests a provisional approval choice.

# Zero-Trust Architecture Audit Docs

Use this reference when Michael asks for a Prismatic setup / zero-trust / George operations audit intended for another AI or external reviewer.

## Trigger

- Requests for a hyper-detailed `.md` explaining the Prismatic setup, zero-trust posture, George's role, branches/worktrees/workspaces/releases, or how to move forward.
- Requests where the deliverable is a shareable architecture review rather than an implementation prompt.

## Pattern that worked

1. **Treat it as an evidence-bound audit, not a narrative recap.** Inspect live state where available: handoff, control clone, worktrees, systemd runtime, release paths, SQLite counts, dashboard/API behavior, provider-neutral receipt state, and relevant docs/contracts.
2. **Lead with status and boundary.** Use `PASS / PARTIAL / BLOCKED`; for mixed architecture reviews, call out security blockers first before strengths.
3. **Separate design direction from operational adoption.** In the 2026-07-30 audit, the exact tuple/outbox/cap-one/release/receipt design was strong, but provider-neutral receipts were not yet the operational merge authority.
4. **Map all overloaded nouns.** For “workspace,” distinguish registered dashboard workspace, task checkout, immutable release artifact, and coordination artifact store. Do not let one filesystem scanner define all of them.
5. **Name what George does and should not own.** George coordinates intent/contracts/reviews/evidence/sequencing; the Engine should eventually own deterministic state transitions, launch, reconciliation, receipt validation, and dashboard projection.
6. **Surface public-read confidentiality issues as first-class zero-trust failures.** A read-only unauthenticated route can be critical if it exposes paths, workspaces, receipts, logs, or previewable files.
7. **Preserve product-surface continuity.** For dashboard defects, recommend replacing unsafe adapters/boundaries while preserving the existing good Hub shell and deep-link UX.
8. **Include a migration plan with exit markers.** Prefer phase markers such as `WORKSPACE_API_PUBLIC_CONFIDENTIALITY_BOUNDARY_OK` and `SIGNED_PROVIDER_NEUTRAL_MERGE_AUTHORITY_OK` over vague next steps.
9. **Write for a future reviewer.** Include explicit questions for the next AI reviewer and non-claims so the reviewer does not infer merge/deploy/test authorization.
10. **Verify the document as an artifact.** Run a lightweight verifier for required sections, evidence markers, balanced fences, no placeholders, size/line/word counts, and no post-verifier mutation. Report the verifier log path and SHA-256.

## Useful output shape

```text
STATUS=<PASS|PARTIAL|BLOCKED>
EVIDENCE=<key live proof bullets>
BOUNDARY=<not claimed>
REPORT=<absolute .md path>
SHA256=<report digest>
NEXT=<exact next architectural/security action>
MARKER=<audit marker>
```

## Pitfalls

- Do not turn the audit into a long flat task history. Capture the architecture class and cite current tasks only as examples with exact non-claims.
- Do not publish raw secrets, tokens, credential paths with sensitive contents, or private file contents. Route behavior and source inspection can be enough to classify exposure.
- Do not let a successful current task obscure unrelated P0 architecture/security blockers.
- Do not recommend deleting branches/worktrees/refs as cleanup unless Michael explicitly authorizes deletion; classify first.
- Do not claim “zero trust” as complete when public GET routes, manual profile launchers, stale runtime pointers, or non-canonical receipts remain.

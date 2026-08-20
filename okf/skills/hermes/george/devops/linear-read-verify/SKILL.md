---
name: linear-read-verify
description: Read and verify bounded Linear issue metadata from George's profile without arbitrary GraphQL, credential exposure, or mutation capability.
---

# Linear Read/Verify

Use this skill when coordinating Prismatic work that requires current Linear issue state, ownership, labels, project, or timestamps.

## Default policy

- Read-only by construction.
- Inspect the original Linear source before relying on session history or local handoffs.
- Never print or copy the profile credential.
- Do not add comments, change state, assign users, or mutate issues through this workflow.
- Linear writes remain separately gated by explicit Michael authorization.

## Commands

Default metadata broker:

```bash
/home/ubuntu/.hermes/profiles/george/scripts/linear_read_verify.py GRO-4210
```

The command accepts only canonical `TEAM-123` issue identifiers and returns bounded JSON fields:

- issue ID and identifier;
- title and URL;
- state/type;
- team, project, and assignee;
- labels;
- created/updated/completed/canceled timestamps;
- `read_only: true`.

It does not accept arbitrary GraphQL and contains no mutation query.

When the default broker is insufficient because the approved review needs descriptions, bounded children, labels, or relations, use the separate allowlisted-exporter pattern in `references/allowlisted-linear-exporter.md`: hardcode the approved parent IDs, keep the query read-only and bounded, fail closed on pagination/over-limit arrays, redact before truncation, suppress exception text in public output, recursively strip the exact loaded credential from normalized output, adversarially test quoted-key credential forms, and get exact-hash local tests plus independent CLEAN review before live credential use.

For label/state existence and dispatch-owner proof, see `references/linear-pagination-owner-labels.md`: explicit `first:100` plus `pageInfo.hasNextPage` is mandatory; never treat a default Linear collection page as exhaustive.

## Verification

Require:

```text
EXIT_CODE=0
ok=true
issue.identifier=<requested identifier>
issue.read_only=true
```

If Linear is unavailable, report the bounded error and do not substitute session history as proof of current Linear state.

## Allowlisted description/relation export

When Michael explicitly authorizes a read-only child-description/relation dedupe for the PE foundational parents, use the separate reviewed exporter rather than extending the general metadata broker:

```bash
umask 077
mkdir -p /absolute/restricted
python3 /home/ubuntu/.hermes/profiles/george/scripts/linear_read_export_allowlisted.py --parent GRO-4263 > /absolute/restricted/output.json
chmod 600 /absolute/restricted/output.json
```

Use `--all` only when all approved parents are in scope. Current fixed allowlist: `GRO-4262`, `GRO-4263`, `GRO-4264`, and the Codex-family parent `GRO-4304` when Michael explicitly authorizes Codex-family read-only inspection. The exporter accepts only approved allowlisted parents or `--all`, uses one fixed GraphQL query, and has no mutation/subscription operation. It returns parent/child descriptions, exact parent links, and incoming/outgoing issue relations. Its output is normalized; labels are strings and children are lists, not raw GraphQL connection objects. See `references/allowlisted-linear-exporter-normalized-output.md`.

If the next child in the audited sequence is `Todo` but its description/labels impose an operational hold such as `not dispatch-ready`, keep the work read-only: freeze a discovery/precontract artifact with all event/source/key/producer booleans false, record predecessor blockers, and do not admit a producer or manufacture a replacement Linear task from chat/session history.

Before live use:

1. Run `python3 -m py_compile` on exporter and tests.
2. Run `/home/ubuntu/.hermes/profiles/george/scripts/tests/test_linear_read_export_allowlisted.py` through unittest.
3. Bind independent review to exact script/test hashes.
4. Require `CLEAN`; do not use live credentials on `BLOCKED`.
5. Redirect stdout directly to a mode-600 file; do not let full descriptions flood chat/tool output.
6. Validate `ok=true`, `read_only=true`, exact allowlist/parent identifiers, output hash, and file mode using a compact summary.
7. Consume the normalized schema correctly: `parent.children` is a list, `issue.labels` are strings, and `issue.state` is the bounded state object. Do not assume raw GraphQL edge/node shapes or label dictionaries.
8. If redirection or CLI argument validation fails before the request, treat the empty/partial output file as non-evidence, create the restricted directory or fix the CLI shape, and rerun.

Security pitfalls learned during review (see `references/allowlisted-linear-exporter-security-review-2026-07.md` for the concrete truncation-boundary and redirect-handler test recipes):

- Never print raw exception text; transport exceptions can embed authorization headers.
- Explicitly bound labels, children, and both relation directions; reject pagination and over-limit arrays rather than silently truncating.
- For Linear collection reads used as existence/absence/owner proof, always request an explicit bounded page size (for example `first:100`) and inspect `pageInfo.hasNextPage`; default `team.labels`/state pages are not exhaustive. Do not conclude that labels such as `agent:agy` are missing from a default page or any paginated result with `hasNextPage=true`; rerun an exhaustive bounded query or fail closed.
- Apply the same rule to nested readback collections inside exact issue lookups: `labels`, `relations`, `children`, and similar connections must be explicitly bounded and `hasNextPage=false` before exact comparison or postcondition claims.
- Bind owner/label findings by both exact name and Linear ID in the proof packet before using them in a writer.
- Build the HTTP client with redirects disabled. Python's default `urllib.request.urlopen()` redirect handling may preserve `Authorization` across 301/302/303 redirects, including cross-origin redirects. Install a rejecting `HTTPRedirectHandler` and fail before any follow-up request is constructed; do not rely on checking the final response URL. Test offline with a sentinel credential and verify the CLI emits only its generic suppressed error.
- Redact before truncation. This includes two separate passes: generic secret-pattern redaction and recursive replacement of the exact loaded credential on the raw bounded response **before** normalization/field truncation. A post-normalization exact-secret pass is defense in depth only; by itself it can miss a credential prefix cut at the truncation boundary. Test an unpatterned exact credential crossing `MAX_DESCRIPTION_CHARS` and reject both the full value and a meaningful prefix.
- Handle quoted keys/values, backticks, compound names such as `AWS_SECRET_ACCESS_KEY`, JWT/API-key/private-key patterns, and recursively strip the exact loaded credential from normalized output.
- The fixed query's schema plausibility is not live-schema proof; first live use remains a bounded read-only canary.

## Ad-hoc Linear reads (portable CLI)

For quick unstructured lookups (text search, recent-issue sweeps, one-off
bounded GraphQL), use the portable CLI:
`/home/ubuntu/gro4270-clean-review-q6H2L5/portable-skills/linear/scripts/linear_api.py`
(stdlib only). Auth: `LINEAR_API_KEY` env from `/home/ubuntu/.linear_api_key` —
read the file, never inline the literal; if the shell redactor mangles
`$(cat ...)`, use the `execute_code` env-dict route (see
`bearer-token-via-shell-substitution`).

Commands: `whoami`, `list-teams`, `list-projects [--team]`, `list-states`,
`list-issues [--team --status --assignee --label --limit]`,
`get-issue GRO-123`, `search-issues <query>`, `raw <graphql_query>`.
Keep `raw` queries read-only and bounded (`first: N` + check `hasNextPage`).

GraphQL filter pitfalls (verified live 2026-08-19):

- `IssueFilter` has **no** `q` field — text search is the
  `search-issues` command, not `filter: {q: "..."}` (HTTP 400
  `Field "q" is not defined by type "IssueFilter"`).
- Time filters use `createdAt: {gt: "2026-08-18T00:00:00.000Z"}` —
  the field is `createdAt`, not `created`.
- `raw` output is top-level JSON `{"issues": {"nodes": [...]}}` —
  **no** `data` wrapper. `search-issues` output is a top-level **list**,
  not a dict — branch on `isinstance(d, list)` before `.get()`.
- `assignee { name }` comes back `null` when unassigned — guard with
  `(n.get("assignee") or {}).get("name")`.

## Relation/reuse manifest before writes

When a bounded read-only export is used to prepare issue reuse, supersession, dedupe, or dependency edges, produce a proposed relation/reuse manifest before any write. See `references/relation-reuse-manifest.md`.

After Michael approves the planning architecture and authorizes drafting an exact executable packet without writes, follow `references/executable-packet-drafting.md`: include full replacement payloads, label/state/parent/relation deltas, drift guards, minimal direct relations, and independent exact-hash review before asking for mutation approval.

After Michael explicitly authorizes execution of a specific mutation packet, follow `references/fail-closed-linear-writer.md`: keep write code separate from read-only brokers, bind every review to exact SHA256, prove or reject client-supplied IDs before relying on them, record durable intents before forward and rollback mutations, run failure-injection proof, and require independent `CLEAN` on the current exact writer SHA before live writes. If Linear rejects a deterministic issue-ID create but reconciliation proves no issue exists, use `references/linear-server-generated-issue-create-fallback.md` to build a fresh server-ID writer with packet-correlation receipts and exact-title/equivalent idempotency.

Exception for final bookkeeping after exact-head acceptance: when standing or explicit authorization covers `mark this accepted issue Done`, independent exact-head review is `CLEAN/PASS`, and the only mutation is one target issue's `stateId`, use `references/single-issue-state-transition-after-acceptance.md` instead of creating a new broad writer/precontract loop. Still require live baseline, exact-head guard, durable intent receipt, one mutation, readback reconciliation, receipt hash, and strict non-claims. If the live baseline already shows the intended final state, do not send a redundant mutation; reconcile with a read-only receipt using `references/no-op-state-reconciliation-after-merge.md`.

For parent-completion runs where child issues are explicitly superseded by their current Linear descriptions, do **not** use the `Done` shortcut and do not bulk-close the family. Use `references/superseded-child-state-reconciliation.md`: classify every child, prove replacement/transferred acceptance, freeze a non-executable stateId-only canceled/superseded packet, require a dedicated one-issue writer rather than repurposing old multi-issue executors, require local dry-run/failure-injection plus independent exact-hash review, then mutate one issue at a time with durable intents and readback receipts.

If an authorized writer fails a byte-exact postcondition because Linear canonicalized stored Markdown (for example `\n- ` list markers stored as `\n* `), or because Linear's read-after-write view converges after the immediate post-update check, use `references/linear-markdown-normalization-recovery.md`: classify exact residual drift from live Linear, guard the normalized/converged live state with pinned hashes, restore only baseline residual fields, verify projections/absence conditions, and require dry-run + independent exact-SHA review before any recovery mutation. If retrying the original frozen packet from a recovered/quarantined state, freeze and hash-bind a separate post-recovery retry baseline plus the source PASS recovery receipt; do not reuse stale before-guards or restore dispatch without separate authorization.

Key requirements:

- bind the manifest to the exact export path/hash and `read_only=true` evidence;
- state the live relation baseline separately from prose dependency fields in descriptions;
- classify every existing child as reuse/patch, supersede, hold, consolidate, or rewrite before proposing new issues;
- prefer exact read/reparent proposals over duplicate creation when an issue family already appears elsewhere but was outside the approved export;
- remove `dispatch:ready` from rewritten/superseded issues before patching descriptions or adding relations;
- propose only minimal direct `blockedBy` edges and omit redundant transitive edges;
- get exact-hash independent review before asking for mutation approval unless Michael explicitly requests a provisional choice;
- when reviewers have access to exact descriptions, reconcile their findings before approval: preserve independently useful siblings, create only genuinely missing candidates, and do not materialize cumulative/malformed prose dependency chains as Linear edges. See `references/pe-foundational-relation-review-2026-07.md` for the PE foundational example.
- for Prismatic Codex work, treat `codex` as the installed Codex CLI behind PE's canonical `AgentHarness`, never as a Hermes profile: reject `SOUL.md`/profile-shaped scope, Hermes credential copying, Hermes profile dispatch, and second launcher/queue/state-store designs; keep the PE `codex-cli` registry entry disabled until dedicated-HOME authentication, exact clean-worktree cap-1 canary, durable receipts, cleanup, and recovery proof pass.

## Write boundary

If Michael explicitly authorizes a Linear mutation, stop using these read-only brokers. Prepare the exact proposed mutation, target identifier, expected state transition, relation changes, and rollback/non-claims for separate approval/execution. Do not add mutation support to either read-only script.

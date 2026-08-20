---
name: linear-handoff-build-out
description: Produce an OKF handoff bundle + Linear epic tree (parent + child epics + child tasks) so any agent (or human) can pick up a feature cold. Enforces seven-field descriptions (or eight-field for multi-agent pickup), owner labels, acceptance test IDs, distributed-execution headers, and cold-start HANDOFF.md.
tags: [handoff, linear, okf, epic, parent, child, owner, acceptance-test, multi-agent, distributed-execution]
---

# Linear Handoff Build-Out

Use this skill when a feature needs a Linear epic + OKF docs a fresh agent can pick up cold without prior context.

## When to use

- A new feature has been approved and needs an OKF bundle + Linear tree.
- A Linear epic exists but is missing owner labels, first steps, or acceptance tests.
- A handoff is needed (different agent, contractor, or future self in 6 months).
- A feature's plan surfaces **gaps in the platform the feature depends on** — audit first, build the gap-closure epic, *then* the feature epic. See `references/platform-gap-audit.md`.
- A Linear epic will be picked up by 2+ agents in parallel or sequence — see `references/distributed-execution-header.md`.

## Required OKF bundle

For a feature at `okf/projects/<project-slug>/`, produce **all** of:

| File | Required content |
|---|---|
| `index.md` | Project hub: parent epic goal + exit criterion, child epic table with **owner + first step columns**, full task inventory with rubric reference, sequencing, decisions/risks/standards pointers. |
| `HANDOFF.md` | Cold-start path: 5-step recipe (or 8-step when cross-project dependencies exist) with concrete commands, read order, first concrete action, stop conditions, owners, conventions not to break. |
| `decisions/NNN-<slug>.md` | One ADR per major decision. Each must carry **Owner** + **Acceptance Test IDs** sections. |
| `risks/<slug>.md` | Risk register with named owners (Michael, George, etc.) + **observable signal** per risk. |
| `standards/<slug>.md` (if class-level) | Binding requirements with stable test IDs. |

Link the project from `okf/index.md` and `okf/projects/index.md` in the same change.

## Required Linear tree

### Parent epic
- Title: `<FEATURE> — <one-line goal>`
- State: `Todo` (unstarted)
- Description: parent exit criterion + rubric definition + sequencing + OKF pointers
- Labels: `agent:<owner>`, `dispatch:ready`, `type:feature`

### Child epics (N)
- Title: `<FEATURE>-<EPIC_SLUG> — <one-line goal>`
- `parentId`: parent UUID
- Description: parent exit criterion + epic exit criterion + first step + rubric + target path + acceptance tests + plan reference (all seven fields)
- Labels: `agent:<owner>`, `dispatch:ready`, `type:epic`

### Child tasks (M per epic)
- Title: `[<FEATURE>-<EPIC_SLUG>-NN] <action verb + object>` (zero-padded 2-digit)
- `parentId`: child epic UUID
- Description: parent exit criterion + epic exit criterion + first step + rubric + target path + acceptance tests + plan reference + **Distributed-Execution Header** (see `references/distributed-execution-header.md`).
- Labels: `agent:<owner>`, `dispatch:ready`, `type:task`, `agent:peer-review-blocked`

## Seven-field description shape (verbatim order)

1. **PARENT EXIT CRITERION (verbatim):** copy from parent epic.
2. **EPIC EXIT CRITERION (verbatim):** copy from parent epic.
3. **FIRST STEP:** 1-3 concrete actions an agent can perform in <15 min.
4. **RUBRIC:** four bullets (Unit / Integration / Revenue / Assumption).
5. **TARGET PATH:** repo-relative file path where the work lands.
6. **ACCEPTANCE TESTS:** list of test IDs that prove the exit criterion.
7. **PLAN REFERENCE:** `okf/projects/<project-slug>/index.md` (+ HANDOFF.md).

## Eight-field description shape (for multi-agent pickup)

When 2+ agents may pick up tasks from the same epic tree (the default), add an **eighth field**:

8. **DISTRIBUTED EXECUTION HEADER** — at minimum `depends_on_siblings`, `blocks`, `branch_slug`, `swarm_locks`, `pytest_command`, `evidence_comment_template`, `pickup_signal`, `review_signal`. See `references/distributed-execution-header.md` for the full spec.

Without field 8, parallel/sequential pickup is silent: agents don't know which siblings to ship together, which files need a swarm lock first, or which pytest line proves the slice. Default to eight-field whenever the epic is large enough that 2+ agents might pick up tasks in parallel.

## Acceptance-test ID convention

Stable IDs in three flavors:

- `<FEATURE>-TEST-<EPIC_SLUG>-NN` — unit/integration tests.
- `<FEATURE>-PERF-<EPIC_SLUG>-NN` — performance budget tests.
- `<FEATURE>-NEG-<EPIC_SLUG>-NN` — negative tests (Done rejected without evidence, etc.).

Renames require a new ID + redirect note in `decisions/`.

## Owner / routing labels

Use the existing PE convention (do not introduce new labels without an ADR):

- `agent:fred` / `agent:ned` / `agent:kai` / `agent:agy` / `agent:jules` / `agent:george`
- `dispatch:ready` / `dispatch:blocked` / `dispatch:paused` / `dispatch:priority` / `dispatch:phase-priority`
- `agent:needs-human-review` (paired with `dispatch:blocked` when waiting on Michael)
- `type:feature` / `type:epic` / `type:task` / `type:docs` / `type:research`

## Distributed-execution labels

For multi-agent pickup (the default), every child task also carries:

- `agent:in-progress` — claimed by an agent, actively being worked. Other agents must not pick it up. Add atomically before reading source code; remove before handoff.
- `agent:peer-review-blocked` — task cannot move to `Done` without explicit peer-review approval. Always present on tasks touching shared code paths. Set during the build-out, removed only by the reviewer.

### Recommended task lifecycle

```
Todo  --(agent picks up + sets agent:in-progress)-->  In Progress
In Progress  --(evidence posted)-->  In Review  (label: agent:peer-review-blocked stays)
In Review  --(peer approves)-->  Done
In Review  --(peer rejects)-->  In Progress  (label: agent:peer-review-blocked stays)
In Progress  --(blocked)-->  Todo  (label: dispatch:blocked + agent:needs-human-review)
```

### Claim protocol (every pickup agent must follow)

1. Run `gh issue view GRO-XXXX --json labels` (or GraphQL) to confirm `agent:in-progress` is **not** present.
2. If clear, atomically add `agent:in-progress` via `issueUpdate` **before** reading any source code.
3. If the task is already `agent:in-progress`, post a comment asking for status and move to a different task in the same epic.
4. After pickup: acquire swarm lock for every file in `TARGET PATH`, open branch per lane convention with slug from the Distributed-Execution Header, implement, test, post evidence, request review.
5. Move to `In Review` (do NOT self-approve to `Done`).

### Handoff protocol (when pausing)

1. Post a comment with: current state, what works, what's pending, files touched, branch name.
2. Add `agent:needs-human-review`.
3. Remove `agent:in-progress` (so another agent can pick up).
4. Do **not** delete the feature branch.

## HANDOFF.md shape

```markdown
# <Project Name> — Handoff

## 1. What is this?
<one paragraph: goal + exit criterion verbatim>

## 2. Where does the work live?
- Code paths (repo-relative)
- OKF docs (paths)
- Linear epic + epics + tasks (IDs and titles)

## 3. Read order (cold start, ~10 minutes)
1. <doc/command>
2. <doc/command>
3. ...

## 4. First concrete action
<1-3 imperative bullets that produce a verifiable artifact>

## 5. Stop conditions
- <what blocks progress and who to escalate to>
- <what "Done" means, with the exit criterion verbatim>

## 6. Owners
| Role | Name |

## 7. Conventions not to break
<lane / branch / commit / lock rules>

## 8. Cross-project dependencies (only when applicable)
- This project unblocks <other-project-id>: <which tasks>.
- <other-project-id> depends on this: <which artifacts>.
```

## Verification gate

Before declaring the build-out complete, run a verifier that checks:

- All required OKF files exist with valid frontmatter.
- `git_path` matches **repo-relative** file location (the durable form), not OKF-relative.
- All `okf/...` Markdown links resolve.
- No forbidden credential markers (`sk_live_`, `sk_test_`, `ghp_`, `github_pat_`, `xoxb-`, `xoxp-`, `Bearer sk-`) — even as observable-signal prose, even inside backticks. Use category wording: "known GitHub-style credential pattern (raw prefix intentionally withheld)".
- Each decision has `## Owner` + `## Acceptance Test IDs`.
- Risk register has named owners + observable signal per risk.
- Linear readback: 1 parent + N epics + M tasks, all in `Todo`, all labeled.
- Every child task description contains all seven fields (or all eight for multi-agent).
- HANDOFF.md exists with the right sections.
- Every child task carries `agent:peer-review-blocked`.
- Every child task description contains the Distributed-Execution Header fields (when applicable).

Report as **ad hoc targeted verification, not suite green.**

## Pitfalls

- Do not introduce new labels without an ADR — PE has a routing convention; respect it.
- Do not put a literal credential prefix (e.g. `ghp_`) inside an OKF artifact even as a "what to watch for" example. Use category wording: "known GitHub-style credential pattern (raw prefix intentionally withheld)".
- Do not skip the seven-field description shape; tasks shorter than the standard are non-conformant.
- Do not assume the parent exit criterion is obvious — copy it verbatim into every child description.
- Don't put the same `agent:` label on every task — match the owner per task. A bulk label copy from the parent epic silently misroutes work to the wrong lane. Verify each child's label set against the per-task owner map before declaring the build-out done.
- Do not run Linear mutations without first verifying with a dry-run lookup (state UUIDs, label UUIDs).
- Do not call the build-out complete until both OKF verifier and Linear readback pass.
- When loading the Linear API key from a dotenv file, never print the value; audit log only the first 12 chars.
- Frame the first-draft task count as a **plan ceiling**, not a commitment. If a reviewer (George-style) is reviewing in parallel, the final count may compress. Phrase as "up to N candidate slices, not Fred's 29-task tree. This is not an approved task count." See `plan-reconciliation-after-peer-review`.
- Do not pause for re-approval between OKF docs and Linear mutation — one approval covers both. The OKF docs ARE the plan. See `okf-documentation-ops` §16.
- If a child task needs to dispatch to an external CLI (Codex CLI, AGY CLI), the lane description must reference that CLI's argv/service-HOME/cap-1 contract, not a Hermes profile shape. See `codex-cli-integration`.
- Do not pause for re-approval between OKF docs and Linear mutation — one approval covers both. The OKF docs ARE the plan. See `okf-documentation-ops` §16.
- Do not assume `parentId` accepts an identifier like `GRO-4214` — it requires the issue's UUID. Walk the tree first; capture `{identifier: uuid}` for every epic.
- Do not assume multi-line description bodies work — Linear returns HTTP 400. Build descriptions as a single Python string with `\n` escapes.
- Do not skip the post-batch readback — the live GraphQL response is the source of truth. Compare it against the build-out plan; if anything is missing, patch and re-run, do not declare done.
- Don't build a feature epic when the platform audit reveals blocking gaps — make the gap-closure project its own parent epic and sequence it BEFORE the feature epic. See `references/platform-gap-audit.md`.
- Don't invent new labels for a gap-closure epic; the existing PE agent/dispatch/type label set is sufficient (verify with `issueLabels(first: 100)` before declaring a new label needed).
- When two projects depend on each other (e.g., a gap-closure epic unblocking a feature epic), put the dependency in **both** directions: the gap-closure task description's `ACCEPTANCE TESTS` field names the feature task it unblocks; the feature task description names the gap-closure artifact (e.g., `pe/journal/cron/` package) it depends on. One-way references leave the dependency invisible from the other side of the tree.
- Don't claim a build-out is "done" without an audit pass first — claim-based completion is a recurring failure mode. Always run the verifier BEFORE reporting status; if the user asks "is this enough?", treat that as a signal to re-audit, not to defend.
- Don't ship a 7-field description shape when 2+ agents will pick up tasks from the epic. Default to 8-field with the Distributed-Execution Header. Without it, parallel/sequential pickup is silent and agents collide.
- Don't assume the verifier will get its conventions right on the first try. Verifier bugs are a real failure mode: `git_path` was repo-relative (not OKF-relative) in my first pass; section-heading patterns (e.g., `### 2.1` vs `§2.1`) must match what you actually wrote. Run the verifier, see the failures, fix the *right* layer (often the verifier, not the doc).
- Don't put forbidden-marker strings into an OKF artifact even as documentation of what to watch for. The verifier is literal. Use category wording.
- Don't pre-assume Linear identifiers in the build-out plan.** Linear's auto-numbering is sequential and gap-filling per workspace, not locally gap-resumable. When the build-out plan names `GRO-4373, GRO-4374, ...` as expected identifiers for the new tasks, those numbers may already be consumed by other work (Zapier infra, peer reviews, etc.). Plan by **child epics/tasks** (titles, descriptions, parent linkage, labels) and read back the live `identifier` from each `issueCreate` response. Treat the assigned identifier as a post-create fact, not a pre-create assumption. The post-batch readback (gotcha #9) is the truth source.

- **Audit for in-flight overlapping work BEFORE creating the epic tree.** A `issues(filter: {team, orderBy: createdAt desc}, first: 20)` query against the target team catches mid-flight epics whose titles/scope overlap with the proposed build-out. Worked example 2026-08-05: a planned `PRISMATIC_PROMOTE_V0_2` epic for `bin/prismatic-promote` would have created 10 duplicate child issues when `[PE-PHASE-B-0]` through `[PE-PHASE-B-4]` (GRO-4495–GRO-4499) already existed with overlapping scope but different design philosophy. The right resolution was the **hybrid path**: create the parent epic as the contract/spec reference, link the existing in-flight issues as `depends_on` from the new children, and only create new issue numbers for genuinely-new work. Three concrete rules: (1) every epic build-out starts with `issues(filter: {team, first: 20, orderBy: createdAt desc})` against the target team; (2) titles matching the proposed epic's `[<FEATURE>-<SLUG>-N]` pattern are flagged as potential overlaps; (3) when overlap is found, surface it to the user as a multi-choice decision (a/b/c hybrid) before any `issueCreate` call. Duplicating an in-flight epic silently breaks routing, label invariants, and dispatch state — a 10-line audit is cheaper than 10 issue merges.
- **Don't trust the `agent:*` label for pickup eligibility — the Distributed-Execution Header (field 8) carries the true ownership.** An `agent:fred` label is the entry-point convention, not lane ownership. A task labeled `agent:fred` with `branch_slug: ned/pe-workflow-...` and `swarm_locks: ['workspace-global']` is **Ned's lane** despite the label. Authoritative signals, in priority order: (1) `branch_slug` prefix (matches your lane's prefix), (2) `swarm_locks` paths (acquire before editing), (3) `review_signal` (which gate closes the task), (4) `agent:*` label — never label alone. Tested 2026-07-31: 3 PE-WORKFLOW-* tasks had `agent:fred` labels but Ned's branch_slug + swarm_locks. The label was the trap. The pickup agent must read field 8 in the description before claiming. See `references/linear-api-gotchas.md` gotcha #13 for the full rule.

- **For handoffs where the build owner consolidates the whole work on one laptop (Antigravity 2.0), pair the Linear tree with an OKF Context Pack section.** When Michael consolidates a multi-lane build on his laptop via Antigravity (full AGY visibility, single host), the OKF and the Linear tree serve different audiences: the Context Pack section is the builder's reference (file paths, APIs, SHAs, anti-patterns, acceptance markers), the Linear tree is the reviewer's reference (tasks, descriptions, owner labels). Both must carry the same ownership map, acceptance markers, and verification commands. See `okf-documentation-ops/references/okf-context-pack-for-ai-build-agents-2026-07-31.md` for the Context Pack shape. Worked example: Review/Merge Factory V1 OKF §16 (12 subsections, 25 verified paths) + the proposed GRO-RF-V1 + 12 child tasks tree.

## References

- `references/linear-api-gotchas.md` — session-level Linear GraphQL API quirks: state-is-UUID, label-name-to-UUID resolution, multi-line description bodies cause 400, rate-limit retry pattern, dotenv load inside `execute_code`, `parentId` is the UUID not the identifier, audit-prefix credential logging, and the dry-run-then-mutate-then-readback order. Plus #14 (self-hosted "portability" build drifts from cloud schema — introspect first: `issue(identifier:)` unsupported, `NumberComparator` is Float, capitalized sort enums) and #16 (verify the hosted review-link surface end-to-end before promising it — the canonical deep link is `/workspaces?file=<rel-path>` where the server resolves the owning workspace; `invalid workspace identifier` is usually your own hand-typed `workspace_id` typo, not a gateway bug; tarball+SHA in Linear is the always-works fallback; supersede SHAs with explicit 📌 FINAL comments when the packet changes).
- `references/review-packet-shape.md` — sender-side recipe for a reviewer-ready REVIEW_PACKET.md: the 10-section shape (§1 paths → §2 attestation table → §3 re-runnable recipes with mutating steps marked → §5 partials-first caveats → §6 out-of-scope → §7 ad-hoc sender-verification log), self-consistent N/N counts, the SHA-supersede + 📌 FINAL comment discipline, and the delivery checklist (tarball, fresh-extract diff, N/N verifier, Linear comment).
- `references/platform-gap-audit.md` — pre-feature dependency closure pattern: surface inventory → blocking/needs-fill/later classification → gap-closure project on top → feature epic on top of that. When a feature surfaces platform gaps, audit first, build a separate parent epic, sequence gap-closure before the feature.
- `references/distributed-execution-header.md` — field 8 spec for multi-agent task pickup: `depends_on_siblings`, `blocks`, `branch_slug`, `swarm_locks`, `pytest_command`, `evidence_comment_template`, `pickup_signal`, `review_signal`. Plus the claim protocol, handoff protocol, and the `agent:in-progress` + `agent:peer-review-blocked` lifecycle.
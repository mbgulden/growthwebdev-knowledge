# OKF Project-Hub Structure (canonical shape)

The canonical OKF bundle for a feature build that warrants its own parent epic + child epics + child tasks. This pattern emerged from the journal-pe-integration and pe-cron-workflow-gaps builds (2026-07-26) and applies to any future feature handoff.

## Required file layout

```
okf/projects/<project-slug>/
├── index.md                    # Project hub
├── HANDOFF.md                  # Cold-start recipe (sections 1-7 or 1-8)
├── decisions/
│   ├── 001-<slug>.md
│   ├── 002-<slug>.md
│   └── ...                     # One ADR per major decision
├── risks/
│   └── <slug>.md               # Risk register
└── ... (any other project-specific docs)
```

The project must be linked from `okf/index.md`, `okf/projects/index.md`, and (for decisions) `okf/decisions/index.md` in the same change.

## Required content per file

### `index.md` (project hub)

- **Parent epic goal + exit criterion** (verbatim, copy-paste from the parent epic description).
- **Child epic table** with at minimum these columns: `#` (sequence), `Epic`, `Title`, `Exit criterion`, `Owner`, `First step`, `Tasks`.
- **Total task count** (e.g., "Total: 39 child tasks across 7 epics").
- **Task inventory** organized by epic — one section per epic with the task titles and target paths.
- **Rubric** applied to every task (Unit / Integration / Revenue / Assumption).
- **Decision Records** pointer — list every ADR in `decisions/`.
- **Risk** pointer — list the risk register path.
- **Discovery Evidence** pointer — list the discovery report path.
- **Bound Standard** pointer — list the binding standard path.
- **Sequencing** — explicit order with rationale ("Stabilize before Storage before Ingest before Governance before Cron before UI before HDE" is the canonical order from journal-pe-integration).
- **Routing Convention** — what labels every task carries (`agent:<owner>`, `dispatch:ready`, `type:task`, `agent:peer-review-blocked`); what description shape is used (seven-field + Distributed-Execution Header).
- **Cold Start Path** — pointer to `HANDOFF.md`.

### `HANDOFF.md` (cold-start recipe)

Sections (1–7 baseline; 1–8 when cross-project dependencies exist):

1. **What is this?** — one paragraph: goal + verbatim exit criterion from the parent epic.
2. **Where does the work live?** — Code paths (repo-relative), OKF docs (paths), Linear epic + epics + tasks (IDs and titles).
3. **Read order (cold start, ~10 minutes)** — numbered list of 5–8 steps pointing at the OKF docs + Linear issues an agent should read first.
4. **First concrete action** — 1–3 imperative bullets that produce a verifiable artifact; typically "pick the lowest-numbered task in the earliest epic that is still `Todo`".
5. **Stop conditions** — explicit list of when to escalate (ask Michael / George / Becca / AGY), each with a trigger; explicit definition of "Done".
6. **Owners** — table of `Role | Name` for parent epic owner, risk acceptance, stability sign-off, etc.
7. **Conventions not to break** — branch prefix per `PRISMATIC_ENGINE.yaml`, commit prefix, lane ownership, swarm locks, no Done without verified evidence.
8. **Cross-project dependencies** *(optional, only when applicable)* — what this project unblocks, what this project depends on.

### `decisions/NNN-<slug>.md` (one ADR per major decision)

Each ADR must carry:

- **Frontmatter** (type=Decision, title, description, resource, git_path, tags, timestamp, linear_issue, git_repo, last_verified, verified_by, status).
- **Context** — why this decision was needed; what existed before; what triggered the question.
- **Decision** — what was decided; the binding form of the choice.
- **Consequences** — what changes because of this decision.
- **Reversibility** — how to undo this decision; per-clause reversibility if any.
- **Owner** — Decision owner, Implementation owner, Reversibility owner, Compliance owner (where applicable).
- **Acceptance Test IDs** — list of test IDs that prove the decision is implemented, with Linear issue links.

### `risks/<slug>.md` (risk register)

Each risk as a **table** with these cells:

| Field | Value |
|---|---|
| Owner | <named humans — Michael, George, Becca, ned, fred, AGY> |
| Likelihood | low/medium/high (with notes if applicable) |
| Impact | low/medium/high/critical |
| Observable signal | <what specific measurement or event signals this risk has triggered> |
| Mitigation | <concrete actions taken to reduce the risk> |
| Backout | <how to roll back if the risk materializes> |

The risk register must also include **Rollout Plan** (per-feature-flag), **Observability Requirements**, and **Owner** sections at the bottom. Named humans (not generic "team" placeholders) in every Owner cell.

### `standards/<slug>.md` (if class-level)

Use only when the project introduces a binding standard that other projects will inherit. Otherwise skip — the project-specific docs are enough.

A binding standard has:

- **Scope** — what this contract binds.
- **Normative requirements** — numbered tables (`H1`–`H7`, `L1`–`L4`, `R1`–`R5`, `D1`–`D5`, `W1`–`W3`).
- **Conformance** — what a change must do to be conformant.
- **Verification language** — the exact phrasing to use when reporting conformant work.
- **Cross-references** — pointers to related standards and OKF docs.

## Required hub-level pointers

When the project lands, update these indexes in the same change:

- `okf/index.md` — add a row to the "Recent Additions" table with date, title, path, type. Include `Revision` rows for incremental additions.
- `okf/projects/index.md` — add the project slug + path.
- `okf/decisions/index.md` — add a "Project Decision Folders" row pointing at the new `okf/projects/<slug>/decisions/` folder, plus "Latest Decisions" rows for each ADR.
- `okf/standards/index.md` (if a binding standard was added) — add a row.
- `okf/reports/index.md` (if a discovery report was added) — add a row.

## When to use this shape

Use it when:

- The feature has 1+ parent epics with N child epics and M child tasks.
- 2+ agents may pick up tasks from the epic tree.
- The user asks for a "comprehensive plan" with OKF + Linear deliverables.
- The build-out is the first feature of a new class of work and the lessons generalize.

Do not use it when:

- The work is a single Linear task (no epic tree).
- The work is a bug fix or a hotfix that does not warrant durable documentation.
- The work is internal-only and the user has explicitly waived documentation.

## Pitfalls

- Do not skip the HANDOFF.md. A project without HANDOFF.md is non-conformant even if every other file is perfect — the cold-start reader has no recipe.
- Do not put generic "team" placeholders in the Owners section or the risk register. Named humans only.
- Do not skip the Sequencing section in `index.md`. Without it, an agent picking up tasks in the wrong order will hit cross-epic blocking.
- Do not copy the parent exit criterion loosely — copy it verbatim. "Close enough" wording is a subtle drift that future agents cannot detect.
- Do not link to the index from the index itself. Add a "Recent Additions" row in `okf/index.md`, but the project index is the natural discovery entry point already.
- Do not skip the `Routing Convention` section in `index.md`. Without it, agents will pick up tasks without setting `agent:in-progress` and the multi-agent coordination collapses.
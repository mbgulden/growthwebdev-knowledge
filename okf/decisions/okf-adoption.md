---
type: Decision
title: OKF Adoption (Hub-and-Spoke)
description: Adopt Open Knowledge Format v0.1 with hub-and-spoke layout. Hub = growthwebdev-knowledge repo; spokes = project repos.
resource: okf/decisions/okf-adoption.md
tags: [decision, okf, knowledge-management, documentation]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/decisions/okf-adoption.md
last_verified: 2026-06-19
verified_by: fred
status: current
---

# OKF Adoption (Hub-and-Spoke)

## Context

Knowledge sprawl across the growthwebdev stack:

- Repo docs (`/home/ubuntu/work/<repo>/docs/`)
- Profile MEMORY.md (`~/.hermes/profiles/<name>/memories/`)
- Linear Documents (newly created, 1 so far)
- AGY artifacts (`/tmp/agy-dispatch-*-result.md`)
- Skill references (`~/.hermes/profiles/<name>/skills/<skill>/references/`)

Without a standard, every new doc asks "where does this go?" and the answer
is "wherever Michael last put one."

## Decision

Adopt Open Knowledge Format v0.1 with a **hub-and-spoke** layout:

- **Hub repo:** `mbgulden/growthwebdev-knowledge` — cross-project standards, project indexes, decision records.
- **Spoke repos:** each project keeps its own `okf/` subdirectory (e.g. `prismatic-engine/okf/`).

Frontmatter follows OKF v0.1 spec with these extensions: `linear_issue`,
`git_repo`, `git_path`, `last_verified`, `verified_by`, `status`.

## Consequences

**Positive:**

- Single format across the stack. Markdown + YAML = no vendor lock-in.
- Git-versioned knowledge. PR review covers docs alongside code.
- Frontmatter enables query/index: "give me all `type=Standard` docs with
  `status=current`."
- Standards live in the hub so they're canonical across projects.

**Negative:**

- Two-place maintenance (hub + spoke). Drift risk.
- Initial migration cost (every doc needs frontmatter + index updates).
- OKF v0.1 is a draft spec; future versions may break our frontmatter.

## Alternatives considered

- **One giant wiki:** rejected — becomes a dumping ground, no permission boundaries.
- **One wiki per repo (no hub):** rejected — solves "where docs live" but not
  "how do I find cross-project docs."
- **Notion:** rejected — vendor lock-in, not git-versioned.
- **Cloudflare Pages:** considered for public-facing docs only, not for internal.

## Implementation plan

- **Tier 5a (this turn):** Hub repo created. 3 pilot docs in `prismatic-engine/okf/`.
- **Tier 5b:** Migrate remaining repo docs to OKF on a per-repo basis as their docs stabilize.
- **Tier 5c:** Wire OKF awareness into `prismatic doctor`. Add viewer (similar to Google's `viz.html`).

## Refs

- OKF v0.1 spec: <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>
- Knowledge Catalog blog: <https://cloud.google.com/blog/products/data-analytics/introducing-the-google-cloud-knowledge-catalog>
- Tier 4 architecture: [`../projects/prismatic-engine.md`](../projects/prismatic-engine.md)
- GRO-2033 (Ned's docs initiative)
- GRO-2039 (this decision's tracking issue)

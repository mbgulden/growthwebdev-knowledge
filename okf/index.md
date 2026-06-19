---
type: Index
title: growthwebdev-knowledge — Master Index
description: Master listing of all OKF concepts in the growthwebdev knowledge hub.
resource: https://github.com/mbgulden/growthwebdev-knowledge
tags: [index, hub, okf]
timestamp: 2026-06-19T11:15:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/index.md
last_verified: 2026-06-19
verified_by: kai
status: current
---

# growthwebdev-knowledge — Master Index

This bundle indexes cross-project standards and points to per-project docs in
spoke repositories.

## Sections

- [Standards](./standards/index.md) — Cross-project canonical standards
- [Projects](./projects/index.md) — Per-project index docs (pointing at spokes)
- [Decisions](./decisions/index.md) — Architecture decision records
- [Integrations](./integrations/index.md) — External tool integrations (MCP servers, SaaS APIs)

## What is OKF?

OKF (Open Knowledge Format) is a vendor-neutral spec for representing knowledge
as plain markdown files with YAML frontmatter. See
[SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Our frontmatter extensions: `linear_issue`, `git_repo`, `git_path`, `last_verified`,
`verified_by`, `status`.

## Maintenance

- Hub `index.md` files: hand-maintained for now. Tier 5c may add a generator.
- Spoke docs: project repos own their own `okf/`. Hub indexes point at them.
- Sync: when a spoke doc moves or is deprecated, update the per-project index here.

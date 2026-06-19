# growthwebdev-knowledge

Canonical knowledge hub for growthwebdev projects.

This repository hosts OKF (Open Knowledge Format) bundles that index and document
the cross-project standards, runbooks, and architecture decisions used across
the growthwebdev stack.

## Layout

```text
okf/                           # Open Knowledge Format bundle (per OKF v0.1)
├── index.md                   # Master listing
├── standards/                 # Cross-project canonical standards
│   ├── review-loop-canonical.md
│   ├── linear-rate-limit.md
│   └── ...
├── projects/                  # Per-project index docs (point at spokes)
│   ├── prismatic-engine.md
│   └── ...
├── decisions/                 # Architecture decision records
│   └── tier-1-tier-4-status.md
└── README.md                  # This file
```

Spoke repositories (e.g. `prismatic-engine`) keep their own `okf/` subdirectories
for project-specific docs. This hub indexes them via the per-project pages.

## OKF v0.1

We follow the Open Knowledge Format v0.1 spec:
<https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>

Frontmatter rules:

- `type` — REQUIRED. Short string ("Architecture", "Standard", "Runbook", "Concept").
- `title` — display name
- `description` — one-line summary
- `resource` — canonical URI (Linear issue, GitHub file path)
- `tags` — list of strings
- `timestamp` — ISO 8601

Extensions we use (allowed by spec):

- `linear_issue` — e.g. "GRO-2024"
- `git_repo` / `git_path` — file location
- `last_verified` / `verified_by` — audit trail
- `status` — current | draft | deprecated

## Where to find things

| Need | Where |
|---|---|
| Cross-project standard (e.g. review loop) | `okf/standards/` |
| Per-project docs | spoke repo's `okf/` (linked from `okf/projects/`) |
| Architecture decisions | `okf/decisions/` |
| Current Linear work | Linear (linked via `linear_issue` frontmatter) |
| Runtime state | Hermes profile `MEMORY.md` (not OKF) |

## Tier 5a pilot status

GRO-2039 tracks the pilot. Three docs in `prismatic-engine/okf/`:

- `architecture.md`
- `review-loop-canonical.md`
- `linear-rate-limit.md`

Each gets an `index.md` listing. AGY peer review before merge.

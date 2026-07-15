---
type: Index
title: Prismatic Engine
description: Compatibility project pointer for Prismatic Engine; canonical project index now lives under okf/projects/prismatic-engine/index.md.
resource: okf/projects/prismatic-engine.md
tags: [index, project, prismatic-engine, compatibility]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic Engine

The canonical Prismatic Engine OKF project index is now:

```text
okf/projects/prismatic-engine/index.md
```

Open it here:

- [Canonical Prismatic Engine project index](./prismatic-engine/index.md)

## Current records

| Record | Status | Why it matters |
|---|---:|---|
| [Canonical project index](./prismatic-engine/index.md) | current | Single hub entry point for Prismatic governance, dispatcher, dashboard, Tier 7, and OKF recovery records. |
| [Governance Dashboard Ingestion Queue repair closeout](./prismatic-engine/ingestion-queue-repair-2026-07-14.md) | current | Durable queue ledger, `/api/gateway` aliases, retry/purge mutation semantics, audit timeline, and live proof. |
| [Prismatic OKF treasure hunt Phase 1–6 reconciliation](../reports/prismatic-okf-treasure-hunt-2026-07-15.md) | current | Full source inventory, extraction, dedupe, classification, and canonical structure proposal. |

> Current caveat: `prismatic-engine/deploy-fresh` does **not** currently contain a first-class `okf/` tree. Use the treasure-hunt report plus the repo-local `docs/okf-map.md` breadcrumb before trusting older hub links to `prismatic-engine/blob/main/okf/...`.

## Legacy note

Older content in this file pointed directly at historical `prismatic-engine/blob/main/okf/...` paths. Those paths are not treated as current truth unless verified against the current deployment lane. This file remains as a compatibility shim for older links.

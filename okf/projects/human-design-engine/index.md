---
type: Index
title: Human Design Engine
description: Hub index for Human Design Engine launch, payment, onboarding, and governance records.
resource: okf/projects/human-design-engine/index.md
tags: [index, project, human-design-engine, hde, stripe]
timestamp: 2026-07-13T20:00:00Z
linear_issue: GRO-3792
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/human-design-engine/index.md
last_verified: 2026-07-13
verified_by: fred
status: current
---

# Human Design Engine

Hub index for Human Design Engine records that are broader than one repository file.
The active spoke repo is `mbgulden/hd-platform` / local workspace
`/home/ubuntu/work/hd-platform-staging`.

## Current records

| Record | Date | Status | Why it matters |
|---|---:|---:|---|
| [HDE Stripe staging launch closeout](./staging-stripe-launch-2026-07-13.md) | 2026-07-13 | current | Revenue gate, staging push, verification boundary, and remaining launch proof. |

## Related standards

- [Prismatic staging governance](../../standards/prismatic-staging-governance.md)
- PWP visual QA proof standard — pending hub publication on `main`; keep hosted visual proof in the HDE launch evidence bundle.

## Open launch evidence still required

The 2026-07-13 closeout proves the local staging build and Stripe test-account
availability. It does **not** replace the hosted pre-live walkthrough. Before
public launch, capture hosted staging evidence for:

- browser checkout-session creation in Stripe test mode,
- webhook event roundtrip,
- success/onboarding resume path,
- live visual walkthrough and screenshots,
- accessibility/performance smoke where practical.

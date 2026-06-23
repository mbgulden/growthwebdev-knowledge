---
type: Index
title: Incidents
description: Index of incident reports — what broke, root cause, fix, and anti-pattern rule.
resource: okf/incidents/index.md
tags: [index, incidents, post-mortems, root-cause]
timestamp: 2026-06-23T17:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/incidents/index.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Incidents

What broke, why, and how it was fixed. Each incident has a root cause + anti-pattern rule.

| Incident | OKF location | When |
|---|---|---|
| **AGY/Ned/Kai dispatcher fix (2026-06-23)** | [`./2026-06-23-dispatcher-fix.md`](./2026-06-23-dispatcher-fix.md) | 5-min batch-invoke replaced with queue writes |

## How to file

When something breaks:
1. Stop and reproduce
2. Find the root cause (not just the symptom)
3. Fix it
4. Write the incident report (root cause + fix + anti-pattern rule)
5. File a follow-up Linear issue if more work is needed
6. Update OKF process docs if the incident reveals a missing standard

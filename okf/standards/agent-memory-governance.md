---
type: Standard
title: Agent Memory Governance
description: Cross-profile standard for selective Hermes memory pruning, dedupe, OKF/skill routing, and future memory write gates.
resource: okf/standards/agent-memory-governance.md
tags: [hermes, memory, governance, agents, pruning]
timestamp: 2026-07-18T00:00:00Z
linear_issue: none
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/agent-memory-governance.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# Agent Memory Governance

## Purpose

Hermes profile memory is the smallest and highest-impact knowledge layer. It should contain durable facts and preferences that change agent behavior, not task logs, PR history, branch names, stale blockers, or raw operational output.

This standard governs selective pruning across Fred, orchestrator, Ned, George, Kai, and other Hermes profiles.

## Placement gate

Before writing a memory, route the fact through this gate:

| Candidate | Destination |
|---|---|
| Durable user preference or correction | `USER.md` |
| Durable environment/agent convention that changes future behavior | `MEMORY.md` |
| Reusable workflow, commands, pitfalls, verification pattern | Hermes skill |
| Governance standard, incident, audit, architecture, project policy | OKF |
| Current task progress, PR, commit, branch, one-off blocker, stale issue count | Linear/session history, not memory |
| Easy live lookup | Tool lookup, not memory |

A memory entry should normally pass all five tests:

1. Valid for 30+ days.
2. High-friction for Michael to repeat.
3. Changes future agent behavior.
4. Concise enough to stay under cap.
5. Not better represented by OKF, a skill, Linear, git, or session history.

## Selective pruning algorithm

1. Parse each target file by `§`-delimited entries.
2. Back up every edited file under `memories/.archive/YYYY-MM-DD/selective-prune-<timestamp>/`.
3. Classify entries as keep, replace, remove, or move-to-OKF/skill.
4. Remove exact duplicates inside the profile.
5. Replace stale task-specific entries with short durable summaries plus OKF/skill pointers.
6. Keep ambiguous but still-useful domain facts by compressing them, not deleting them.
7. Verify parseability, caps, duplicate absence, backup presence, and OKF/skill reference existence.

## Rewrite rules

Good memory shape:

> Michael prefers active-problem-only digests; green/all-clear cron output should be silent. OKF: `okf/standards/cron-alert-output-contract.md`.

Bad memory shape:

> On 2026-07-13, job X failed, PR Y fixed it, commit Z merged, then detector asked for verifier N.

Keep procedure out of memory:

> Use skill `memory-selective-pruning` for future cross-profile memory audits.

## Profile-specific guidance from the 2026-07-18 review

| Profile | Review outcome |
|---|---|
| Fred / orchestrator | Deduped and compressed to behavior/governance preferences; moved verification, cron, OKF, and dispatch detail behind OKF/skill references. |
| Ned | Compressed stale HDE/Cloudflare/Darius implementation facts into live-check/OKF-backed conventions; preserved Sentinel and HDE product direction. |
| George | Compressed oversized user profile entry; kept George’s review/runway role and AOT/Kai boundary. |
| Kai | Kept AOT/Kai operating facts; future pruning should move media-classification detail into Active Oahu business OKF when available. |

## Future write gate

Do not write memory when the fact is:

- a completed-work log,
- a PR/commit/branch/status update,
- a temporary Linear issue state,
- a raw source dump,
- an unverified external fact,
- a procedure better captured as a skill,
- a project/governance record better captured as OKF.

Prefer replacing existing stale entries in the same operation over adding new ones.

## Verification contract

A pruning run is verified only when a fresh `/tmp/hermes-verify-*` script checks:

- edited memory files exist and parse into entries,
- backups exist,
- edited files are below configured caps or over-cap status is intentionally reported,
- exact duplicate entries are absent inside each edited file,
- stale-task markers are reduced or explicitly justified,
- referenced OKF/skill files exist,
- no temp verifier remains.

Report the result as **ad hoc targeted verification**, not suite green.

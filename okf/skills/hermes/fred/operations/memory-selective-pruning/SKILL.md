---
name: memory-selective-pruning
description: Selectively prune Hermes profile memories by replacing stale/task-level facts with tight durable summaries, deduping across memory/user stores, and gating future memory writes against OKF/skill placement.
triggers:
  - profile memories are near capacity
  - user asks to prune, groom, compact, or dedupe memory
  - memory entries contain stale PRs/issues/branches/session outcomes
  - recurring corrections should become a skill or OKF standard instead of another raw memory
---

# Memory Selective Pruning

Use this before editing `~/.hermes/profiles/*/memories/MEMORY.md` or `USER.md`.

## Best-practice decision gate

Only keep a memory entry when it is:

1. **Durable** — likely valid for 30+ days.
2. **High-friction to rediscover** — saves Michael from repeating himself.
3. **Action-shaping** — changes how an agent should behave.
4. **Small** — ideally under 180 chars; rarely over 260 chars.
5. **Not better as OKF/skill/session history**.

Route elsewhere:

| Candidate | Destination |
|---|---|
| Procedure/workflow | Skill |
| Project standard, policy, audit, incident, architecture | OKF |
| Task progress, PR number, commit, branch, temporary blocker | Session history or Linear, not memory |
| Raw facts easy to query/live-check | Tool lookup, not memory |
| User preference/correction | USER.md if global, MEMORY.md if operationally scoped |

## Pruning workflow

1. **Inventory first**
   - Parse every target profile’s `MEMORY.md` and `USER.md` by `§` entries.
   - Record char count, entry count, exact duplicates, near-duplicates, stale-task markers (`GRO-`, PR, branch, Done, merged, date-specific outcomes), and oversized entries.

2. **Back up before edits**
   - Copy each edited file to `memories/.archive/YYYY-MM-DD/selective-prune-<timestamp>/`.
   - Never edit without a rollback path.

3. **Classify each entry**
   - Keep as-is: compact durable preference/fact.
   - Replace: stale detail that can become a tight summary plus OKF/skill reference.
   - Remove: duplicate, superseded, task progress, old branch/PR/result, or easy live lookup.
   - Move to OKF/skill: reusable procedure or project standard.

4. **Rewrite, don’t just delete**
   - Prefer consolidating 3–8 related entries into one high-signal summary.
   - Include durable OKF references where the entry points to policy/history, e.g. `OKF: okf/standards/agent-memory-governance.md`.
   - Avoid imperative phrasing in memories; write declarative facts.

5. **Future write gate**
   Before adding memory, ask:
   - Would this be stale in a week?
   - Is it a completed-work log?
   - Is this actually a reusable procedure? If yes, update/create a skill.
   - Is this a governance/project record? If yes, OKF.
   - Can a tool rediscover this cheaply? If yes, do not memorize.

6. **Verify**
   - Files parse into non-empty `§` entries.
   - No exact duplicate entries remain inside each edited profile.
   - Memory/User files are below target caps, or remaining overage is explicitly manual/intentional.
   - New OKF/skill references exist.
   - Backups exist.
   - Report as ad hoc targeted verification, not suite green.

## Safety rules

- Do not remove secrets by printing them; redact or replace with “credential location/pattern” only.
- Do not delete ambiguous domain facts if the agent depends on them and no OKF source exists yet; compress them instead.
- Do not prune another profile unless Michael explicitly authorizes cross-profile memory work.
- Do not treat “referenced path missing” as automatic stale if the fact is still an operating convention; verify or compress.
- Do not use memory for raw task progress, PR queues, or completed-work logs.

## Canonical OKF reference

- `okf/standards/agent-memory-governance.md` — cross-profile memory gate, pruning rubric, and reviewed profile rewrite log.
- `references/agent-memory-okf-lifecycle-2026-07.md` — session pattern for making the Agent Memory OKF standard durable on `origin/main` before profile memories rely on it.

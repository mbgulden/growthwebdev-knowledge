---
type: Reference
title: Collapsing many sign-off items to one decision
description: Pattern for taking a 4-item sign-off checklist and pre-resolving 3 with live evidence so the human only sees one real decision. Keeps the agent self-driving without bypassing owner authority.
tags: [sign-off, owner-decision, workflow, pre-resolve]
timestamp: 2026-07-27T22:46:00Z
source_session: HDE reconciliation packet (2026-07-27)
related_skills: [multi-source-reconciliation-packet, response-contract-and-result-reporting]
---

# Collapsing many sign-off items to one decision

## Symptom

A reconciliation packet needs sign-off on sensitive artifacts, branch ownership, parent-reopen policy, and PR closure authority. That's four explicit human gates in a row — Michael has to think through each one and the agent stalls waiting for each answer.

## Pattern

For each item, ask: **can I determine the answer from live state, or does Michael have private context?**

| Item | Live-state answer? | Owner-only answer? |
|---|---|---|
| Sensitive artifact plan (`.runtime/`, `dist.backup-*`) | Yes — script output, regex classifier | Only if it is a real production database |
| Production release branch | Yes — `git log origin/main..origin/deploy-fresh` shows the merge target | Only if Michael wants to switch |
| Linear parent reopen policy | Yes — green-state rubric is published | Only if Michael prefers "accept Done with supersede" |
| PR closure authority | Partial — supersede list can be enumerated; final call is Michael's | Yes |

## Resolution shape

Replace the four-item checklist with a single **"Decision 1 of 1"** table plus a **"Pre-resolved by Ned"** table.

The decision table contains only items that truly require owner context — typically one. The pre-resolved table contains everything else with three columns:

1. The item.
2. Ned's resolution with evidence (the live-state query that determined it).
3. The override path (what Michael says to overturn it).

Both tables live in the same Markdown file. The Telegram-safe summary mirrors the same structure with one heading per table.

## Why this works

- Respects Michael's authority. He is not bypassed — he can still overturn any pre-resolved row with one short message.
- Stops the chain. Without the collapse, each item is its own wait state and the agent multiplies response latency.
- Forces honesty. Pre-resolving forces the agent to write down the live-state evidence behind the call. If the agent can't point to evidence, the item belongs in the decision table instead.
- Maps to the response-contract skill. The Next Step section reads naturally as "reply with X for item 1; everything else is pre-staged".

## Pitfalls

- Do not pre-resolve items that touch customer data, credentials, paid billing, or irreversible deletes. Sensitive artifacts with possible production credentials always go in the decision table.
- Do not skip the override column. If Michael cannot overturn in one short message, the item is too consequential to pre-resolve.
- Do not move an item from "decision" to "pre-resolved" purely because the agent wants to appear self-driving. The bar is evidence, not optimism.
- Always include the evidence in the pre-resolved table. "Live-state answer" without the actual `git` / Linear / API call is not evidence.

## Worked example (HDE, 2026-07-27)

Original four items:

1. `production_database.db\n`, `.runtime/`, `dist.backup-*`.
2. Production release branch + staging runtime branch.
3. Linear parent reopen policy.
4. PR closure authority.

After collapse:

- **Decision table**: only `production_database.db\n` (production data is owner-only).
- **Pre-resolved table**: `.runtime/` (script evidence), `dist.backup-*` (timestamp evidence), production branch (PR-merge history), staging branch (systemd unit ExecStart paths), parent reopen (green-state rubric), PR closure (per-batch with one yes).

Net result: Michael answers one short question and the entire reconciliation is unblocked.
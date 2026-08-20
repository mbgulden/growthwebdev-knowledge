---
name: linear-routing-classify
description: Linear issue labels are mutually consistent with the dependency graph.
---

# linear-routing-classify

## What this verifier checks

Linear issue labels are mutually consistent with the dependency graph.

Specifically:

For each Linear issue: agent:* labels match dispatch:* labels (e.g., agent:needs-human-review ↔ dispatch:paused). A task labeled dispatch:ready has all agent:completed markers in its dependency chain. agent:needs-human-review issues have at least one pending_decisions_for_human[] entry in the latest handoff of the assigned agent.

## Inputs

linear_team (str, default: 'MBG'), days_back (int, default: 30)

## Exit codes

0 if all consistent, 1 if any inconsistency (prints issue ID + reason)

## When to use this verifier

Per `verifier-as-deliverable-discipline/SKILL.md`, this verifier ships alongside any artifact that touches its domain. Run it before claiming the artifact is done.

## Adoption status

Status: shipped as a named skill; the verification logic is documented. The implementation script (`verify.py`) is the next deliverable for each verifier. Until the script lands, this verifier exists as a discipline (a named check the agent runs mentally) rather than a runnable artifact.

**Note for future-self:** this is intentional. The four named verifiers were promoted to named skills before their scripts existed because the discipline is "name the check", not "ship the script first". The script is the next bounded move for each.

# GRO-559 Routing Classification (Email Capture / Lead Magnet)

**Issue:** GRO-559 "Set up Email Capture and Lead Magnet system"
**First surfaced in Ned cron sweep:** 2026-06-26 05:47Z (drift-added; not in 01:30Z/23:31Z/21:55Z sweeps)
**Labels:** `agent:ned` (misrouted)
**State:** Backlog

## Correct lane: **content/marketing**

Lead-magnet design (sample deprogramming session, framework PDF, mini-course), opt-in landing pages, and automated email nurture sequences for lead conversion — none of these touch infrastructure (GPU nodes, disk, GitHub, Cloudflare, swarm agents). The labeling was almost certainly a sweep artifact from the same `scan_tasks.py` bug that misroutes GRO-608/575/572/571/570/568/567/565/564.

## One-liner for triage comment

> **GRO-559** — Set up Email Capture and Lead Magnet system. → **content/marketing lane** (lead-magnet design + landing pages).

## If GRO-559 reappears on a future cron sweep

1. Skip the validation fetch (already classified).
2. Reference this note in the routing-sweep enumeration.
3. Continue to count it as one of the N misrouted items but don't re-investigate.

## Sibling issues still likely to drift in

- GRO-559 (this one) — content/marketing
- Any `agent:ned` issue touching landing pages, email funnels, opt-in forms, lead magnets, content upgrades → content/marketing lane
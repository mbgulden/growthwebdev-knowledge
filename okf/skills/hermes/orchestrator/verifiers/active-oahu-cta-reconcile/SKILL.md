---
name: active-oahu-cta-reconcile
description: Every CTA on the active-oahu mirror is reachable and matches its marketing claim.
---

# active-oahu-cta-reconcile

## What this verifier checks

Every CTA on the active-oahu mirror is reachable and matches its marketing claim.

Specifically:

For each CTA element on the live mirror: (1) the href/url resolves (HTTP 200 or 3xx), (2) the element is visible (not display:none, not aria-hidden, not 0×0), (3) the destination matches the visible text (e.g., 'Book Now' → FareHarbor shortname, not /contact), (4) the CTA is reachable from the homepage in ≤3 clicks.

## Inputs

site_root (str, default: '~/work/active-oahu-tours-mirror-2529/site')

## Exit codes

0 if all CTAs reconcile, 1 if any CTA broken (prints CTA selector + reason)

## When to use this verifier

Per `verifier-as-deliverable-discipline/SKILL.md`, this verifier ships alongside any artifact that touches its domain. Run it before claiming the artifact is done.

## Adoption status

Status: shipped as a named skill; the verification logic is documented. The implementation script (`verify.py`) is the next deliverable for each verifier. Until the script lands, this verifier exists as a discipline (a named check the agent runs mentally) rather than a runnable artifact.

**Note for future-self:** this is intentional. The four named verifiers were promoted to named skills before their scripts existed because the discipline is "name the check", not "ship the script first". The script is the next bounded move for each.

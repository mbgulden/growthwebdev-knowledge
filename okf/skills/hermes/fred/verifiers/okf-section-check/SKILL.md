---
name: okf-section-check
description: Every OKF doc has valid frontmatter, status:current, and required core sections.
---

# okf-section-check

## What this verifier checks

Every OKF doc has valid frontmatter, status:current, and required core sections.

Specifically:

Frontmatter (type, title, status:current, timestamp, tags), 6 standard sections (Purpose, What this standard defines, What this standard does NOT cover, Adoption status, Honest lessons, Related work), all relative .md links resolve, no orphans.

## Inputs

okf_path (str): the OKF file to check

## Exit codes

0 if pass, 1 if any check fails

## When to use this verifier

Per `verifier-as-deliverable-discipline/SKILL.md`, this verifier ships alongside any artifact that touches its domain. Run it before claiming the artifact is done.

## Adoption status

Status: shipped as a named skill; the verification logic is documented. The implementation script (`verify.py`) is the next deliverable for each verifier. Until the script lands, this verifier exists as a discipline (a named check the agent runs mentally) rather than a runnable artifact.

**Note for future-self:** this is intentional. The four named verifiers were promoted to named skills before their scripts existed because the discipline is "name the check", not "ship the script first". The script is the next bounded move for each.

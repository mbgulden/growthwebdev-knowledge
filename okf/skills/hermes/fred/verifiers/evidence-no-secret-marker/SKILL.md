---
name: evidence-no-secret-marker
description: No raw API key, token, or '***' literal placeholder appears in committed files.
---

# evidence-no-secret-marker

## What this verifier checks

No raw API key, token, or '***' literal placeholder appears in committed files.

Specifically:

Scan git-tracked paths for: literal '***' substring (3+ asterisks), known key prefixes (sk-or-, lin_api_, AIza, sk-, ghp_), bearer token patterns. Excludes: test fixtures under /tmp/hermes-verify-* and pin/archive files.

## Inputs

scan_paths (list of paths to scan, default: okf/ and skills/)

## Exit codes

0 if clean, 1 if any marker found (prints file:line)

## When to use this verifier

Per `verifier-as-deliverable-discipline/SKILL.md`, this verifier ships alongside any artifact that touches its domain. Run it before claiming the artifact is done.

## Adoption status

Status: shipped as a named skill; the verification logic is documented. The implementation script (`verify.py`) is the next deliverable for each verifier. Until the script lands, this verifier exists as a discipline (a named check the agent runs mentally) rather than a runnable artifact.

**Note for future-self:** this is intentional. The four named verifiers were promoted to named skills before their scripts existed because the discipline is "name the check", not "ship the script first". The script is the next bounded move for each.

---
name: corrections-lead-with-recipe
description: When correcting an agent's work, lead with the verification recipe (the ground-truth check the agent can run), not the assertion of the correct value. Recipes enable self-correction; assertions alone invite confident same-shape re-attempts that pass internal verifiers but fail real-world.
---

# corrections-lead-with-recipe

## The rule

When telling another agent (or yourself in a future turn) that their artifact is wrong:

1. **State the discrepancy** — what's wrong, in one sentence.
2. **Name the verification recipe** — the exact command or check the agent should run to see the discrepancy themselves. Example: "grep `gtag.*config` in `site/index.html` to find the real GA4 ID" or "look at the live API response, don't trust the cached value."
3. **Then state the correct value** — only after the recipe is named.
4. **Demand a specific reply format** — e.g., "reply with `kpi-collections.json rewritten at <path>, <bytes>` so the correction is verifiable mechanically."

## Why this works

An assertion alone ("the GA4 ID is G-PRRRLMBR8Z") invites the agent to take your word for it. They may write the right value this time but won't build the muscle to check the next time.

A recipe ("grep site/index.html for `gtag.*config`") teaches the agent to ground themselves in external truth. They can re-verify your correction, catch their own mistakes, and apply the pattern to the next correction.

## When to use this

- Any time you correct an artifact produced by another agent (or yourself).
- When the correction involves a real-world value (a key, a path, an ID) that the agent could verify against external truth.
- When you want the corrected artifact to survive a future-self re-verification.

## Anti-patterns

- "The X should be Y, just fix it." (No recipe. The agent re-derives X and may pick a different wrong value.)
- "Trust me, X is Y." (Recipes enable trust calibration, not blind trust.)
- "X is Y, you can verify later." (Verifying "later" means "never". Recipe-then-verify-now.)

## Verification

The corrected artifact, after the agent applies the recipe, matches external truth without further nudging. The agent posts a verifiable reply (path + bytes, or screenshot + URL, or terminal output) that proves the change landed at the right place with the right values.

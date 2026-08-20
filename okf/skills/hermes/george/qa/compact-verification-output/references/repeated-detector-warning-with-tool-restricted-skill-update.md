# Repeated verification detector warning during a tool-restricted skill-library update

Session lesson from Prismatic dashboard task-admission closeout.

## Trigger

A Hermes verification guard repeats the same changed-path warning after a current-turn compliant verifier already ran, and the next user task is not to continue product work but to update the skill library. The user explicitly restricts tools to memory/skill management.

## Durable pattern

1. Do **not** run terminal/build/test tools when the user has explicitly restricted the task to memory and skill-management tools.
2. Treat the repeated guard as prior-session evidence to encode, not as authorization to violate the current tool boundary.
3. Update the relevant verification-output skill/reference with the lesson from the repeated warning. If the same session also produced a product-class lesson, update that umbrella skill too rather than only recording the detector behavior.
4. In the final reply, state exactly which skill/reference changed and why.

## How to handle the original repeated warning in normal product-work turns

When tools are allowed, the first repeated direct warning after edits still gets one fresh same-turn `/tmp/hermes-verify-*` verifier plus visible command classes. If the identical warning repeats after that current-turn compliant rerun, stop the loop and label detector non-recognition with hashes and non-claims. This also applies when the guard's `last output` keeps showing an older/stale verifier hash after a newer matching verifier already ran: comply once visibly in the current product-work turn, assert no post-verifier mutation, then stop the infinite rerun loop rather than repeatedly revalidating unchanged paths.

## Pitfall

Do not let a generic verification guard override a later, explicit user instruction that narrows allowed tools. The fix is to preserve the workflow lesson in the skill library, not to perform unrelated product verification during a skill-curation request.

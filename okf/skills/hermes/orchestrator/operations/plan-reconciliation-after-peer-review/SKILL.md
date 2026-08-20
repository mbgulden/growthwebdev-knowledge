---
name: plan-reconciliation-after-peer-review
description: Reconcile a draft plan against a peer reviewer's corrections without losing them. Honor every specific correction with live verification, surface decisions to the user, hold the no-mutation boundary until approval. Load this skill when (a) a reviewer handed you a list of corrections with file:line evidence, (b) you are about to send corrections to an agent and want the verification-recipe discipline, (c) you are about to claim "X works" with caveats — to avoid softening partial results into a successful headline. Update this file with the embedded pitfall in SKILL.md before starting work.
type: skill
---

# Plan Reconciliation After Peer Review

A peer reviewer just sent back N corrections against a draft plan. The corrections are concrete (file:line evidence) and bounded (specific gaps, not vibes). The reconciliation is to update the existing doc so it honors every correction, surfaces the residual decisions to the user, and stops short of any mutation until the user signs off.

This is **not** the same as a rewrite. A rewrite discards the reviewer's work; this skill makes the reviewer's work load-bearing.

## When to use

- A reviewer (George, or a senior reviewer on a class-level change) handed you a list of corrections with file:line evidence and recommended Linear / OKF structure.
- The user asked you to "honor" or "fold in" the corrections.
- A first draft made claims the reviewer falsified (e.g. "this is a stub" when it isn't, "this is empty" when it isn't, "size is X" when it's Y).
- A draft proposed destructive cleanup that a reviewer demands be re-framed to a non-destructive sequence.
- A draft named an architectural authority (trigger authority, scheduler authority, lock authority, rate-limit authority) and a later user correction changes the **deployment model** the authority was assumed to run under.

## When NOT to use

- The reviewer is asking for general improvements or open-ended feedback (no concrete corrections). Defer to ordinary doc iteration.
- The reviewer is a peer at the same responsibility level — defer to the user for direction.
- No plan exists yet — this skill reconciles, it does not create from scratch.
- The corrections involve a destructive mutation the user has already pre-approved with a non-revocable "yes do it" — proceed directly without reconciliation.

## Workflow

1. **Read the reviewer's full packet, then verify each correction live on the host.**
   - For every concrete correction (file:line, count, byte size, schema field, argv shape), run a non-mutating command that proves or disproves it.
   - Capture the verification command + outcome in the reconciliation notes; do NOT just trust the reviewer's claim.
   - If a correction does NOT verify, push back explicitly with evidence. Don't honor claims you can't reproduce.
   - **When YOU are the reviewer sending corrections to an agent, lead with the verification recipe, not the assertion.** "The GA4 ID is `G-PRRRLMBR8Z`" is an assertion; "grep `site/index.html` for `gtag.*config` — the only ID present is `G-PRRRLMBR8Z`" is a recipe the agent can re-run. Recipes enable self-correction; assertions enable confident re-mistakes. Apply this to every bounded-move correction, not just plan reconciliation.
2. **Classify each correction into one of three buckets:**
   - **`falsified claim`** — the reviewer proved the draft wrong. Replace the claim with the verified truth.
   - **`unsafe procedure`** — the reviewer says "stop doing X that way." Replace with the reviewer's safer sequence or propose an equivalent.
   - **`missing structure`** — the reviewer says "you forgot X." Add it.
3. **Write the revision in place, not as a new file.** The reconciled doc replaces the original draft at the same path. Preserve the original SHA in the new file's front-matter (`replaces: <sha>`) so future readers can diff.
4. **Compress where possible.** A reviewer who proposes 29 tasks may genuinely intend 18. Don't multiply epics; reuse existing parents whenever the reviewer's corrections fit them.
5. **Surface residual decisions to the user with a clear table, not a paragraph.** Each decision needs an explicit approved/not/blocked state, not narrative.
6. **Hold the no-mutation boundary.** No Linear writes, no profile / alias / cron / source change, no login, no `rm -rf`, no history rewrite. The reconciled doc is a **plan**, not a build-out. The next step is a separate `linear-handoff-build-out` invocation, gated on user approval.
7. **Verification packet at the end of the doc.** Always include a `RESULT=PASS` style block with the original doc SHA, the reviewer's packet SHA, the verified truths, and the no-claim markers (`linear_mutated=false`, `profile_mutated=false`, etc.). If the doc name was wrong in the packet, patch the file and re-read it.
7a. **Use the canonical verifier, not adjacent proof.** When a repo has `npm run build` / `npm test` / `pytest` / `python3 scripts/verify-*.py`, that is the canonical verifier for changes in that repo. Adjacent checks (Node `--check`, HTML balance walks, brace counts, custom ad-hoc probes) **supplement** but never replace the canonical command. If a verification status nudge fires after you declared "verified," you ran adjacent proof — run the canonical command and report its exit code and tail. Don't compound adjacent checks hoping to satisfy the detector.

## Pitfalls (load these as test cases)

- **Don't change an already-implemented control into a "needs to be built" task.** If the reviewer proves the rate-limit circuit is already wired into the main path, the reconciled plan keeps ONE bounded audit/repair slice, not a fresh epic that duplicates work.
- **Don't accept destructive wording.** "Wipe from history" / "rm -rf this" / "delete without backup" → replace with `inventory → supported export → archive → explicit destructive approval → supported deletion`. Hermes, Git, Linear all have non-destructive equivalents.
- **Don't assume an empty state holder is empty.** Profile directories, config files, and state DBs almost always contain more than the surface suggests. Verify with `ls -la` or equivalent before claiming "this is a clean wipe."
- **Don't trust feature flag names as rollback.** A config flip stops new side effects; it does NOT roll back already-mutated state, in-flight processes, or safety invariants. Each area needs its own correct rollout control. See the **Cron runner row** in `codex-cli-integration`'s feature-flag table for the "no always-on daemon + no second scheduler authority" pattern.
- **Don't assume the deployment model.** When a plan names an architectural authority ("the trigger authority"), check whether the deployment model can support it. If the user corrects the deployment model later, the authority choice must change. See "Mobile-first product trap" below.
- **Don't multiply reviewers' corrections into new epics.** Most peer-review packets reduce the work, not increase it. If the reviewer said "use existing parent GRO-4261," use it. Don't create a new PE-LOCKS epic when GRO-4261's PE-LOCKS-01/02 covers the same shape.
- **Don't ship the doc without verifying the verification packet.** When you patch a wrong token in the verification block, re-read the file and confirm the patched state matches what you'll claim in chat. Trust the file on disk, not what you intended to write.
- **Don't narrate when a table is clearer.** Reviewer corrections → table. Decisions requested → table. Feature-flag controls → table. Trigger surfaces → table. Default to Markdown tables for any structured data over bullets.
- **Don't run a syntax check and call it "verified."** When a repository has a canonical verifier (`npm run build`, `npm test`, `pytest`, `pnpm typecheck`, `python3 scripts/verify-*.py`, etc.) that one is the canonical proof. Adjacent checks (Node `--check`, HTML tag-balance walks, brace counts) **supplement** but never replace the canonical run. A system nudge of `Verification status: unverified` after you declared "verified" means you ran adjacent proof, not canonical proof — fix it by running the canonical command, not by running more adjacent checks. Report the canonical command's actual exit code and output, not a status derived from syntax-shape evidence. Scope label: **ad-hoc targeted verification, not suite green** even when the canonical verifier passes, unless the suite is the verifier.
- **Don't accept a self-consistent verifier PASS as ground truth.** A verifier that checks JSON-parses + schema-keys-present + formula-gates will PASS on factually-wrong values (e.g. a placeholder GA4 ID, invented event names, a URL path that doesn't exist). 44/44 PASS on a JSON file means nothing if the verifier never asks "is this value true?" Always include a ground-truth cross-check (live `grep` against the real site, real `head -c` against the real file, real `curl` against the real endpoint) that is independent of the producer's own claims.
- **Don't soften partial results into a successful headline.** When a result has caveats (2 of 5 vague, 1 of 5 unrelated failure), the headline sentence must contain the partials — not bury them in footnotes. "Cold-start proof: 5/5" with two vague replies is an overclaim; "Cold-start proof: 2/5 pass, 2/5 partial, 1/5 unrelated failure — gap NOT closed" is accurate reporting. The next session reads the handoff and trusts the headline; if the headline is wrong, they ship on top of partials. When a partial appears, diagnose it in the same turn or surface it explicitly. See `references/overclaim-partial-results-discipline-2026-07-27.md` for the worked example (gap #1 cold-start, July 2026).

## Mobile-first product trap (LESSON — from v2 of this same skill)

**Symptom:** a plan proposes "system cron as the preferred thin trigger" (or "always-on daemon," or "running background scheduler") without checking whether the product is mobile/laptop-first and the host is not always on.

**User correction that triggered this lesson (2026-07-27):**
> "prismatic engine will be accessible on multiple devices and may or may not be on a server that's 'always on'. You may be accessing it from your phone. Is system cron as the preferred thin trigger the way to go?"

**Why this hits:** system cron only fires when the host process is running. If the deployment model is mobile / laptop / phone-first, the host is **not** always on. The "trigger authority" choice must match the deployment model.

**Workable resolution that preserves the invariant:** keep **one canonical runner**, but drive it from **opportunistic wakeup** instead of a single always-on trigger. Specifically:

| Trigger surface | Fires when | Role |
|---|---|---|
| System cron lines | Host is on AND minute matches | Thin opportunistic hook into canonical runner. If host is asleep, write a marker, do not run scripts. |
| App startup / device wake / dashboard open | Operator opens the gateway | Catch-up sweep over `(now - last_session_end)` with bounded backfill window, missed-after-window recorded as `missed_during_offline`. |
| Manual "Run now" | Operator clicks | Ad-hoc fire through the same canonical runner. |
| External event | Webhook / push / registered upstream | Forwarded into the same runner; not a separate scheduler. |

**Invariant that survives the correction:** exactly one canonical runner. No second scheduler authority. Receipt identity `(job_id, schedule_bucket, trigger_kind)` keeps every fire observable.

**Diagnostic before shipping:** ask the user "is the host always-on, or is the product mobile/laptop-first?" before naming any trigger authority. If the answer is mobile-first, do not let "system cron" be the default trigger.

## Sub-decisions to surface when the trigger authority is contested

When the trigger authority is contested or changed, surface these four sub-decisions for the reviewer / user before the next code slice lands:

1. **`trigger_kind` taxonomy** — is the baseline set (`system-cron | pe-startup | manual | external-event`) enough, or do you also need `mobile-wake | background-fetch | deferred-push`?
2. **Backfill window default** — 24h / 72h / 7 days. Larger = more thundering-herd risk. Smaller = more `missed_during_offline` receipts.
3. **Hook binary shape** — does the crontab line invoke `python -m <package>` (requires the runtime checkout to be reachable) or a standalone shim (cleaner, new binary to install)? Recommended: standalone shim.
4. **Catch-up sweep gating** — auto-run on every dashboard open (simple, friendly) vs opt-in first time per session (keeps cold-open latency bounded)? Recommended: opt-in.

Do not proceed past the user-approval gate until these are answered.

## Companion skills

- `linear-handoff-build-out` — when the user approves the surfaced decisions, mutate Linear: parent + child epics + tasks with seven-field descriptions and the Distributed-Execution Header. Pairs with `okf-documentation-ops/references/okf-context-pack-for-ai-build-agents-2026-07-31.md` when the build owner is an AI agent on a single laptop (Antigravity 2.0, AGY) rather than a multi-agent chat room — the Context Pack is the agent's reference surface; the Linear tree is the reviewer's surface.
- `okf-documentation-ops` — when packaging the OKF bundle under `okf/projects/<topic>/`.
- `codex-cli-integration` — provides the canonical argv shape that this skill's corrections often reshape.
- `cron-failure-remediation` — produces the structural evidence (paths, sizes, command-line history) the reviewer uses to challenge the draft.

## References

- `references/reconciliation-session-2026-07-27.md` — full worked example: pe-foundational-gaps v1 (496 lines, 31,028 bytes) → reviewer packet (248 lines, SHA `55dfccc...`) → v1 reconciled (24,199 bytes) → v2 reconciled after user-approval cycle (32,343 bytes) including the mobile-first trigger-authority re-framing.
- `references/async-bounded-prep-handoff-2026-07-27.md` — worked example of a peer class: user-issued "do these things while I'm out" scope (not reviewer-issued corrections). Read-only audit + N local drafts + non-claim summary, drafts written outside the live tree, canonical verifier (`npm run build`) run on the host. Trigger conditions, anti-patterns, and the verification-canon pitfall captured together with the reconciliation use case.
- `references/overclaim-partial-results-discipline-2026-07-27.md` — companion pitfall: don't soften partial results into a successful headline. Worked example from gap #1 (cold-start greeting) where 2/5 of the probes were vague and 1/5 was an unrelated failure. Pairs with the verification-recipe-vs-assertion lesson already in this skill: both are about not letting clean framing obscure messy reality.

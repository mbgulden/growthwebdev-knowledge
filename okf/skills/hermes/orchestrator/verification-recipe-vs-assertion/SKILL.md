---
name: verification-recipe-vs-assertion
description: When sending corrections to an agent (or self-correcting), lead with the verification recipe — not the assertion. "The GA4 ID is G-PRRRLMBR8Z" is an assertion; "grep site/index.html for gtag.*config — the only ID present is G-PRRRLMBR8Z" is a recipe the agent can re-run. Recipes enable self-correction; assertions enable confident re-mistakes. Use whenever you correct another agent's work, hand off a bounded move, or write a handoff that future-self needs to verify before executing. Companion discipline to overclaim-partial-results — both are about not letting clean framing obscure messy reality.
category: operations
type: skill
triggers:
  - sending a bounded move to another agent and want the correction to stick
  - writing a handoff that future-self needs to verify before executing
  - claiming a Hermes mechanism is "wired" — about to call config check or schema declaration as proof
  - sending corrections and the underlying fact has external ground truth (live URL, real file, actual command output)
  - audit cycle where the reviewer handed you a list of corrections with file:line evidence
  - handing a bounded move to a sub-agent and need a mechanically-verifiable reply format
---

# Verification Recipe vs Assertion — the corrections discipline

**Core principle:** when you correct an agent's work, lead with the **recipe** the agent can run to verify the correction themselves. Asserting facts the agent then accepts blindly enables confident re-mistakes; asserting recipes the agent runs to re-confirm enables self-correction.

This is the partner discipline to `plan-reconciliation-after-peer-review/SKILL.md`'s `overclaim-partial-results-discipline` pitfall. That pitfall is about how *you* claim work; this one is about how *you* correct work.

## The pattern

### Assertion (don't lead with this)

> "The GA4 ID is `G-PRRRLMBR8Z`. The events are `booking_click` and `booking_complete`. The `/tours/` URL doesn't exist."

The agent has three options: trust, verify, or ignore. If they trust, they'll write the right answer. If they verify with different sources or reasoning, they may find contradictions. If they ignore, they'll guess.

### Recipe (do lead with this)

> "Run `grep -rh 'gtag.*config.*G-' /home/ubuntu/work/<site>/site/*.html | sed 's/.*\(G-[A-Z0-9]*\).*/\1/' | sort -u`. The only ID present is `G-PRRRLMBR8Z` — that's the real one. Then `grep -rho 'gtag.*event.*[a-z_]*' <site>/site/*.html | sort -u` — the only custom event names emitted are `booking_click` and `booking_complete`. Then `curl -sS https://<site>/<suspect_url> | head -c 200` to confirm whether the suspect URL actually serves."

The agent runs the recipes, sees the ground truth, and writes the file. If they later need to re-verify (e.g., the file gets stale, or they need to write a sibling file), they can re-run the same recipes. The verification is durable.

## Why recipes beat assertions

Three concrete reasons:

1. **Self-correction:** With a recipe, the agent can confirm the correction before applying it. With an assertion, the agent has to take your word for it — or guess whether to verify, and against what.

2. **Reproducibility:** A recipe is a command you can re-run later. An assertion is a claim that decays — the underlying fact may change, and the assertion becomes wrong without anyone noticing. Recipes can be checked against current ground truth every time.

3. **Audit:** When you say "this is wrong because the live site says X," a recipe shows your work. The agent can reproduce your check, then reproduce their fix. The audit chain is end-to-end.

## When to use recipes

Use a recipe whenever:

- **You're correcting an agent's work** and want the correction to stick.
- **You're writing a handoff** that future-self needs to verify before executing.
- **You're handing off a bounded move** and want the receiver to confirm scope before starting.
- **You're pushing back on a claim** that another agent made.
- **You're writing a verifier** that another agent will run later.

Recipes are especially valuable when:

- The ground truth is external (a live URL, a real file, an actual command output).
- The correction involves a specific value the agent could misread (a placeholder vs a real ID, an invented event vs a real one, a wrong path vs a right path).
- The agent is operating in a loop where the same fact will matter repeatedly.

## When assertions are fine

Assertions are fine when:

- **The fact is internal to your reasoning** (e.g., "this is the wrong order — call B before A").
- **The fact is a stylistic preference** (e.g., "use a table, not bullets").
- **The fact is a clear convention** (e.g., "never put secrets in a handoff").
- **The agent has no way to verify independently** and the assertion is your honest read.

In those cases, an assertion is fine. Recipes are for facts that have ground truth the agent can check.

## Compact 4-step form (formerly `skills/micro/corrections-lead-with-recipe/`)

The single-recipe form of this discipline — kept here so the umbrella is the only source of truth. When you need the 4-step version in chat or in a bounded move, copy this:

1. **State the discrepancy** — what's wrong, in one sentence.
2. **Name the verification recipe** — the exact command or check the agent should run to see the discrepancy themselves. Example: "grep `gtag.*config` in `site/index.html` to find the real GA4 ID".
3. **Then state the correct value** — only after the recipe is named.
4. **Demand a specific reply format** — e.g., "reply with `kpi-collections.json rewritten at <path>, <bytes>` so the correction is verifiable mechanically."

**Why recipes beat assertions.** An assertion alone ("the GA4 ID is G-PRRRLMBR8Z") invites the agent to take your word for it. A recipe ("grep site/index.html for `gtag.*config`") teaches the agent to ground themselves in external truth; they can re-verify your correction and apply the pattern to the next one.

**Anti-patterns.** "The X should be Y, just fix it." / "Trust me, X is Y." / "X is Y, you can verify later." (Verifying "later" means "never".)

**Verification.** The corrected artifact, after the agent applies the recipe, matches external truth without further nudging. The agent posts a verifiable reply (path + bytes, or screenshot + URL, or terminal output) that proves the change landed at the right place with the right values.

## Bounded-move-with-corrections — the class of correction that works for sub-agents

When you hand an agent a bounded move (write this file, run this command, produce this artifact) and they produce something wrong, the correction needs three things to actually stick:

1. **A specific target.** Not "the right path" — the exact path including any suffix or branch name. Sub-agents don't have the same model context you do; they may interpret "active-oahu-tours-mirror" as either of two on-disk paths.
2. **A verification recipe.** The agent can re-run the recipe to confirm the correction is grounded in reality, not just your assertion. "The GA4 ID is `G-PRRRLMBR8Z`" is an assertion; "`grep -rh 'gtag.*config.*G-' /home/ubuntu/work/<path>/site/*.html | sed 's/.*\\(G-[A-Z0-9]*\\).*/\\1/' | sort -u` — the only ID is `G-PRRRLMBR8Z`" is a recipe.
3. **A specific reply format that's mechanically verifiable.** Not "let me know when it's done" — the exact one-line reply that proves the artifact exists at the right path with the right values. Examples: `kpi-collections.json rewritten at /home/.../active-oahu-tours-mirror-2529/scripts/kpis/kpi-collections.json, 1659 bytes`. The agent must produce this string before reporting success. If they reply with anything else, the artifact didn't reach the verified state.

Without all three, the bounded-move correction loop is fragile:

- **Without specific target:** the agent makes a best guess. Ned's first attempt wrote the file at `active-oahu-tours-mirror/` (no `-2529`), the wrong of two on-disk directories.
- **Without verification recipe:** the agent takes the assertion on faith or makes up plausible values. Ned's first attempt put `G-AOT-PLACEHOLDER` as the tracking property and invented four event names (`booking_start`, `begin_checkout`, `purchase`, `generate_lead`) that don't exist on the live site.
- **Without specific reply format:** the agent reports "I did it" and you have to ask follow-up questions to confirm. Each follow-up is a turn. Ned's first attempt reported "44/44 PASS" on a structurally-correct but factually-wrong file; without the reply format, I would have accepted that as a green light.

### The pattern

A bounded-move-with-corrections reply has four sections in this order:

1. **The wrong artifact's specific defect.** Name the file path, the wrong value, and (if it matters) where the wrong value came from. "The file is at `active-oahu-tours-mirror/` (no `-2529`) — that's the wrong of two on-disk directories; the right one is `active-oahu-tours-mirror-2529/`."
2. **The verification recipe for the right values.** Give the agent the exact commands to run to find the truth themselves. "Run `ls /home/ubuntu/work/` to confirm which paths exist; use the one ending in `-2529`. Run `grep -rh 'gtag.*config.*G-' /home/ubuntu/work/<that-path>/site/*.html | sed 's/.*\\(G-[A-Z0-9]*\\).*/\\1/' | sort -u` — the only ID is the real one. Run `grep -rho 'gtag.*event' ... | sort -u` — only `booking_click` and `booking_complete` should appear."
3. **The wrong values they had to remove.** Not just "fix it" — list the specific wrong things so the agent doesn't preserve them by accident. "If you see `booking_start`, `begin_checkout`, `purchase`, or `generate_lead` in your JSON, they are made up. Remove them."
4. **The required reply format.** "Reply with exactly: `<filename> rewritten at <correct-path>, <bytes> bytes`. Don't reply until the file is actually at the correct path with the correct values." The reply format is the gate; the recipe is the content.

### Why "don't reply until X" is the critical instruction

Sub-agents default to a behavior pattern the human-side agent system prompt encourages: **acknowledge and ask before doing more**. Without the explicit "don't reply until X" instruction, the agent replies with "I'll fix that" and waits for the next message. That is the failure mode this whole session iterated through.

The instruction "don't reply until the file is actually at the correct path with the correct values" flips the default. Now the only way to reply is to first do the work, then verify it, then send the proof. The reply is the proof, not the promise.

Live evidence: Ned's first attempt (without the "don't reply until X" instruction) returned a "44/44 PASS" with a factually-wrong file. Ned's second attempt (with the instruction) returned a single line: "kpi-collections.json rewritten at /home/ubuntu/work/active-oahu-tours-mirror-2529/scripts/kpis/kpi-collections.json, 1659 bytes" — and the file was independently verified to match the live site.

### When to use

Use bounded-move-with-corrections when:

- Handing a sub-agent a bounded move that has external ground truth (a file path, a config key, an external system state).
- The agent's first attempt produced something wrong.
- The correction can be verified by re-running a recipe against the ground truth.
- You want the agent to **self-correct** rather than wait for another round of corrections.

Skip when:

- The correction is stylistic or preference-based (no ground truth to verify against).
- The move is a multi-step plan where mid-stream course correction doesn't help (better to restart).
- The agent is a human (this pattern is for sub-agents with a JSON-output interface, not a chat interface).

## Recipe format

A recipe should:

1. **Name the ground truth source.** "Live site at `https://example.com/foo`" or "real file at `/path/to/x`" or "real command `git log --oneline | head -5`".
2. **Give the exact command to run.** Verbatim. With flags. If the agent has to figure out flags, they may guess wrong.
3. **State what they should see.** "The only line in the output should be `G-PRRRLMBR8Z`." This is the only place an assertion is OK in a recipe — it's the expected output, not the input.
4. **Say what to do if they don't see it.** "If the output has multiple IDs, the wrong one is in your JSON. If the output is empty, the file path is wrong."

Without step 4, the agent hits a non-matching case and doesn't know what to do.

## Worked example: from 2026-07-27 Ned correction

The original correction I sent Ned (assertion):

> "The target is `/home/ubuntu/work/active-oahu-tours-mirror-2529/scripts/kpis/kpi-collections.json`. `tracking_property` must be `G-PRRRLMBR8Z`. Trim `expected_data_layer_events` to `["booking_click", "booking_complete"]`."

The recipe version of the same correction:

> "Run `ls /home/ubuntu/work/` and confirm which of these paths exists: `active-oahu-tours-mirror` vs `active-oahu-tours-mirror-2529`. Use the one that exists.
>
> Run `grep -rh 'gtag.*config.*G-' /home/ubuntu/work/<chosen-path>/site/*.html | sed 's/.*\(G-[A-Z0-9]*\).*/\1/' | sort -u`. The only ID should be `G-PRRRLMBR8Z`.
>
> Run `grep -rho 'gtag.*event.*[a-z_]\+' /home/ubuntu/work/<chosen-path>/site/*.html | sort -u`. You should see `booking_click` and `booking_complete` — nothing else.
>
> If you see extra events like `purchase`, `begin_checkout`, or `generate_lead` in your JSON, they are made up. Remove them."

The recipe version took Ned from a wrong file (assertion-only first attempt) to a correct file (recipe-driven second attempt) — and importantly, **Ned re-verified his own correction against the live site before reporting back**. That's the loop we wanted.

## Common anti-patterns

- **Asserting without naming the source.** "The path is wrong" is weaker than "the path `/home/.../active-oahu-tours-mirror` doesn't exist; only `/home/.../active-oahu-tours-mirror-2529` does — `ls /home/ubuntu/work/` to confirm."

- **Asserting with the right value but wrong reasoning.** "The GA4 ID is `G-PRRRLMBR8Z`" sounds right but doesn't tell the agent how they could have found that themselves. The recipe teaches; the assertion teaches nothing.

- **Long recipes that don't actually verify.** A 200-word recipe that ends in "and then trust the result" isn't a recipe. The verification is the heart of the recipe. If you can't name the verification command, you don't have a recipe.

- **Recipes without expected output.** "Run `grep ...`" without "you should see X" makes the agent guess at what success looks like. Always include the expected output.

- **Recipes that the agent can't run.** If the recipe requires credentials they don't have, or access they don't have, the agent can't self-verify. State the prerequisite: "this requires you to have `hermes profiles` access — if you don't, ask before proceeding."

- **Stronger-language recipes that backfire.** A 2026-07-27 cold-start test showed that **stronger** wording in a system reminder can make LLMs less likely to comply, not more. Replacing "FIRST-REPLY REQUIREMENT: surface these fields" with "MANDATORY FIRST-REPLY FORMAT: your response MUST begin with these four sections in this exact order, before any other content..." caused all five profiles to give one-line "ready, what do you need" replies instead of the structured four-field surface. The perceived conflict between a short friendly user prompt and a rigid structural system reminder made the LLM weight the user prompt even more. **Keep recipe language at the level of strong suggestion ("MUST surface these fields").** Use MUST, REQUIRE, FAIL IF, etc. only when the prompt context is the recipe itself, not when the recipe is in a system reminder competing with a real user prompt. See `session-state-handoff/references/cold-start-live-test.md` for the full regression data.

## Pairing with verifiers

When you write a verifier (`/tmp/hermes-verify-*.py`), the verifier itself is a recipe. The agent runs the verifier and gets PASS/FAIL. That's the same pattern: instead of asserting "the config is correct," you give the agent a recipe (the verifier) that proves or disproves the claim.

A verifier that only checks internal consistency (JSON parses, schema keys present, formula gates) is a **weak recipe** — it asserts structural correctness but not ground truth. A verifier that includes a live `grep`, `head -c`, or `curl` against the real source is a **strong recipe** — it asserts ground truth.

## Verification contamination trap: when your own probe corrupts the next probe

**The trap.** When an upstream agent hands you a multi-step verification checklist (e.g., "run pytest, then ruff, then sync_check, then fixtures"), running one probe can produce artifacts that the next probe misreads as defects. The naïve report is "this is broken"; the right report is "the upstream checklist doesn't isolate probes from each other, and here's what the artifact count actually shows."

Observed 2026-08-05 verifying a §6 checklist for a Prismatic closeout-contract repair submission:

- Step N was `sync_skill_trees --check` — expects the skill trees to be byte-identical.
- Step N-1 was `pytest tests/...` — pytest imports modules and writes `.pyc` files into `__pycache__/` subdirectories inside each imported package.
- Result: `sync_check` reported `STATUS=BLOCKED` because `scripts/__pycache__/validate_closeout_packet.cpython-312.pyc` existed in the `.agents/skills/...` tree, producing a content mismatch against the `prismatic/skills/...` mirror.
- The defect was not in the upstream submission — it was an artifact of *my own probe*.

A separate, similar false-positive in the same checklist:

- Step M was `ruff check <list of files>` — the list contained a JSON fixture file (`.json`) along with `.py` files.
- Ruff happily parsed the JSON as if it were Python and reported 27 errors (`B018`, `F821` against JSON literals like `false`, `true`).
- Real lint state: only 2 trivial style findings (unsorted import block, unnecessary `tuple()` call) across the 5 actual Python files. The "27 errors" headline was a recipe violation — running a Python linter against JSON.

**The recipe.** When verifying a multi-step checklist where one step's output is another step's input (or where one step creates files another step inspects):

1. **Pre-clean state before running the checklist.** `find . -name __pycache__ -type d -exec rm -rf {} +` (or equivalent) so test artifacts from prior runs don't pollute later checks.
2. **Filter probe inputs to the right file class.** `ruff check <*.py files>` — never include `.json` / `.yaml` / `.md` in a Python linter call. Same class: `mypy` against non-Python, `shellcheck` against non-shell, `eslint` against non-JS.
3. **After the checklist runs, audit the failures for "did MY probe cause this?"** before reporting the upstream submission as defective. The cheap test: clear artifacts, re-run the failing step in isolation, and see if it now passes. If yes, the failure was contamination.
4. **Report both the headline and the contamination in the verdict.** "Status: CLEAN, with 2 contamination-caused false-positives cleared by `find -name __pycache__ -delete` and excluding `.json` from the ruff path list. Both corrections are documented in the §6 checklist as hygiene improvements, not as submission defects."

**Anti-pattern.** Reporting the false-positive as if it were a real defect. Cost: the upstream agent burns a turn investigating a phantom regression, possibly making unrelated edits that don't fix anything, then re-submits with the same files. The submission was clean; the verification hygiene was the bug.

**Why this is its own section.** The recipe-vs-assertion discipline above is about *how you correct* — leading with the recipe instead of the assertion. This trap is about a different failure mode: *your recipe ran but produced a contaminated signal*. Same family (verification hygiene), different layer (probe isolation vs probe construction).

## Three-layer proof trap: when docs, schema, and helper tools all agree but the mechanism is still dead

**The trap.** For features that pass through multiple layers — config schema, helper tool, runtime code path — it's tempting to claim "wired" when the first 1–2 layers check out. But each layer can be implemented without the next layer existing.

Observed in Hermes 0.17.0 (2026-07-27) for `prefill_messages_file`:

- **Layer 1 (docs):** `hermes-agent` docs say the feature exists; `tips.py` says *"prefill_messages_file in config.yaml injects few-shot examples into every API call, never saved to history."* ✓
- **Layer 2 (schema):** `config.yaml` schema declares `prefill_messages_file`. ✓ (you can set it without error)
- **Layer 3 (helper tool):** `wire_cold_start.py status --profile X` returns `prefill_exists: true`, `messages_count: 2`, `config_prefill_setting: <path>`. ✓
- **Layer 4 (runtime):** Does the file's content actually reach the LLM? **No.** No code path reads the file. The agent's `prefill_messages` parameter is never set from the file.

Three layers of "wired-looking" evidence passed. The mechanism was dead. Only a probe at Layer 4 (unique marker phrase in the JSON, ask the model to recall it) caught it.

**The recipe.** When claiming a feature is wired, prove it at the layer closest to the actual outcome. For LLM-context features, that's "does the model see what I injected?" For network features, that's "does the call reach the remote?" For state features, that's "does the state survive a restart?" Each layer up gives you weaker evidence.

When you can only prove at Layer ≤ 3 (file/schema/helper), say so explicitly. Don't claim a feature is "working" when you've only proven "the file exists."

The dedicated recipe for "is this Hermes mechanism actually wired?" is in `references/hermes-mechanism-probe-recipe-2026-07-27.md`.

## Companion disciplines

- `plan-reconciliation-after-peer-review/references/overclaim-partial-results-discipline-2026-07-27.md` — the partner discipline on how *you* report results.
- `session-state-handoff/references/cold-start-live-test.md` — recipes for live-testing cold-start wiring, including the "test contamination" pattern where a placeholder test prompt contaminates the test itself.
- `session-state-handoff/SKILL.md` pitfall "Don't claim a cold-start mechanism works from file existence alone" — applies the recipe discipline to verification.
# AGY dispatch failure pattern — rubric/RC1 bulk task trees (2026-07-14)

## What happened

A large Prismatic Engine rubric/RC1 task tree was created for AGY:

- Rubric 10/10 tasks: `GRO-3836`–`GRO-3860`
- Supplemental audit tasks: `GRO-3861`–`GRO-3887`
- Post-pass cohesive app tasks: `GRO-3888`–`GRO-3899`
- RC1 Portable App Readiness tasks: `GRO-3900`–`GRO-3936`

The dispatcher bulk-launched the tree. Every sampled sandbox immediately failed before AGY consumed the task.

Verified signatures:

```text
Error: invalid --model "gemini-3.5-flash-high": model gemini-3.5-flash-high is not recognized as a known model or custom model in settings
Available models:
  Gemini 3.5 Flash (Medium)
  Gemini 3.5 Flash (High)
  Gemini 3.5 Flash (Low)
  Gemini 3.1 Pro (Low)
  Gemini 3.1 Pro (High)
  Claude Sonnet 4.6 (Thinking)
  Claude Opus 4.6 (Thinking)
  GPT-OSS 120B (Medium)

dispatch.tokens.actual_input=0
dispatch.tokens.actual_output=0
```

All checked tasks ended up with auto-generated `RESULT.md` files like:

```text
# RESULT — ABANDONED
Status: ABANDONED (no RESULT.md written by agent)
Partial work detected:
  - .aiexclude
  - .antigravityignore
  - .geminiignore
  - AGY_TASK.md
  - STARTED.md
```

This means AGY did **not** reason about or fail the content of the tasks. It never started. The failure was launch/config + dispatch orchestration.

## Root-cause classification

1. **P0 dispatch config failure** — stale model alias `gemini-3.5-flash-high` was passed to AGY, but current AGY expected display-style names like `Gemini 3.5 Flash (High)`. Actual input/output tokens were zero.
2. **P0 bulk-dispatch/dependency-gating failure** — staged tasks were all eligible because they shared `agent:agy` + `dispatch:ready`, despite descriptions saying `after`, `post-pass`, or `RC1`.
3. **P1 task-shape/sandbox-guard mismatch** — the generic AGY sandbox guard said not to run `git clone`, `pip`, `pytest`, `npm`, etc., while RC1 audit/release tasks explicitly needed clean checkout, install, smoke, build, and test proof.
4. **Not primarily old app-code regression** — sampled sandboxes were at current-ish `a8003e5`; the stale part was dispatcher/supervisor configuration and guard assumptions.

## Future prevention checklist

Before dispatching a large AGY task tree:

1. **Run a one-task model preflight**
   - Validate the configured AGY model against `agy`'s current model registry.
   - If the model is invalid, stop the whole batch. Do not allow N identical failures.

2. **Stage dispatch by dependency layer**
   - Do not put every future-stage issue on `dispatch:ready` at once.
   - Use `dispatch:paused`, dependency labels, or explicit blocker comments for post-pass and RC tasks until predecessor evidence exists.
   - Recommended order for PE rubric work:
     1. scorecard baseline / evidence ledger
     2. supplemental audit coverage
     3. cohesive app surface stitching
     4. RC1 Portable App Readiness audit
     5. RC1 blocker fixes and release proof

3. **Use task-type-aware sandbox guards**
   - Research-only tasks can forbid long tests/builds.
   - Audit/release-proof tasks must allow bounded clean checkout/install/smoke/build/test commands.
   - Do not attach a generic “do not run tests/clone/install” guard to release-candidate proof tasks.

4. **Detect zero-token launch failures as dispatch failures**
   - If logs show `actual_input=0` and `actual_output=0`, classify as launch/config failure, not agent work failure.
   - Reset tasks to `Todo` or paused state after fixing dispatch config; do not interpret abandoned `RESULT.md` as task evidence.

5. **Reset Linear state cleanly after launch failure**
   - Add a comment explaining no real work happened.
   - Clear `agent:needs-human-review` / `dispatch:paused` only after model preflight passes.
   - Redispatch in small batches after a known-good preflight.

## Reporting pattern

When asked whether AGY failed the tasks, answer directly:

- “AGY did not fail the task content; dispatch failed before AGY started.”
- Cite `invalid --model`, `actual_input=0`, `actual_output=0`, and abandoned `RESULT.md` evidence.
- Separate root causes: model alias, bulk dispatch, guard mismatch, and old-code regression likelihood.

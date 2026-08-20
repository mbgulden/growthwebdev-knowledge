# Darius Star playtest telemetry closeout pattern — 2026-07-17

Use this when a Golden Thread run selects a browser game / playable demo project and AGY recommends more assets, mobile controls, or architecture work before first-user measurement.

## What happened

- Registry + live Linear selected `darius-star` as oldest stalled non-done project.
- AGY research correctly favored **Playtest-Led Funnel Optimization** over more asset generation.
- AGY gap analysis hallucinated a missing mobile-touch-control gap.
- Live repo inspection showed `js/touch_controls.js` exists and `index.html` includes touch-control styles/scripts, so the correct task was a **regression gate**, not duplicate implementation.
- Existing branch `feature/gro-3832-first-session-telemetry` already contained first-session telemetry work.
- AGY execution exited 0 but included scratchpad/progress chatter (`I am waiting for...`). Treat that as non-evidence until direct verification passes.

## Durable pattern

1. Query live Linear non-done issues before creating new work.
2. Inspect local repo artifacts that would falsify AGY gap claims before trusting them:
   - `AGENTS.md`
   - `index.html`
   - relevant `js/*.js`
   - existing test files
3. Convert hallucinated missing-feature gaps into regression/verification tasks when the feature already exists.
4. For a playable demo, prefer first-session telemetry closeout before more content or asset production.
5. Do not move the task to Done if the PR is still open; move it to In Review with evidence.

## Verification commands used

From `/home/ubuntu/work/darius-star`:

```bash
python3 scripts/verify_syntax.py
node tests/telemetry_test.js
node tests/telemetry_integration_test.js
npm run build
git status -sb
gh pr list --repo mbgulden/darius-star --head feature/gro-3832-first-session-telemetry --json number,title,url,state,headRefName,baseRefName
```

Expected evidence shape:

- `verify_syntax: 47/47 passed`
- telemetry unit tests prove storage-failure isolation and sourcePath allowlist
- browser integration smoke emits `session_start`, `death`, and `replay_intent`
- `npm run build` exits 0, even if it reports the repo's expected no-build-step message
- branch is clean and tracking origin
- PR is open or merged; state transition must reflect that reality

## Task shaping

Top task should be a closeout/publish gate, not another implementation spike, when telemetry code already exists:

- Unit: telemetry adapter/sourcePath tests
- Integration: browser smoke for start/outcome/replay events
- Revenue: shareable playtest evidence tied to plays/completions/feedback
- Assumption: current vertical slice can or cannot produce measurable first-session data before paid asset work

Create follow-on backlog tasks only for gaps that remain after verification, such as portal SDK seam, preload bounce-risk measurement, and mobile-touch regression gates.

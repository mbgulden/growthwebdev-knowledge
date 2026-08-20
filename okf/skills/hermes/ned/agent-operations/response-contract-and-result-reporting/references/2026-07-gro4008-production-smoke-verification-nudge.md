# GRO-4008 production-smoke verification nudge pattern

Context: after a cron task was already finalized and reported, Hermes issued a verification-only nudge because changed code and RESULT artifacts were present but the detected verification evidence was stale/truncated.

Reusable pattern:

1. Treat the nudge as verification-only. Do not resume implementation or broaden scope.
2. Run the exact named canonical command from the task worktree. In this case: `npm run build` from `/tmp/hd-platform-gro4008`.
3. Run the task's focused verifier if one exists. In this case: `npm run verify:production-smoke`.
4. Add a fresh `/tmp/hermes-verify-*` ad-hoc artifact verifier when the nudge lists changed files or a RESULT artifact. It should assert:
   - changed source/docs files exist,
   - package script hooks point at the expected commands,
   - safety-critical source markers exist (for GRO-4008: unpaid-session guard, expiration-on-failure, HTML-fallback rejection),
   - RESULT.md contains PR/state/blocker evidence,
   - the temporary verifier is removed after running.
5. Report the fresh verification results only, plus one plain-English recap of what happened. Preserve blocker semantics: if the implementation verifies but live proof still fails, say `verified implementation; not green` rather than `done`.

Concrete GRO-4008 evidence shape:

- `npm run build` passed: Astro built 10 static pages and route-complete postbuild ran.
- `npm run verify:production-smoke` passed: smoke contract present/live-safe.
- `/tmp/hermes-verify-gro4008.py` passed and was removed.
- Remaining blocker: live report-delivery smoke returns `HTTP 200 text/html` for the synthetic PDF route, so the smoke correctly fails that as static fallback HTML rather than report delivery.

Pitfall: a successful live checkout smoke is not enough for a checkout/report-delivery task. If the report-delivery leg returns HTML fallback, keep the issue partial/In Review and call out the live blocker explicitly.
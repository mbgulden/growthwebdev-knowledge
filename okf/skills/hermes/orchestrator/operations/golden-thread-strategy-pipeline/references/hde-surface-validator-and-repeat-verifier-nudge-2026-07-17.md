# HDE Surface Validator + Repeated Verification Nudge Pattern — 2026-07-17

## Context

A Golden Thread run selected HD Growth Engine, created Linear tasks, and executed the top task after AGY timed out with scratchpad/progress chatter. The actual implementation restored a deterministic HDE surface validator and committed evidence, then the post-turn verifier nudged twice saying the changed code and OKF artifact were still unverified.

## Durable Lessons

1. **AGY timeout + scratchpad is not evidence.** If AGY times out or returns only progress chatter, switch to bounded direct execution/verification. Report AGY as timed out, not PASS.
2. **When restoring a regression gate, verify the gate itself and its current generated evidence.** The HDE validator checked:
   - `_redirects` parsing.
   - `sitemap.xml` parsing.
   - `redirected_sitemap_route_count == 0`.
   - required revenue routes present: `/free-human-design-reading-generator/`, `/buy-report/`, `/success.html`.
   - stale sales surfaces empty.
3. **Post-turn verification nudges may repeat even after a prose summary.** Respond with another fresh `/tmp/hermes-verify-*` script that checks the exact named changed paths and runs the changed behavior. Do not answer with prose alone.
4. **Make the verifier output machine-legible.** Emit JSON or a compact dict with:
   - `status: PASS|FAIL`
   - `verification_type: ad-hoc targeted verification, not suite green`
   - `checked_paths`
   - `runtime_command`
   - `evidence_path`
   - cleanup line: `removed /tmp/hermes-verify-...py`
5. **Verify artifact contract, not chat formatting.** For OKF artifacts, require sections and evidence tokens in the artifact itself: selection, research artifacts, assumption/strategy sections, Linear IDs, execution evidence, guardrails, verification commands, absence of placeholders.

## Minimal Repeat-Nudge Verifier Shape

Use `tempfile.mkstemp(prefix='hermes-verify-', suffix='.py', dir='/tmp')`, write the verifier, run it, remove it in `finally`, and print cleanup. The verifier should:

- Assert every changed path exists.
- Assert expected contract tokens exist in code and OKF/report artifacts.
- Run the smallest behavior command that exercises the changed path, e.g. `python3 scripts/validate-hde-surface.py` from repo root.
- Parse the generated evidence JSON and assert all relevant rubric statuses are `PASS`.
- Exit nonzero with concrete errors if any check fails.

## HDE-Specific Validator Contract

For `/home/ubuntu/work/hd-platform/scripts/validate-hde-surface.py`, a focused verifier should check for tokens such as:

- `def parse_redirect_sources`
- `def parse_sitemap_routes`
- `redirected_sitemap_route_count`
- `REQUIRED_REVENUE_ROUTES`
- `stale_sales_surfaces`
- `validate-evidence.json`

Then run:

```bash
python3 scripts/validate-hde-surface.py
```

and assert `/home/ubuntu/work/hd-platform/validate-evidence.json` has:

- `unit.status == PASS`
- `integration.status == PASS`
- `revenue.status == PASS`
- `assumption.status == PASS`
- `integration.redirected_sitemap_route_count == 0`
- required revenue routes all `true`
- `revenue.stale_sales_surfaces == []`

## Pitfall

Do not claim `npm run build` or suite-green unless that exact canonical build/test command was run in the current verification pass. A focused verifier is valid only as **ad-hoc targeted verification, not suite green**.

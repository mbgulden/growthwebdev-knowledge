# Proof Loop demo wedge pattern — 2026-07-08

## When this applies

Use this pattern when a Golden Thread / Prismatic Proof Loop task asks for a demo, sales wedge, or externally understandable proof loop. The deliverable is not just code; it is a replayable artifact a non-internal viewer can understand quickly.

## Exit criterion shape

A valid demo wedge should prove:

`issue/event trigger → governed routing decision → bounded agent/work fixture → verification verdict → cleanup status`

For the Prismatic Proof Loop 2 example, the explicit parent criterion was:

> A non-internal viewer can watch/run the demo and understand the differentiated wedge in under 90 seconds, with reproducible fixture evidence.

## Recommended implementation pattern

1. **Prefer a deterministic fixture before a live integration.**
   - Build a script that simulates the Linear/GitHub trigger without production API calls.
   - Include enough realistic fields to demonstrate the path: issue identifier, labels, repo/branch/event, expected agent, verification command.
   - Keep the fixture replayable and non-destructive.

2. **Generate a complete artifact bundle in one command.**
   A good demo smoke writes:
   - `fixture-event.json` — replayable trigger fixture.
   - `demo-evidence.json` — timestamped trigger/routing/execution/verification/cleanup evidence.
   - `demo-script.md` — 90-second operator/founder narrative.
   - `capture-checklist.md` — exact recording steps and expected outputs.
   - `three-user-feedback-package.md` — short message + focused feedback prompts.
   - a tiny bounded work product fixture, e.g. `demo_workspace/agent_output.py`.

3. **Make the script itself judge publishability.**
   - Print a concise verdict (`PASS`/`FAIL`), run ID, routed agent, scope, output dir, cleanup status, and JSON summary.
   - The script should exit non-zero if any required stage is missing or unverified.

4. **Keep scope labels explicit.**
   - Fixture demos are usually `ad hoc targeted fixture verification`, not canonical/full-suite green.
   - State whether real Linear/GitHub/orchestrator calls were made. For fixture runs, this should be `0`.

5. **Use a `/tmp/hermes-verify-*` verifier after edits.**
   Verify at minimum:
   - `py_compile` for the demo script.
   - `ruff check` and `ruff format --check` for changed Python.
   - demo smoke exits 0.
   - evidence JSON has `PASS`, deterministic run ID/routed agent, required stages, cleanup status, and zero real API calls.
   - docs/evidence comment include scope, issue reference, verdict, and live-integration blocker.
   - clean up the verifier file after running.

6. **Post or save evidence before moving task state.**
   - If Linear is healthy, post the evidence comment.
   - If Linear is rate-limited/cooldown is active, save a Linear-ready evidence comment locally and do not burn API budget.
   - Do not move the epic/task to Done if the branch cannot be shared or pushed, even if the local fixture passes.

## Pitfalls caught

- A demo wedge that only describes the workflow is insufficient. It needs a runnable fixture and evidence bundle.
- A live integration blocker should not erase fixture progress. Report the fixture as verified and the live path as blocked.
- Do not conflate fixture proof with live webhook delivery. Call out the live-integration blocker separately.
- If Git push fails after a verified local commit, do not mark the task Done; the share/publish path is part of demo readiness.

## Minimal command shape

```bash
python3 scripts/proof_loop_demo_wedge.py --output-dir artifacts/proof-loop-demo-wedge/latest --clean
```

Expected summary shape:

```text
Verdict: PASS
Run ID: demo-...
Routed agent: orchestrator
Scope: ad hoc targeted fixture demo; no production Linear/GitHub/orchestrator calls; not canonical/full-suite green
Cleanup: clean
```

# 2026-07 Prismatic worktree usefulness proof layer

Session learning: preserving all ambiguous work avoids accidental deletion, but creates rot unless the system also pressures agents to make useful work legible. The durable pattern is safety gates + portable proof + promotion pipeline.

## What changed conceptually

The earlier guarantee was:

> Anything not mechanically proven disposable is preserved.

Michael pushed the next question: how do we guarantee agent work becomes proven useful/indispensable, so only truly broken work is trashed and undocumented good work does not rot forever?

The answer is not a smarter deletion heuristic. It is a portable proof/provenance layer:

> Missing proof preserves work and creates a proof gap; it never makes work disposable.

## Recommended record model

Worktree records should expose both safety and usefulness:

- `safety_class`: `safe-remove`, `keep`, `manual-review`, `safe-prune-metadata`
- `safety_reasons`
- `value_class`: `indispensable`, `preserve-needs-proof`, `broken-review`, `disposable`, `unknown`
- `value_score`
- `value_signals`
- `proof_gaps`
- `promotion_recommendation`

## Portable proof bundle

Use JSON files that travel with the worktree:

- `.prismatic/worktree-proof.json`
- `prismatic-worktree-proof.json`
- `.worktree-proof.json`

Suggested fields:

```json
{
  "schema": "prismatic.worktree-proof.v1",
  "issue": "GRO-1234",
  "summary": "What changed and why it matters",
  "verdict": "useful",
  "agent": "ned",
  "created_at": "ISO-8601",
  "verification": [{"command": "pytest ...", "result": "passed"}],
  "artifacts": [],
  "handoff": "Next action for human/agent"
}
```

Verdicts: `useful`, `indispensable`, `promote`, `blocked`, `broken`, `superseded`.

## Routing rules

- `indispensable` / `promote` → open/update PR or Linear comment.
- `preserve-needs-proof` → assign proof-capture/review; do not delete.
- `blocked` → route to correct agent/human lane.
- `broken-review` → require explicit disposal review.
- `disposable` → safe janitor target when safety gates pass.

## Verification pattern

Focused tests/ad-hoc verifier should prove:

1. Dirty undocumented work becomes `preserve-needs-proof` and `manual-review`.
2. Proof-backed work with verification becomes `indispensable` and recommends `promote`.
3. Missing proof never creates `disposable`.
4. CLI/API both expose the same fields.

## Communication note

When reporting this to Michael, avoid raw log sludge. Translate into trust decisions: preserved, needs proof, promotable, blocked, disposal-review, or safe-remove.

# GRO-4317 detector tempfile verifier pattern

Session-specific detail from the GRO-4317 exact-head repair lane, condensed into a reusable detector response.

## What happened

After code/test edits, the workspace detector repeatedly reported changed paths as unverified even after a passing proof packet. The durable response was **not** to argue that the detector missed the proof. The safe response was to rerun a small idempotent proof in the detector's requested shape and keep the boundary explicit.

## Reusable pattern

- Generate the verifier path under `/tmp` with `tempfile` and prefix `hermes-verify-`.
- Make the verifier assert exact head/tree/clean tracked state and the changed behavior.
- Run the focused behavior test(s), then the broader focused suite when recognition remains brittle.
- Run lint/format/compile/diff checks as visible commands.
- Delete only the disposable verifier script; keep and hash the proof log.
- Report `AD_HOC_OR_CANONICAL=ad-hoc targeted` and avoid claiming canonical suite green unless a canonical suite actually ran.

## Pitfall

A `/tmp/hermes-verify-*` **script** and a `/tmp/hermes-verify-*` **proof log** have different lifetimes. The script should usually be cleaned up. The log is evidence and should remain available with a hash while the review/acceptance lane is open.

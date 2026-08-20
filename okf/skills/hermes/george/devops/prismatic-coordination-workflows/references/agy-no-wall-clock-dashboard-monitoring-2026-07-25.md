# AGY no-wall-clock runtime + dashboard activity monitoring (2026-07-25)

## Durable lesson

AGY canonical runs must be progress-supervised, not time-bounded. The user explicitly rejected a 10-minute cap and restated that AGY must be allowed to run as long as needed while the Prismatic dashboard monitors whether it is still working.

## Required contract shape

- Runtime deadline is `null` / no PE wall-clock cap.
- The AGY CLI may require a print-mode duration argument; treat any huge duration bridge as protocol plumbing, not PE policy.
- Do not expose configurable task timeouts as the canonical PE AGY control path.
- Harness capability should advertise `supports_timeout=false` and `supports_cancel=true` when timeout would imply PE can terminate a run by elapsed time.
- Quiet/suspect/stale classifications are dashboard review evidence only; they must not automatically kill the producer.
- Cancellation must be explicit and exact-run-scoped.

## Activity receipt fields to preserve

For dashboard monitoring and later review, durable receipts should include enough exact-run evidence to distinguish `working`, `quiet`, `suspect`, and `terminal` without leaking secrets:

- run ID / manifest path / process-result path / activity path;
- child PID and process start ticks;
- process-tree count;
- cumulative CPU ticks;
- read/write bytes;
- artifact count and artifact bytes;
- latest artifact timestamp;
- activity sequence;
- last progress timestamp and quiet duration;
- runtime deadline (`null`);
- automatic kill flag (`false`);
- verification state.

## Proof pattern that mattered

Use an explicit quiet-period survival probe, not just static source checks:

1. Launch a real canonical/tmux producer.
2. Force it into a deliberately quiet period longer than the dashboard `quiet` threshold.
3. Verify the dashboard/activity API classifies it as quiet or suspect while the process remains alive.
4. Let it complete normally.
5. Verify cleanup and terminal receipt.

This proves the policy property the user cares about: crossing an inactivity threshold does not kill AGY.

## Dashboard requirements

- Reuse the existing canonical dashboard shell; do not make a mini/fallback dashboard the primary experience.
- The panel copy should be explicit: `No wall-clock cap · monitor only`.
- If runtime storage is unavailable, render a truthful unavailable/empty state, not mock live data.
- API output should omit admission tokens and expose dashboard-safe exact-run evidence.

## Reporting boundary

When reporting this class of work, keep claims separate:

- targeted no-kill/quiet-period proof;
- dashboard API proof;
- rendered browser proof;
- wheel/release smoke proof;
- full-suite collection status;
- independent exact-head review status;
- production/deploy status.

Do not claim canonical full-suite green if broader collection is blocked by unrelated repo layout/import errors. Report that as a boundary with the log path and affected collection class.
# AGY unlimited runtime with progress supervision

Session lesson: when canonicalizing PE AGY CLI workflow, do **not** turn AGY's `--print-timeout` requirement into a Prismatic Engine wall-clock deadline.

## Contract

- PE AGY runtime deadline is `null` / no wall-clock cap.
- `--print-timeout` is only an AGY protocol bridge because AGY requires a Go duration for `--print` mode.
- A zero duration can mean immediate timeout; do not use `0s` as "unlimited" without probing the live binary.
- If a duration argument is required, use the maximum accepted whole-second Go duration as a bridge (historically `2562047h47m16s`) and label it clearly as **not** a PE runtime cap.
- Do not auto-kill because a run is long, quiet, or suspect.
- Cancellation must be explicit operator/governed policy and must target the exact admitted run/session/process tree.

## Dashboard/activity model

Long AGY tasks should be monitored through durable exact-run activity receipts, not timeouts:

- exact run/session id;
- exact child PID and process start identity;
- process-tree count;
- CPU ticks;
- read/write bytes;
- log/artifact count and byte growth;
- newest artifact timestamp;
- last observed progress timestamp;
- quiet duration;
- classification: `working`, `quiet`, `suspect`, or `terminal`;
- `runtime_deadline: null`;
- `automatic_kill: false`.

Classifications are dashboard/operator signals only:

| Classification | Meaning | Action |
|---|---|---|
| `working` | CPU/I/O/log/artifact/process-tree progress observed | continue |
| `quiet` | short no-progress interval | display only |
| `suspect` | extended no-progress interval | investigate or explicitly cancel exact run |
| `terminal` | process exited and receipt exists | collect result and verify |

## Verification pattern

When proving this class of work:

1. Probe the live AGY binary's timeout parsing rather than assuming `0s` or a blank timeout is accepted.
2. Assert the canonical contract exposes `runtime_deadline is None` and `runtime_policy == no-wall-clock-cap-progress-supervised`.
3. Assert harness capabilities report `supports_timeout=false`, `activity_receipts=true`, and explicit cancel support.
4. Run a fake long producer that stays alive beyond the former timeout threshold and writes periodic artifacts/logs.
5. Verify activity receipts update and dashboard/API reports `working` without automatic termination.
6. Verify explicit cancel cleans only the exact run and writes a cancellation receipt.

## Pitfall

Historical swarm supervisors used warning/kill/retry windows because earlier AGY runs died around fixed boundaries. Preserve the useful activity signals, but do not preserve wall-clock kills as PE Core policy. Long legitimate work must remain observable rather than arbitrarily terminated.

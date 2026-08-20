# Agentic-swarm-ops → PE canonical AGY workflow deep-dive

Use this as a session-specific detail bank for future PE AGY launcher/harness reviews.

## Key finding

The predecessor workflow had useful operator ergonomics but unsafe lifecycle semantics. The highest-risk defect was treating a short launcher-survival check as if AGY completed work. Future PE work must preserve the distinction:

```text
launch_acknowledged != producer_completed != independently_verified != accepted/merged/deployed
```

## Useful patterns to preserve

- Durable `tmux` session as the unattended AGY anchor.
- Short `/goal` prompt plus detailed frozen Markdown task file.
- Plan-first discipline before code edits.
- Durable result artifact with a stable machine marker.
- Separate stdout/stderr/diagnostics logs.

## Patterns to reject or repair

- Raw detached `Popen` supervisors or bespoke one-off launch scripts when PE has a canonical CLI/harness.
- Dispatcher advancement after only a few seconds of launcher survival.
- Global mtime result selection from a shared brain/result directory.
- Mutable executable paths without SHA-256 binding.
- `pgrep -f` or global process cleanup instead of exact tmux session/pane/PID/start-time identity.
- World-writable artifact/runtime modes.
- Generic checkpoint commits such as `git add -A` from a producer.
- Prompt instructions that forbid comments while stall/heartbeat logic depends on comments.
- Tests/scripts that exit during import and therefore cannot serve as normal pytest suites.

## PE integration checklist

When engraving a predecessor workflow into Prismatic Engine, update and verify these together:

1. Stable CLI front door, e.g. `prismatic agy contract|render|launch|wait`.
2. Runtime contract: `/goal`, max prompt length, frozen task file, result marker, plan/result paths, timeout, sandbox, isolated home, minimal environment.
3. Admission receipt: explicit authorization, event id, attempt, attempt token, task SHA, executable SHA, receipt digest.
4. Replay/cap control: durable token ledger and active-slot ledger; mismatched replay fails closed.
5. Harness lifecycle: advertised registry module exists and persists state after PE restart; producer completion remains verification-pending.
6. Packaging: registry JSON and harness module included in wheel/sdist; clean-room non-editable install proves import/CLI outside source checkout.
7. OKF/docs/release smoke: contract, ADR, research, evidence map, public smoke, and release smoke all point to the same canonical workflow.

## Proof boundaries to report

Use compact packets and do not overclaim:

- Focused AGY CLI/harness tests are `AD_HOC_OR_CANONICAL=ad-hoc targeted`.
- Existing AGY-surface regression suites are not canonical full-suite green.
- Public/release smoke does not imply deployment.
- Wheel clean-room proof does not imply a published release.
- A background full-suite run is not evidence until its result is read and bound to the exact final tree.
- New edits after proof require fresh verification before claiming the latest working tree is green.

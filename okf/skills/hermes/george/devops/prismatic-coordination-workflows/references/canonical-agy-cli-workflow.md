# Canonical AGY CLI Workflow Lessons

Use this reference when coordinating Prismatic Engine AGY work, especially when porting or reviewing unattended AGY producer launches.

## Durable lesson

Do not let PE agents or operators rebuild one-off AGY launchers when a canonical workflow exists. The canonical AGY path must be executable, documented, OKF-linked, and tested so it stays at the foreground of operator behavior.

A launch receipt is not completed work. Treat AGY as an untrusted producer whose process/result artifacts must be collected and independently verified before any downstream task transition, PR admission, merge, release, or deploy. If a dispatcher only waits briefly to see whether the launcher crashes, that is a launch-acknowledgment gate, not a completion gate.

## Canonical PE integration surfaces

When engraving AGY into Prismatic Engine, preserve all four surfaces together:

1. **Stable CLI** — `prismatic agy contract|render|launch|wait`, with the canonical `/goal` prompt prefix and explicit `PRISMATIC_AGY_RESULT_V1` result marker.
2. **Harness module** — if `prismatic/harnesses/registry.json` advertises `prismatic.harnesses.agy_cli`, the module and class must exist, implement the current `AgentHarness` lifecycle, and persist enough state to survive PE restarts.
3. **Packaging/clean-room proof** — the registry JSON and harness module must be included in wheels/sdists; non-editable clean-room installs must prove CLI and harness import outside the source checkout.
4. **OKF/docs/release smoke** — canonical AGY contract, ADR, research/deep-dive, OKF evidence map, public smoke, and release smoke should all point to the same workflow contract so legacy one-off launchers do not drift back into use.

## Canonical shape to preserve

- Launch AGY through the PE canonical CLI front door, not raw detached `Popen` or bespoke scripts.
- Use a durable `tmux` anchor with a unique session name and exact-session cleanup.
- Keep the operator-facing goal short: `/goal ...`, max roughly 1,200 characters.
- Put detailed scope in a frozen task file; bind that file by digest in the manifest/receipt.
- Require a reviewed admission receipt before real execution; bind event id, attempt number, attempt token, task SHA-256, executable SHA-256, and receipt digest into retained launch evidence.
- Use replay protection and cap control for unattended producer launches: same token + same bindings may return the existing run; mismatched replay must fail closed; active-slot ledgers should enforce the configured concurrency cap before launch.
- Keep producer completion separate from verification/admission. A zero AGY exit plus valid result marker means `producer_completed=true` and `verification_status=pending`, not downstream approval.
- Bind launch evidence to workflow version, AGY executable path/hash, task digest, manifest digest, tmux session, pane PID, and `/proc` start ticks where available.
- Keep stdout, stderr, and AGY `--log-file` diagnostics as separate evidence streams.
- Use an explicit, isolated AGY home and a minimal allowlisted child environment; do not inherit unrelated operator/provider secrets.
- Keep AGY as an untrusted producer: no self-admission, no Linear/GitHub writes unless explicitly authorized, no PR approval, no merge/deploy/restart, and no acceptance of its own output.
- Retain containment ceilings and retry policy in the contract: warn on stalls, externally contain long runs, and cap attempts.

## What to mine from agentic-swarm-ops

Good patterns to port:

- `tmux` as the durable anchor for unattended AGY.
- Short `/goal` prompt plus detailed markdown task file.
- Plan-first discipline and durable book-end artifacts.
- Separate stdout/stderr/diagnostic logs.
- Explicit result marker for machine review.

Do not port unchanged:

- world-writable modes such as `0777`;
- mutable auto-updating binaries without hash binding;
- broad `pgrep -f` process matching;
- choosing results by newest brain-directory timestamp;
- generic checkpoint auto-commits;
- workstation-specific absolute paths;
- wrappers that lose exact child exit status or process identity;
- dispatcher logic that equates a short post-launch survival check with producer completion;
- registry/docs entries that advertise a harness or CLI entrypoint not included in the installed wheel.

## Agentic-swarm-ops deep-dive checks to repeat

When asked to pull lessons from `agentic-swarm-ops` or a similar predecessor repo, do not only read docs. Compare the live launcher, dispatcher, supervisor, watchdog, tests, and packaging surfaces. Specifically check for:

- contradictory timeout layers and stale-process cleanup windows;
- result/artifact selection by global mtime rather than launch-bound paths;
- prompt instructions that forbid comments while stall logic depends on comments;
- mutable executable paths or auto-updaters that are not hash-bound in receipts;
- child environments that inherit broad operator credentials;
- missing installed-package data such as harness registries;
- tests/scripts that exit at import time or otherwise cannot be collected as normal pytest tests.

## Verification standard

A valid proof packet should separate:

```text
COMMAND=<exact command or grouped command>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=<scope>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=<non-claims>
MARKER=<marker>
```

Reject wrapper receipts that return success while hiding missing modules, swallowed exit codes, or partial execution. Rerun with explicit sequential exit-code handling and known-good environment before claiming green.

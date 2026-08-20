# AGY headless runtime stability and timeout triage

Use this reference when a Prismatic AGY producer, one-shot consumer, or supervised launcher fails around a wall-clock boundary, especially near five minutes.

## Durable lesson

Do not assume a pinned AGY path is immutable just because the launcher checked its hash before spawn. AGY can spawn a background updater at startup and replace the executable path while the old process is still running. That can invalidate later retry/review assumptions and make path names such as `agy-bin-1.1.6` stale.

## Required triage sequence

1. Preserve the raw producer/AGY logs before changing anything.
2. Extract a timestamped process timeline from AGY diagnostics:
   - version line;
   - updater spawn line;
   - update-success receipt/status;
   - signal line such as `Got signal terminated, shutting down`;
   - print-mode timeout line and poll count.
3. Compare the pre-launch binary hash/version with the current hash/version/mtime of the same path.
4. Check AGY updater status files under both the runtime HOME and the controlling user HOME when applicable:
   - `~/.gemini/antigravity-cli/updater/update_status.json`
5. Verify timeout syntax independently with short probes before concluding a flag was malformed. Both separated and equals forms may be valid depending on version, so test exact runtime behavior.
6. Run a long control probe with explicit `--print-timeout=<longer-than-boundary>` before retrying production work.
7. Compare the failed launch transport against the canonical orchestrator/`agentic-swarm-ops` AGY dispatcher before writing a custom supervisor. Current Prismatic AGY dispatches use a wrapper that anchors AGY in a uniquely named tmux session; raw detached `Popen` is not equivalent and can recreate the background/SIGTERM class. See `references/agy-canonical-tmux-transport.md`.
8. Treat descendant process escape as a separate blocker: if AGY exits while a terminal command keeps running, the wrapper/supervisor must contain and reap the process group.

## Remediation pattern

Before retrying a failed producer after an AGY timeout/update event:

- Create a genuinely immutable runtime copy in a dedicated version directory that AGY's updater cannot replace.
- Patch the secured wrapper to execute that exact binary, not a mutable PATH target or misleading version filename.
- Pin both wrapper and binary hashes in the supervisor or admission artifact.
- Use explicit long print timeout syntax, e.g. `--print-timeout=30m`.
- Set supervisor deadline longer than the AGY print timeout.
- Add process-group/session containment and cleanup so shell/tool descendants cannot outlive AGY.
- Require independent exact-artifact review before retry authorization.

## Reporting boundary

Separate these claims:

- Proven: the path mutated, the process received SIGTERM, and print mode reported timeout.
- Not proven unless directly evidenced: the updater itself sent SIGTERM.
- Not authorized: a retry, candidate acceptance, or scale-up based only on targeted timeout proof.

## Compact proof block template

```text
COMMAND=<timeline/hash/updater-status/probe command summary>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=AGY headless runtime stability / timeout triage
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=retry authorization, full-suite green, or that updater sent SIGTERM unless directly proven
MARKER=AGY_HEADLESS_RUNTIME_STABILITY_TRIAGED
```

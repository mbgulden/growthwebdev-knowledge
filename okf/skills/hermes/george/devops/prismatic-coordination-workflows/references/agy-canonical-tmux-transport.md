# AGY Canonical Durable Transport

## When to use

Use this reference whenever Prismatic launches or debugs AGY/Antigravity CLI producers, especially for one-shot consumers, exact-artifact admission lanes, or unexplained deaths near a fixed wall-clock boundary.

## Durable lesson

Do not invent a fresh raw `subprocess.Popen`/detached-shell supervisor for AGY when the swarm already has a canonical transport. First inspect and port the live `agentic-swarm-ops` dispatcher pattern.

Canonical production shape observed in the orchestrator lane:

```text
agent_dispatcher.py
  -> /home/ubuntu/.local/bin/launch_agy_with_artifact.py
  -> uniquely named tmux session
  -> AGY/Antigravity CLI
```

The dispatcher detaches only the wrapper. The wrapper anchors AGY in tmux, monitors exit, preserves artifacts, and handles cleanup/checkpoint behavior. Raw detached `Popen(start_new_session=True)` can reproduce the known background/SIGTERM class and should not be treated as equivalent durability.

## Pre-retry investigation checklist

Before retrying a failed AGY launch:

1. Preserve launcher/stdout/stderr/AGY logs before changing anything.
2. Record the exact AGY binary path, version, sha256, mtime, and permissions from both launch time if available and current time.
3. Check whether a background updater replaced the executable while an older process was still running.
4. Compare the failed launch transport against the canonical dispatcher/wrapper in `agentic-swarm-ops` and the orchestrator profile.
5. Run a long explicit control probe, e.g. `--print-timeout=10m` with a workload exceeding five minutes, in an isolated test workspace.
6. Distinguish a universal AGY timeout ceiling from a noncanonical transport/mutable-runtime failure.
7. Contain any flawed launchers by removing execute permission or otherwise fail-closing before designing a retry.

## Canonical launch controls to preserve

- Start bounded AGY prompts with `/goal`.
- Keep the inline prompt short and place detailed task contracts in a dispatch file or equivalent artifact.
- Use explicit `--print-timeout`; do not rely on assumed defaults.
- Separate stdout/result capture from diagnostic logs where possible.
- Use a uniquely named, owner-controlled tmux session for durable AGY anchoring.
- Bind ledger/running identity to the exact tmux session and AGY PID/start ticks when operating a cap-one or exact-artifact launcher.
- On timeout/failure, kill only the exact owned tmux session/process group and prove no descendants remain.

## Exact-artifact lane caveats

The generic `launch_agy_with_artifact.py` is reference material, not automatically safe to call unchanged from an exact-artifact admission lane. Before reuse, review whether it:

- calls a mutable AGY path that may auto-update;
- performs broad checkpoint commits outside the task's acceptance contract;
- returns the exact AGY exit status needed by the caller;
- has permissions suitable for the threat model;
- scopes artifact discovery tightly enough for concurrent producers.

For exact-artifact launchers, port the transport pattern and harden the implementation rather than blindly shelling out to the generic wrapper.

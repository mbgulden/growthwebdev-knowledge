---
name: agy-session-recovery
description: Recover from crash loops, clean stale processes, and check watchdog files.
version: 1.0.0
---

# AGY Session Recovery

Diagnose hung tasks, terminate deadlocked child processes, and check watchdog output logs.

## Trigger Conditions

Use this skill when AGY outputs freeze, commands time out, or the watchdog detects stalling.

## Numbered Steps with Exact Commands

1. **Identify orphaned background processes**:
   Look for running `agy` or `agy-bin` tasks:
   ```bash
   pgrep -f agy-bin
   ```

2. **Clean up crash loops**:
   Kill orphaned tasks to free system ports and resources:
   ```bash
   kill -9 $(pgrep -f agy-bin) 2>/dev/null
   ```

3. **Check watchdog progress logs**:
   Inspect the orchestrator's CLI log output:
   ```bash
   tail -n 100 $HERMES_PROFILE/home/.gemini/antigravity-cli/logs/watchdog.log 2>/dev/null || echo "No log found"
   ```

4. **Verify process cleanup**:
   Check that no processes remain:
   ```bash
   pgrep -f agy-bin
   ```

## Pitfalls

- **Watchdog False Positives**: Do not panic on `history_truncation_error` logs. They are benign startup messages.
- **Ignoring D-state PIDs**: processes deadlocked in D-state cannot be cleaned by simple kills. Run `ps` to find them and force-kill the parent process or script.

## Verification Steps

- Ensure `pgrep -f agy-bin` returns empty.

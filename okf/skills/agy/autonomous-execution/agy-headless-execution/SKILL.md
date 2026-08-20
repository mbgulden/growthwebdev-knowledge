---
name: agy-headless-execution
description: Multiplex long-running execution commands via tmux.
version: 1.0.0
---

# AGY Headless Execution

Keep background tasks running and capture logs safely without session disconnects.

## Trigger Conditions

Use when launching long-running processes (e.g., development servers, big scraper runs, test suites) that must survive CLI resets.

## Numbered Steps with Exact Commands

1. **Verify tmux presence**:
   ```bash
   tmux -V
   ```

2. **Launch detached tmux session**:
   Create a session named `agy-runner`:
   ```bash
   tmux new -s agy-runner -d
   ```

3. **Send commands to the session**:
   Execute the long process:
   ```bash
   tmux send-keys -t agy-runner "npm run dev > /tmp/dev-server.log 2>&1" C-m
   ```

4. **Monitor progress**:
   Check logs or dump session output:
   ```bash
   cat /tmp/dev-server.log
   ```

5. **Kill session when done**:
   ```bash
   tmux kill-session -t agy-runner
   ```

## Pitfalls

- **Frozen interactive prompts**: Commands requiring user input inside a detached tmux session will hang. Always pass flags like `-y` or `--non-interactive`.
- **Duplicate tmux sessions**: Clean up abandoned sessions to prevent background CPU waste.

## Verification Steps

- List active sessions:
  ```bash
  tmux list-sessions | grep "agy-runner"
  ```
  Ensure the session is running.

---
name: agy-sandbox-security
description: Execute bash scripts safely inside sandboxed environments and avoid mounting deadlocks.
version: 1.0.0
---

# AGY Sandbox Security

Safely run CLI scripts, verify permissions, set environment constraints, and avoid lockups.

## Trigger Conditions

Use when running external commands, handling user uploads, or navigating mounted directory paths.

## Numbered Steps with Exact Commands

1. **Identify mount pathways (avoid deadlocks)**:
   Never run broad recursive directory commands on user workspace. Check active mount points:
   ```bash
   mount | grep -i fuse
   ```
   Avoid entering `/home/ubuntu/mounts/synology-*` or similar SSHFS/network folders.

2. **Check for deadlocked processes**:
   Look for processes stuck in D state (uninterruptible sleep):
   ```bash
   ps -e -o pid,state,wchan,cmd | awk '$2=="D"'
   ```
   If a process is stuck in D state, force kill it:
   ```bash
   kill -9 <PID>
   ```

3. **Enforce command constraints**:
   Set timeout limits on execution commands to prevent infinite wait cycles.

## Pitfalls

- **Synology Mount Deadlocks**: Running `find` or `grep` recursively under `/home/ubuntu` will stall on Synology NAS directories. Always use `-xdev` or exclude mounts.
- **D state processes**: Processes stuck waiting on network storage cannot be terminated by `SIGTERM`. Use `kill -9`.

## Verification Steps

- Verify no D-state processes are running:
  ```bash
  ps aux | awk '$8=="D"' | grep -v grep
  ```
  Ensure it returns no rows.

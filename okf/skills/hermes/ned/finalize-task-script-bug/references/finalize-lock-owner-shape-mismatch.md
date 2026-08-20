# Finalize lock-owner shape mismatch

## Trigger

After running `/home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh` with `FINALIZE_LOCK_FILES`, the transcript says the files were unlocked, but `node /home/ubuntu/.antigravity/swarm.js status` still shows active locks.

## Why it happens

`finalize_task.sh` uses the legacy three-argument unlock shape:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock "$file" prismatic-engine "$AGENT_ID"
```

Some cron runs acquire locks with the simple owner shape instead:

```bash
node /home/ubuntu/.antigravity/swarm.js lock <repo-relative-path> ned
```

Those are different lock-owner records. Finalize can print `UNLOCKED: <path> ← prismatic-engine` while the simple-owner lock remains as `<path> ned`.

## Required verification

Always run after finalize:

```bash
node /home/ubuntu/.antigravity/swarm.js status
```

If any of the task locks remain under `ned`, manually unlock using the same simple-owner shape:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock <repo-relative-path> ned
```

Then re-run status and require:

```text
No active locks.
```

Do this before suppressing delivery or claiming completion. The finalize transcript alone is not authoritative for lock cleanup when acquisition/unlock shapes differ.

## Related verifier lesson from the same class

For redispatched already-finalized tasks, do not blindly reuse old RESULT verifier assertions. Re-run focused verification from a fresh clean worktree and inspect the current contract output. In GRO-4011, the prior RESULT referred to `metrics`, while the current JSON contract exposed `dashboard_metrics`; the correct recovery was to inspect the JSON keys, update the verifier assertion to the real contract, rerun, and record the corrected evidence rather than escalating a false implementation failure.

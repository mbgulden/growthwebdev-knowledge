# GRO-4011 redispatch finalize refresh: lock owner + comment verification pitfalls

Use this reference when a cron redispatch finds prior work already implemented but Linear drifted back to `In Progress` or the dispatcher asks for fresh execution evidence.

## Pattern

1. Leave the dirty shared checkout alone.
2. Create a clean detached worktree from the pushed task branch.
3. Re-run focused verification there.
4. Rerun finalize with absolute script path and explicit env:

```bash
PRISMATIC_REPO_ROOT=/tmp/<clean-worktree> \
FINALIZE_LOCK_FILES='<actual changed files>' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

5. Verify Linear state, latest evidence comment, PR checks, temp-worktree cleanup, and swarm locks before returning `[SILENT]`.

## Pitfall: finalize can unlock the wrong owner

On GRO-4011, `finalize_task.sh` printed:

```text
UNLOCKED: docs/vision/daily-nervous-system-work-product-loop.md ← prismatic-engine
UNLOCKED: scripts/nervous_system_work_product_loop.py ← prismatic-engine
```

but an immediate `swarm.js status` still showed the same paths locked under simple owner `ned`. The transcript was not authoritative.

**Rule:** after every finalize, run:

```bash
node /home/ubuntu/.antigravity/swarm.js status
```

If any simple-owner locks remain, manually unlock them:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock <path> ned
```

Do not claim cleanup until status prints:

```text
No active locks.
```

## Pitfall: narrow Linear comment queries can miss the newest finalize comment

A post-finalize query using `comments(last:3)` returned older comments and did not show the new finalization comment, even though the comment existed. A wider fetch plus sort did show the new entry.

**Rule:** for finalization evidence proof, fetch a broad comments window and sort by `createdAt` locally:

```graphql
query($id:String!) {
  issue(id:$id) {
    comments(first:50) {
      nodes { createdAt body user { email } }
    }
  }
}
```

Then sort ascending by `createdAt` and inspect the newest entries for the finalize timestamp/body. Do not rely on a narrow `comments(last:N)` slice when verifying evidence after finalize.

## Expected RESULT refresh

Update `/tmp/issue-batches/<ISSUE>_RESULT.md` with:

- clean worktree path used for verification;
- exact verification commands and outputs summarized;
- finalize timestamp;
- Linear state re-query result;
- latest comment confirmation timestamp;
- PR/check state;
- temp worktree cleanup result;
- final `swarm.js status` result.

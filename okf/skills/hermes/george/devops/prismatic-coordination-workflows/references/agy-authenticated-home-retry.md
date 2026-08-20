# AGY authenticated HOME retry pattern

Use when a cap-1 AGY producer exits before edits because OAuth/PKCE runs under the wrong HOME, while durable token paths may already contain valid credentials.

## Trigger

- AGY producer exits early with OAuth/PKCE/auth timeout.
- The exact task/worktree should remain untrusted and must be inspected before relaunch.
- You need to keep cap 1 and relaunch the same exact task, not start a second producer.

## Safe recovery sequence

1. **Do not immediately ask Michael for a browser auth code.** First inspect token metadata only: path existence, size, parseability, refresh-token/access-token booleans, and expiry. Never print token or authorization-code values.
2. **Verify the worktree before retry.** If the failed producer exited before edits, prove the worktree is still at the exact base/clean state; if changes exist, preserve them as an untrusted candidate instead of overwriting/relaunching blindly.
3. **Use the child AGY auth HOME explicitly.** For Prismatic AGY producers, the reliable smoke pattern is:

   ```bash
   HOME=/home/ubuntu/.hermes/profiles/orchestrator/home \
     /home/ubuntu/.local/bin/agy --print-timeout 60s --print 'respond with exactly OK'
   ```

4. **Relaunch the same exact task with the same authenticated HOME.** Keep producer count at one, use the same hashed `AGY_TASK.md`, and write a new process id into durable control state as a replacement/retry, not an additional active producer.
5. **Record the prior attempt as failed-before-edits.** Durable handoff/control state should include the old process id, reason (`HOME` unset/wrong; PKCE timed out), clean-worktree fact, new authenticated process id, and unchanged side-effect boundaries.
6. **Run a state verifier after handoff/control edits.** Bind predecessor merge/release truth, exact task hash, active process liveness, cap 1, and unchanged live cursor/DB boundaries. Label it ad-hoc operational state unless it also runs canonical tests.

## Pitfalls

- Do not run cross-profile token refresh/write scripts just because a producer hit PKCE; if an unexpired token already exists, the fix may simply be the correct `HOME`.
- Do not expose tokens, refresh tokens, OAuth client secrets, or pasted authorization codes in chat or logs.
- Do not treat an auth retry as a new slice or a cap increase. It replaces the failed-before-edits process for the same task.
- Do not preserve environment-specific absence as a durable negative rule. Capture the positive pattern: metadata-only token inspection, authenticated HOME smoke, exact same-task retry, and proof-bound durable-state update.

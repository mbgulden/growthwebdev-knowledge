# Ad-hoc verification after implementation worktree removal

Session pattern: code was implemented, verified, merged, and the implementation worktree was removed. Hermes later warned that changed paths lacked fresh verification because it was still tracking the removed worktree paths.

Reusable fix pattern:

1. Create a temporary verifier script under `/tmp` with filename prefix `hermes-verify-`.
2. The verifier should create its own temporary checkout/worktree from the current target ref, usually `origin/main`, instead of relying on the removed implementation worktree or a dirty canonical checkout.
3. Verify the merged/current behavior from that clean temp checkout.
4. If API tests depend on auth/test env, set those env vars inside the verifier before importing/running tests. Example from Prismatic Engine: `PRISMATIC_API_KEY=unit-test-key` and an isolated `PRISMATIC_STATE_DIR`.
5. Run focused tests and direct behavior probes against the changed feature. Clearly call this **ad-hoc verification**, not full-suite green.
6. Remove the temporary Git worktree, prune worktree metadata, delete the verifier script, and report cleanup evidence such as `verifier_removed`.

Pitfall: if the verifier sets an auth env var that differs from the repository's existing tests, otherwise-valid tests can fail with 401s. Prefer the test suite's own expected value when reusing existing tests.

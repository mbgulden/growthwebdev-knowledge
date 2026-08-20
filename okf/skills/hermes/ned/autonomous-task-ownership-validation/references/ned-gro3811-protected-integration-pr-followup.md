# GRO-3811 protected integration PR follow-up (2026-07-12)

## Class of work

Use this when a protected-branch integration handoff was already processed by another agent/AGY/Fred and marked `Done`, but the actual reviewable GitHub PR or current remote branch is missing/stale.

## Signals

- Linear issue says `Done` / `agent:done` / self-review passed, but `gh pr list` shows no PR for the integration branch.
- Sandbox `RESULT.md` claims conflicts were resolved but says tests were skipped or only self-review ran.
- Sandbox merge commit uses an older `deploy-fresh` parent than current `origin/deploy-fresh`.
- The task crosses protected branches or multiple lanes, so direct-pushing `main`/`deploy-fresh` is still forbidden.

## Workflow

1. **Read the Linear issue and sandbox result first.** Treat self-review as a lead, not proof. Confirm whether a PR/remote branch exists.
2. **Import the sandbox merge as a local base branch.** Example shape:
   - `git fetch /archive/agy_sandboxes/<ISSUE> feature/<issue>:refs/heads/ned/<issue>-agy-base`
   - Create a fresh worktree/branch from that imported merge.
3. **Merge current `origin/deploy-fresh` again.** The sandbox may have used a stale deploy parent. Reproduce the remaining conflicts against current remote state.
4. **Prefer the already-tested sandbox/main resolutions when current deploy-fresh replays old conflicts**, then reapply only the current deploy-fresh deltas needed to satisfy tests. Avoid blindly taking `--theirs` for large core files; that can erase main-side compatibility shims.
5. **Conflict-resolution preservation checklist for Prismatic dispatcher/gateway integrations:**
   - dispatcher heartbeat/watchdog shims,
   - process observer and token-drain hooks,
   - dispatch-ready/lane-contract filtering,
   - capability router imports,
   - gateway plugin-health/auth routes,
   - harness contract compatibility,
   - doctor command wrapper,
   - mode-switch legacy approval API,
   - workspace optimizer old/new CLI compatibility,
   - webhook backfill bounded replay options.
6. **Run focused verification before PR:**
   - conflict marker scan excluding `.git`, venvs, node modules, caches;
   - `python3 -m compileall -q prismatic scripts plugins tests`;
   - targeted pytest suites around every conflict family.
7. **Open a protected integration PR to `main`; do not merge until GitHub checks are green.** If GitHub checks fail after local focused tests pass, stop and report PR-check failure as the next blocker.
8. **Update Linear with PR link and verification evidence; remove stale `dispatch:ready` once a reviewable PR exists** so the task does not redispatch while review/fix is pending.

## Pitfalls from GRO-3811

- AGY/Fred self-review said `Done`, but there was no PR and no remote branch visible; completion needed independent verification.
- The sandbox merge parent for `deploy-fresh` was stale. Current `origin/deploy-fresh` had additional commits, causing a second conflict round.
- Blindly taking current deploy-fresh for large files made focused suites regress because it dropped main-side compatibility shims. The safer pattern was: start from the sandbox resolution, merge current deploy-fresh, preserve known main shims, and use tests to identify missing current-deploy deltas.
- A broad full-repo pytest can surface many unrelated or older suite failures on a massive integration branch. It is useful as a signal, but the immediate acceptance gate should be focused conflict-area tests plus GitHub PR checks.
- If PR checks fail (`Verify shipped plugins load`, `test`, etc.), do not claim the integration is complete. The next step is fixing those checks or documenting a genuine external blocker.

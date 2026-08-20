# HDE production-promotion clean worktree pattern — 2026-07

Use when staging HDE work is verified but the canonical production checkout is dirty or staging-only files would violate Ned's lane guard.

## Situation

- Staging branch contained verified HDE demo/email work but was ahead of upstream and had runtime/generated dirt.
- Canonical `/home/ubuntu/work/hd-platform` checkout also had unrelated dirty production/source files.
- Direct production promotion would have mixed unrelated dirt, staging-only systemd paths, and lane violations.

## Pattern

1. **Fix mechanical blockers in the source branch first.**
   - Run `git diff --check` against the intended promotion range.
   - If a prior commit has whitespace/EOF issues, fix and amend before building the promotion branch.

2. **Create a clean promotion worktree from the production base.**
   ```bash
   cd /home/ubuntu/work/hd-platform
   git fetch --all --prune
   git worktree add -b ned/<production-ready-branch> /tmp/<promotion-worktree> deploy-fresh
   ```

3. **Import the verified source branch explicitly.**
   ```bash
   git -C /tmp/<promotion-worktree> fetch /home/ubuntu/work/hd-platform-staging \
     ned/<source-branch>:refs/remotes/staging/<source-branch-short>
   git -C /tmp/<promotion-worktree> rev-list --reverse <old-source-base>..refs/remotes/staging/<source-branch-short>
   ```

4. **Cherry-pick only the intended commits.**
   - Resolve conflicts by preserving the already-verified staging implementation only for the class of files under promotion.
   - Do not drag unrelated dirty files from either checkout.

5. **Make templates lane-safe.**
   - Ned cannot push `deploy/systemd/*` in the HDE repo; the pre-push guard rejects it.
   - Store service/timer templates under `scripts/systemd/` instead.
   - Production install step can later copy them to `/etc/systemd/system/`, but the repo path stays in Ned's lane.
   - If a gate script checks template existence, make the template directory configurable, e.g. `HDE_DEMO_SYSTEMD_TEMPLATE_DIR`, defaulting to `scripts/systemd`.

6. **Separate production defaults from staging override verification.**
   - Production templates should reference `/home/ubuntu/work/hd-platform`, production URLs, and production timer names.
   - Staging proof should still be possible by setting environment overrides such as `HDE_REPO_ROOT`, `HDE_RUNTIME_DIR`, `HDE_DEMO_LIFECYCLE_TIMER`, `HDE_DEMO_REMINDER_TIMER`, and template prefixes.

7. **Run a focused `/tmp/hermes-verify-*` verifier before pushing.**
   Minimum checks:
   - `git diff --check`
   - Python compile for changed Python files
   - `systemd-analyze verify` for lane-safe templates
   - canonical build command, e.g. `npm run build`
   - changed-file secret scan only, not noisy whole-repo legacy docs
   - production templates do not reference staging paths/services
   - staging gate still passes with explicit staging overrides
   - production gate defaults reference production timer names and may remain `BLOCKED` until timers/evidence are actually installed
   - route smoke for staging demo and existing production public pages

8. **Push and read the guard output.**
   - If lane guard fails, fix the file placement/branch shape, do not force-push around it.
   - After PR creation, treat external CI failures separately from local build success. Cloudflare Pages may pass while Workers build fails; do not merge/force production until the failing check is understood or explicitly waived.

## Reporting shape

Report:
- branch and PR URL,
- base branch,
- verifier marker,
- local build result,
- push guard result,
- CI status,
- whether production was actually deployed.

Be explicit: a clean production-promotion PR is not the same thing as production installation/deployment.

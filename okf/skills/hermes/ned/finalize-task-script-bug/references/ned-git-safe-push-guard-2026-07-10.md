# Ned Git safe-push guard — 2026-07-10

## Class-level lesson
When Ned is moving code or assets to GitHub, the safety boundary is not just "don't push main." Install and verify a pre-push guard that makes unsafe pushes mechanically hard before resuming autonomous cleanup or feature work.

## Trigger from session
Michael explicitly asked: "How do we make sure Ned doesn’t bowl right over and overwrite someone’s everyone else’s branch on GitHub... fix it so it’s not a problem going forward." Later, VFX assets needed to be promoted into the correct Darius/AGY feature lane.

## Installed guard
- Hook path: `/home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push`
- Installer: `/home/ubuntu/.hermes/profiles/ned/scripts/install_git_push_guard.sh`
- Global Git config:
  - `core.hooksPath=/home/ubuntu/.hermes/profiles/ned/git-hooks`
  - `push.default=current`

## Default protections
The pre-push hook blocks before network push:
- protected branch pushes: `main`, `master`, `deploy-fresh`, `staging`, `production`
- branch deletes unless `GIT_SAFE_PUSH_ALLOW_DELETE=1`
- non-fast-forward updates / force pushes unless `GIT_SAFE_PUSH_ALLOW_NON_FF=1`
- local branch pushed to a different remote branch unless `GIT_SAFE_PUSH_ALLOW_RENAME=1`

## Ned-owned repo enforcement
The installer marks known Ned/Prismatic worktrees with:
- `hermes.agent=ned`
- `hermes.enforceBranchPrefix=true`

For those repos, the hook also blocks remote branches that do not start with `ned/` unless `GIT_SAFE_PUSH_ALLOW_FOREIGN_BRANCH=1` is explicitly set.

Configured by installer pattern:
- `prismatic-engine`
- `ned-*`
- `prismatic-engine-ned-*`
- `prismatic-engine-gro*`
- `prismatic-gro*`

Do **not** set `hermes.enforceBranchPrefix=true` globally unless intentionally blocking every profile's non-`ned/` branch pushes. Keep it repo-local.

## Verification pattern
Run hook tests without contacting GitHub by piping pre-push protocol lines:

```bash
cd /home/ubuntu/work/prismatic-engine
head_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse HEAD~1)

# Allowed: same local/remote ned branch, new remote branch.
printf 'refs/heads/ned/test %s refs/heads/ned/test 0000000000000000000000000000000000000000\n' "$head_sha" \
  | /home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push origin git@example.com:test/repo.git
# expected: exit 0

# Block protected branch.
printf 'refs/heads/ned/test %s refs/heads/main 0000000000000000000000000000000000000000\n' "$head_sha" \
  | /home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push origin git@example.com:test/repo.git
# expected: exit 1, protected branch blocked

# Block foreign branch in Ned-owned repo.
printf 'refs/heads/ned/test %s refs/heads/kai/test 0000000000000000000000000000000000000000\n' "$head_sha" \
  | /home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push origin git@example.com:test/repo.git
# expected: exit 1, foreign branch blocked

# Block non-fast-forward overwrite.
printf 'refs/heads/ned/test %s refs/heads/ned/test %s\n' "$remote_sha" "$head_sha" \
  | /home/ubuntu/.hermes/profiles/ned/git-hooks/pre-push origin git@example.com:test/repo.git
# expected: exit 1, non-fast-forward blocked
```

## Promoting out-of-lane assets/code safely
When Michael asks Ned to get work "to the right lane" even if the files are outside Ned's normal write lane:
1. Preserve the dirty state first: binary patch, raw copies, checksums, and concise README.
2. Verify the assets/code are structurally valid for their use (`PIL` dimensions/mode/alpha for PNGs, syntax/tests for code).
3. Fetch the remote feature branch and confirm it is not behind/diverged before committing.
4. Stage only the intended files; never `git add -A` in asset repos.
5. Commit with the owning lane prefix (`[AGY]`, `[Kai]`, etc.) and explain Ned is acting at Michael's request to route/preserve the work.
6. Push `HEAD` to the matching feature branch only; let the safe-push guard block protected/overwrite paths.
7. Create or update the PR against the branch with shared history. If GitHub rejects `main` with "no history in common," inspect merge-base and use the repo's actual base (`master` in Darius during this session).
8. Verify remote commit equals local commit and working tree is clean.

## Darius VFX session example
- Dirty branch: `/home/ubuntu/work/darius-star`, `feature/gro-1928`
- Files: `assets/sprites/vfx/explosion_[0-3]_[0-3].png`
- Preserved archive: `/home/ubuntu/.hermes/profiles/ned/git-archives/darius-star-vfx-dirty-20260710T141211Z`
- Verification: all 16 PNGs were `512x512`, `RGBA`, alpha range `0..255`
- Commit: `c39b03c [AGY] Add transparent player explosion VFX frames (#GRO-1928)`
- PR: `https://github.com/mbgulden/darius-star/pull/18` targeting `master` because `feature/gro-1928` had no shared history with `main`

## Pitfalls
- Hermes shell env may expose `HERMES_PROFILE` as a path or inherited profile value; the hook must prefer repo-local `git config hermes.agent` and normalize env fallback via `basename`.
- `find -name .git -type d` misses worktrees whose `.git` is a file. The installer checks `-e "$repo/.git"` at `/home/ubuntu/work/*` depth instead.
- GitHub's default branch can be `main` while the feature branch lineage actually belongs to `master`; check merge-base before assuming PR base.
- For asset repos, an apparently safe cleanup may be an asset feature. Preserve first, then route to the owning lane.

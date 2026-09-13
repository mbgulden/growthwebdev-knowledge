# Engine status report (class-level) + candidate-head resolution

When Michael asks for "status of prismatic engine" / "where are we on PE", the answer is a five-part live evidence packet. Every part is a fresh command — never handoff-file recall (both `PRISMATIC_CURRENT_HANDOFF.md` and `state/current.json` can be days stale).

## The five-part packet

1. **Production**: `systemctl is-active prismatic-gateway.service`; `ss -ltnp | grep 9000` — confirm the listener PID is the systemd unit, not a rogue python on a side port; `curl -s -o /dev/null -w "%{http_code}"` on `/`, `/dashboard`, `/workspaces` at `https://prismatic.growthwebdev.com`. Prod is nginx+CF: curl with a browser User-Agent (bare/default UA → CF 1010 403). Label HTTP-200 as a live smoke only — never as content-correctness.
2. **Runtime↔repo alignment**: `readlink /home/ubuntu/.prismatic/venv_current` (symlink target encodes the installed sha: `venvs/prismatic-engine-<sha>`) and `readlink /proc/<gateway-pid>/cwd` (durable `releases/...` checkout). Both must match the main-tip sha; mismatch = report the drift, do not fix unprompted.
3. **Repo truth**: `git status -sb` + `git log --oneline` in `/home/ubuntu/work/prismatic-engine`. Dirty-tree residue is reported with file mtimes (mtimes identify which session left it) and left uncommitted/un-discarded without authorization.
4. **Candidate truth**: `git worktree list` + `gh pr list --repo mbgulden/prismatic-engine --state open` (newest first) + per-candidate worktree state.
5. **Handoff cross-check**: `PRISMATIC_CURRENT_HANDOFF.md` is a LANE handoff (the last review lane, e.g. an AGY closeout revision), not an engine snapshot; `state/current.json` is session state. Surface what each lane says, then re-verify every claim against the live commands above. When a lane claim is stale (e.g. "PR open, manual merge pending" but it is MERGED), state the correction in the report.

## Worktree locations are dual (missed by naive scans)

PE worktrees are registered in TWO places plus in-repo:
- `/home/ubuntu/.prismatic/worktrees/<lane>` (the majority)
- `/home/ubuntu/work/prismatic-*` (older standalone checkouts)
- in-repo `worktrees/ned-*`

`git worktree list` (from the main repo) covers all of them; `ls /home/ubuntu/work/prismatic*` misses the `.prismatic/worktrees` half. Always count with `git worktree list | wc -l` (a claim unless run) — 91 were registered as of 2026-09-01. Cleanup is a separately authorized task, never folded into a status report.

## Candidate-head resolution (pitfall hit live 2026-09-01)

A candidate head recorded in a lane handoff (e.g. `6fddcc21` in the AGY V0.2 handoff) will NOT resolve in the main repo: PE candidates live in detached-branch worktrees, not on a remote the main repo fetched. `git cat-file -t <sha>` in the main repo → `fatal: Not a valid object name`.

Resolution recipe:
1. `git worktree list` and match the sha prefix (or `git -C <lane-worktree> rev-parse HEAD`).
2. When found, report: branch name, worktree cleanliness, sync vs its remote (`git rev-parse HEAD` vs `origin/<branch>`), commit dates, and — critically — whether the fresh exact-head review at THAT head has actually been run. Repairs committed on-branch ≠ reviewed; a BLOCKED third-party review at an older head (e.g. `3ff7c756`) does not cover the new head.
3. When absent from every worktree: report the recorded head as unresolvable. Never substitute a different sha.

## 2026-09-01 session evidence (what a good report looked like)

- Production PASS: unit active, pid 937385 on 0.0.0.0:9000, cwd = `releases/prismatic-engine-c3e7c58d…`; `/`, `/dashboard`, `/workspaces` all 200 with browser UA.
- `venv_current` → `c3e7c58d` = main tip = origin/main (runtime and repo aligned; no rogue gateway procs).
- Main tree dirty with Aug 27 06:54–06:55 residue (dashboard.html, release_production.sh, screenshots + untracked proof scripts) — reported, untouched.
- 14 open PRs, newest #427 (Aug 9) — all stale, reported as such.
- AGY V0.2 lane: handoff said candidate `6fddcc21` with 8 release-blocking findings BLOCKED at `3ff7c756`; worktree scan showed `6fddcc21` = `6b2f647` "repair review findings 1-8" + skills re-export already committed — so repairs on-branch, fresh exact-head review NOT yet run. That distinction (repairs-committed vs reviewed) was the load-bearing line of the report.

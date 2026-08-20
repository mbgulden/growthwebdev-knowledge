# GRO-4004 parent-epic redispatch refresh

Use this when a parent/epic issue is redispatched even though a `ned/<issue>` branch, PR, and prior finalization evidence already exist.

Observed pattern on GRO-4004:

- Linear drifted back to `Backlog` with stale `dispatch:ready` despite prior branch/PR/evidence.
- The canonical checkout was dirty/on another HDE branch, so the safe path was a clean detached temp worktree from `origin/ned/GRO-4004`.
- Verification had to prove the parent gate's *red/blocked* state, not force the epic green:
  - `node --check scripts/hde-green-ops-gate.mjs`
  - `node scripts/hde-green-ops-gate.mjs --json > /tmp/gro4004-gate-YYYYMMDD.json`
  - `node scripts/hde-green-ops-gate.mjs --require-green > /tmp/gro4004-gate-YYYYMMDD.txt` and expect exit `1` while child gates remain open.
  - `npm ci && npm run build` in the clean worktree when `node_modules` is absent.
- `npm run build` failing with `astro: not found` in a fresh worktree is dependency setup, not proof of code failure; install from the lockfile and rerun the canonical build.
- Rerun finalize with absolute script path and explicit scope:
  ```bash
  PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro4004 \
  FINALIZE_LOCK_FILES='scripts/hde-green-ops-gate.mjs scripts/docs/gro-4004-hde-green-security-reliability-gate.md' \
  bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4004 ned/GRO-4004 ned
  ```
- Post-finalize checks are mandatory:
  - Query Linear; state must be `In Review`.
  - Remove stale `dispatch:ready` if it remains.
  - Check `swarm.js status`; if simple-owner locks remain, unlock with the same simple form (`swarm.js unlock <path> ned`) because finalize may only clear repo-qualified locks.
  - Inspect PR checks. Keep the epic non-green / not Done while child gates are open or remote checks are red.
- Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh evidence and suppress external delivery (`[SILENT]`) if there is no new blocker requiring Michael.

# Non-standard repo lock/unlock shape after finalize

## When this applies

Use this when `finalize_task.sh` is run from a clean temporary worktree outside the default `/home/ubuntu/work/prismatic-engine`, especially HD Platform tasks with:

```bash
PRISMATIC_REPO_ROOT=/tmp/<repo-worktree> \
FINALIZE_LOCK_FILES='src/pages/foo.astro docs/foo.md src/components/Nav.astro' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE> ned/<ISSUE> ned
```

## Pitfall

The finalize transcript can print successful unlock lines while the lock registry still contains the touched paths if the original locks were acquired with a different argument shape.

Observed pattern:

```bash
# acquisition used the short form
node /home/ubuntu/.antigravity/swarm.js lock src/pages/community.astro ned

# finalize used its default repo-qualified unlock form
node /home/ubuntu/.antigravity/swarm.js unlock src/pages/community.astro prismatic-engine ned
```

Finalize printed `UNLOCKED`, but `/home/ubuntu/.antigravity/swarm_locks.json` still contained:

```json
{"path":"src/pages/community.astro","agent":"ned", ...}
```

## Required recovery pattern

After finalize, verify the lock registry for every touched path before claiming cleanup:

```bash
python3 - <<'PY'
import json
paths = {'src/pages/community.astro', 'docs/retention-community-invitation-funnel.md', 'src/components/Nav.astro'}
locks = json.load(open('/home/ubuntu/.antigravity/swarm_locks.json'))
print([x for x in locks if x.get('path') in paths])
PY
```

If rows remain, unlock with the same argument shape used to acquire the lock:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock src/pages/community.astro ned
node /home/ubuntu/.antigravity/swarm.js unlock docs/retention-community-invitation-funnel.md ned
node /home/ubuntu/.antigravity/swarm.js unlock src/components/Nav.astro ned
```

## Durable lesson

Do not record this as “finalize unlock is broken.” The stable lesson is: **match the lock/unlock argument shape and verify `/home/ubuntu/.antigravity/swarm_locks.json` after finalize whenever using custom `PRISMATIC_REPO_ROOT` or temp worktrees.**

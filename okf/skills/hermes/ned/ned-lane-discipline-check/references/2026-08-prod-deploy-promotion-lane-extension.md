# 2026-08-19 HDE prod deploy promotion — scoped lane extension

Promoting `origin/deploy-fresh` (staging) into `main` for the HDE production
deploy required landing `functions/` (CF Pages API proxies) and
`reports/server.py` — both outside Ned's owned dirs. Relocating them was
wrong (a merge must carry those paths as-is), so a scoped lane extension was
used, with Michael's explicit permission.

## What got flagged
```
❌ [Prismatic Engine] Lane violation by ned:
   - functions/api/checkout/create-session.js
   - functions/api/checkout/session.js
   - functions/api/demo/start.js
   - functions/create-checkout.js
   - reports/server.py
   These files are outside ned's lane.
   Owned directories: ['src/', 'api/', 'scripts/', 'docs/', 'payment/',
                       'public/', 'shared/', 'tests/', '.pwp/', 'package.json',
                       'package-lock.json', 'playwright.config.ts',
                       'lighthouserc.json', 'wrangler.jsonc',
                       'PRISMATIC_ENGINE.yaml']
```

## What was done
1. Edited `PRISMATIC_ENGINE.yaml` `agents.ned.lanes.owner` in the worktree
   `/home/ubuntu/work/hd-platform-prod-merge` to add `"functions/"` and
   `"reports/"`, with a dated comment scoping it to
   `ned/hde-prod-deploy-promotion-2026-08-19` and marking it temporary
   (honoring the 2026-07-17 "revert/narrow before generalizing" note).
2. **Committed** that yaml change (`93176a0`) in the same worktree — the
   pre-push guard reads the file from the checkout being pushed, so an
   uncommitted edit would not count.
3. Pushed the branch, then deployed.

## Key lessons
- The guard reads `PRISMATIC_ENGINE.yaml` **from the worktree being pushed
  from**, not a canonical copy. Edit + commit there.
- A lane extension is a governance change: it requires explicit human
  permission, and the reply should be quoted in the commit message.
- Keep the extension narrow (only the paths the promotion actually needs)
  and mark it temporary. After the PR merges, narrow the owner list back to
  baseline and file a pending decision for Michael if narrowing is contested.
- Do not force-push around the guard, and do not silently drop the out-of-
  lane files — a promotion merge must land them.

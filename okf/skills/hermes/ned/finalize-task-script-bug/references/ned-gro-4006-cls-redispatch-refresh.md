# GRO-4006 CLS/layout stability redispatch refresh

Use this when a previously implemented HD Platform frontend/layout task is redispatched because Linear drifted back to `Backlog` or regained `dispatch:ready`, while an existing `ned/...` branch/PR/comment evidence already exists.

## Confirm before rebuilding

1. Query Linear comments, not just issue labels. Existing evidence may already include branch, commit, PR, Lighthouse numbers, and explicit reason the task is not Done.
2. Fetch the remote branch and inspect the latest commit rather than touching a dirty primary worktree:
   ```bash
   git -C /home/ubuntu/work/hd-platform fetch origin ned/GRO-XXXX main --prune
   rm -rf /tmp/hd-platform-gro-XXXX-reverify
   git -C /home/ubuntu/work/hd-platform worktree add --detach /tmp/hd-platform-gro-XXXX-reverify origin/ned/GRO-XXXX
   git -C /tmp/hd-platform-gro-XXXX-reverify switch -c ned/GRO-XXXX --track origin/ned/GRO-XXXX
   ```
3. Clean generated artifacts before finalize so Playwright/Lighthouse residue is not auto-committed:
   ```bash
   rm -rf test-results playwright-report .playwright /tmp/groXXXX-live-lighthouse.json /tmp/groXXXX-lighthouse.log
   ```

## Verification pattern

Run the lockfile install in the clean worktree if `node_modules` is absent, then verify the exact frontend proof:

```bash
npm ci
npm run build
npm run qa:flows -- --project=desktop-chromium tests/flows/deconditioning-checkout.spec.ts
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' https://ned-gro-XXXX.hd-platform.pages.dev/free-human-design-reading-generator/
npx lighthouse https://ned-gro-XXXX.hd-platform.pages.dev/free-human-design-reading-generator/ \
  --chrome-flags='--headless --no-sandbox' \
  --only-categories=performance \
  --output=json \
  --output-path=/tmp/groXXXX-live-lighthouse.json \
  --quiet
node -e "const r=require('/tmp/groXXXX-live-lighthouse.json'); const a=r.audits; console.log({performance:r.categories.performance.score, cls:a['cumulative-layout-shift'].numericValue, lcp:a['largest-contentful-paint'].numericValue, tbt:a['total-blocking-time'].numericValue})"
```

For GRO-4006 the accepted green proof was: preview HTTP `200`, Lighthouse performance `0.99`, CLS `0.03093969570967699`, LCP about `1585ms`, TBT `0ms`, with `npm run build` and the flow spec passing (`4 passed, 2 skipped`).

## Finalize and state handling

- Acquire locks for the already-changed files before rerunning finalize if the lock registry is clear but finalization needs to unlock them.
- Run finalize with absolute path and explicit repo/lock env:
  ```bash
  PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro-XXXX-reverify \
  FINALIZE_LOCK_FILES='src/pages/free-human-design-reading-generator.astro tests/flows/deconditioning-checkout.spec.ts docs/hde-free-reading-cls-reservation.md' \
  bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
  ```
- Finalize transitions to `In Review` and posts its generic report, but it does not remove stale scanner labels. If this is a redispatch refresh and proof is recorded, remove `dispatch:ready` manually and verify labels afterward.
- Do **not** mark Done while PR checks remain red. Pages/live proof can be green while `Workers Builds: hd-platform` is red due to the repo's Pages-vs-Workers check mismatch; keep Linear `In Review` and document the specific red check.
- Verify after finalize: `swarm.js status` shows no active locks; Linear state is `In Review`; comments include the newest finalizer comment; `dispatch:ready` is absent.

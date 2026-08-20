# HDE Pages vs Workers Builds conflict

Use when an HD Platform PR is otherwise verified but GitHub reports `Workers Builds: hd-platform` red while `Cloudflare Pages` is green.

## Durable lesson

The HD Platform repo's canonical deployment path is Cloudflare Pages. The root `wrangler.jsonc` must stay Pages-compatible, typically with:

```json
{
  "pages_build_output_dir": "dist"
}
```

Do **not** add root-level `assets.directory` just to satisfy `npx wrangler versions upload` for the external Workers Builds check. That makes a local Workers dry-run pass, but Cloudflare Pages preview validation rejects the same config with:

```text
Configuration file for Pages projects does not support "assets"
```

This is not a code green-light: the PR remains `UNSTABLE` while the Workers check is red. Treat it as an external Cloudflare project-owner decision unless there is an explicitly approved separate Worker config/command.

## Verification pattern

1. Verify the actual product path first:
   - `npm ci` if dependencies are absent/stale.
   - `npm run build` or the issue's stronger proof command, e.g. `npm run pwp:verify`.
   - Query `gh pr view <PR> --json statusCheckRollup,mergeStateStatus,headRefOid`.
2. If Pages is red, fetch Pages deployment logs via Cloudflare Pages API and fix repo-side Pages config.
3. If Pages is green and Workers is red:
   - Reproduce `npx wrangler versions upload --dry-run` locally only as evidence.
   - Do not force a conflicting root config into the repo.
   - Search OKF/session/env before declaring a handoff.
   - Leave Linear `In Review`, remove stale `dispatch:ready`, and add `agent:needs-human-review` if a Cloudflare project-owner decision is needed.
4. Record in RESULT that the remaining blocker is the external Workers Builds trigger, not the implemented feature proof.

## Canonical observed sequence

- Adding `assets.directory: ./dist` made `npx wrangler versions upload --dry-run` pass locally.
- The next Cloudflare Pages preview failed during Wrangler config validation because Pages projects do not support `assets`.
- Restoring `pages_build_output_dir: dist` made Pages green again while Workers Builds stayed red.

Conclusion: optimize for the canonical Pages deployment, not for a duplicate Workers trigger that uses incompatible Wrangler semantics.

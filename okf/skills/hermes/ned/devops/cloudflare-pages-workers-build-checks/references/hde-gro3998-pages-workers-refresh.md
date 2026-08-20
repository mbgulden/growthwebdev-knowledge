# HDE GRO-3998 Pages/Workers check refresh

A redispatched HDE SEO/index parent PR had Cloudflare Pages green and `Workers Builds: hd-platform` red.

## Important correction

Do not push a root-level `assets.directory` workaround to a Pages repo just to make Wrangler/Workers semantics happy. This was briefly tried on `ned/GRO-3998`; local `npx wrangler deploy --dry-run` passed, but prior evidence and the skill reference show the same root config breaks Cloudflare Pages validation:

```text
Configuration file for Pages projects does not support "assets"
```

The correct branch state restored `wrangler.jsonc` to Pages-compatible `pages_build_output_dir: "dist"` and documented the remaining Workers check as a Cloudflare project-owner decision.

## Verification pattern used

From the disposable worktree:

```bash
npm ci
npm run build
python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo . --json
python3 scripts/operations/hde_seo_index_hygiene_audit.py --repo .
git diff --check
gh pr view 31 --repo mbgulden/hd-platform --json headRefOid,statusCheckRollup,mergeStateStatus,url
```

After a guard reported verification as stale, rerunning `npm run build` was required even though an earlier build had passed. Treat these guard messages as authoritative: rerun the named verification and report the fresh output.

## Linear/task hygiene

- Keep the issue `In Review`, not `Done`, while a required PR check remains red.
- Remove stale `dispatch:ready` so the scanner does not redispatch completed code work.
- Add `agent:needs-human-review` when the only remaining blocker is the duplicate Workers trigger/project configuration.
- `finalize_task.sh` may unlock paths with a `prismatic-engine` owner shape while simple `ned` locks remain; verify `swarm.js status` and manually unlock lingering simple-owner locks.

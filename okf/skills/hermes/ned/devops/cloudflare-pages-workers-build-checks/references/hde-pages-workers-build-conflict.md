# HDE Pages vs Workers Builds conflict — GRO-3996 reproduction

A PR implementing PWP analytics verification had the actual Pages path green locally and in Cloudflare, but GitHub still reported `Workers Builds: hd-platform` red.

## What was tried

- Branch had `pages_build_output_dir: "dist"` in root `wrangler.jsonc`.
- `npm run pwp:verify` passed:
  - 10 Astro pages built.
  - Analytics proof found GA/GTM on 9 routed pages.
  - Funnel event hooks found on 3 surfaces.
  - Visual/a11y/link checks passed.
- `npx wrangler versions upload --dry-run` failed locally with:

```text
Missing entry-point to Worker script or to assets directory
```

A repo-side attempt added:

```json
"assets": {
  "directory": "./dist"
}
```

That made `npx wrangler versions upload --dry-run` pass locally.

## Why that fix was rejected

After pushing the `assets.directory` change, Cloudflare Pages preview failed. Pages deployment logs said:

```text
Running configuration file validation for Pages:
- Configuration file for Pages projects does not support "assets"
Failed: unable to read the Wrangler configuration file with code: 1
```

So the same root config cannot satisfy both Cloudflare Pages validation and the external Workers Builds trigger when that trigger runs `npx wrangler versions upload` against the Pages repo.

## Correct outcome

- Restore the Pages-compatible `wrangler.jsonc` with `pages_build_output_dir: "dist"`.
- Confirm Cloudflare Pages preview is green again.
- Leave the PR/Linear issue not green while `Workers Builds: hd-platform` remains red.
- Remove `dispatch:ready`; add `agent:needs-human-review` if a Cloudflare project-owner decision is needed.
- Handoff options: disable/waive the duplicate Workers Builds trigger for Pages PRs, or point it at a separate Worker-specific config/command.

# HDE emergency visual rollback + production deployment guard — 2026-07-18

## Trigger

Use this when HDE staging/production suddenly shows old homepage content, old headers/footers, or legacy dark/incorrect styles after cleanup, checkout, or Cloudflare work.

## Durable lessons

1. **Production is not a convenient verification target.**
   - Do not deploy to `humandesignengine.com` / Cloudflare Pages production unless Michael explicitly approves production deployment in the current task.
   - Checkout/API fixes, Access bypasses, and visual shell fixes must not be bundled into an opportunistic production deploy from a dirty tree.

2. **Dirty working trees are deployment hazards.**
   - Before any deploy, record branch/head/status and ensure the artifact comes from the intended branch/commit.
   - If the current repo is dirty, build from an isolated worktree at the approved commit instead of the active checkout.

3. **Emergency visual rollback pattern.**
   - Identify the last known-good visual shell commit/branch (for HDE this was `origin/deploy-fresh` at `d189435` after PR #18).
   - Create an isolated worktree, build there, and verify markers before syncing/deploying:
     ```bash
     git worktree add --detach /tmp/hde-restore origin/deploy-fresh
     cd /tmp/hde-restore
     npm ci
     npm run build
     npm run pwp:verify
     ```
   - Verify built homepage contains the modern markers and not the legacy marker:
     - present: `Verifiable calculations, premium reports`
     - present: `emdash-site-header`
     - present: `menuTrigger`
     - absent: `The Engine Behind Every Chart`

4. **Restore staging runtime with a backup.**
   - If staging is VM-served, backup then swap `dist/`:
     ```bash
     BACKUP=/home/ubuntu/work/hd-platform-staging/dist.backup-bad-old-shell-$(date -u +%Y%m%dT%H%M%SZ)
     cp -a /home/ubuntu/work/hd-platform-staging/dist "$BACKUP"
     rsync -a --delete /tmp/hde-restore/dist/ /home/ubuntu/work/hd-platform-staging/dist/
     ```

5. **Production restore is a corrective rollback, not normal process.**
   - Only do it when correcting an unauthorized/bad production deployment or with explicit approval.
   - Deploy the verified clean artifact, not the current dirty checkout:
     ```bash
     export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN"
     npx --yes wrangler pages deploy dist --project-name hd-platform --branch main
     ```

6. **Live verification must check content markers, not just HTTP 200.**
   - Use cache-busting query strings on both staging and production.
   - Assert for representative routes:
     - HTTP 200
     - exactly one `<header>` and one `<footer>`
     - `emdash-site-header` present
     - `menuTrigger` present
     - legacy marker absent: `The Engine Behind Every Chart`
   - On the homepage, also assert the modern homepage marker is present: `Verifiable calculations, premium reports`.

7. **Do not mix visual rollback with business-copy/checkout changes.**
   - Emergency restore should get the approved shell/homepage back first.
   - Reapply price/copy/payment changes in a separate branch/artifact, verify on staging first, and deploy production only after explicit approval.

## Minimal evidence to report

- Bad deployment ID if known.
- Known-good commit used for restore.
- Staging backup path.
- Cloudflare deployment URL/ID if production restore was explicitly approved or corrective.
- `npm run pwp:verify` summary from the isolated worktree.
- Live cache-busted marker verification for staging and production.

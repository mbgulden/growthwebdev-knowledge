# HDE Staging-only Price/Copy Reapply — 2026-07-18

Session-specific reference for safely reapplying report price/copy changes after an emergency visual rollback.

## Context

A dirty production deployment reintroduced old HDE visual shell/header/footer content. The safe recovery was:

1. Emergency rollback from a known-good clean shell commit.
2. Reapply report price/copy changes separately in a staging-only worktree.
3. Verify heavily.
4. Deploy staging/preview first.
5. Promote to production only after explicit user approval.

## Durable workflow

- Start from the restored shell source of truth, not the dirty canonical checkout.
- Use an isolated worktree/branch, e.g. `/tmp/hde-staging-price-copy-YYYYMMDD` on `ned/...`.
- Reapply only the intended copy/pricing deltas:
  - Homepage report cards.
  - `/buy-report/` Astro route.
  - Legacy report/landing/upsell/affiliate static surfaces.
  - `payment/static/hd-checkout.js` price data.
- For HDE one-off reports, expected prices were:
  - Natal/Foundation `$9` (`900` cents)
  - Transit `$14` (`1400` cents)
  - Relationship Synastry `$14` (`1400` cents)
  - Complete Bundle `$29` (`2900` cents)
- Add/keep Sanctuary positioning: reports are snapshots/maps; Sanctuary/coaching/consultation are the deeper work.

## Verification

Use regex/content checks after `npm run build` because Astro injects `data-astro-*` attributes and minifies inline JS. Do not require exact source formatting in built HTML.

Minimum gates:

```bash
node --check payment/static/hd-checkout.js
npm run build
npm run pwp:verify
```

Focused built-output checks should prove:

- Old homepage marker absent: `The Engine Behind Every Chart` is not present.
- Modern shell present: `emdash-site-header` and `menuTrigger` are present.
- Homepage has `$9`, `$14`, `$29` via regex tolerant of `data-astro-*` attributes.
- Buy-report page has `$9`, `$14`, `$29`, `900/1400/2900` checkout prices, and the Sanctuary CTA.
- Legacy report/affiliate/upsell pages have updated prices/commissions.

## Deployment discipline

- Staging VM sync: back up `/home/ubuntu/work/hd-platform-staging/dist/`, then `rsync --delete` verified `dist/` into staging.
- Cloudflare preview deploy: use a non-main branch, e.g. `ned/hde-staging-price-copy-...`.
- Production proof: query Cloudflare Pages deployments and show latest production did not change after staging-only deploy.
- Only promote to production after an explicit user instruction such as “promote staging to production.”

## Pitfalls

- A general PWP pass is necessary but not enough; include focused price/copy markers.
- Browser smoke should reach Stripe but not complete payment.
- After production promotion, same-origin Pages checkout may need Pages Functions; see the Cloudflare Access/Pages checkout proxy reference.

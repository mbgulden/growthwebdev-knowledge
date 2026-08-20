# HDE Pages demo production deploy — 2026-07

Session lesson from promoting the HDE Sanctuary demo flow to production.

## Failure mode

A PR can merge cleanly and Cloudflare Pages can report deploy success while the live site still lacks expected same-origin API behavior if the production branch does not include the required Pages Functions source.

Observed symptoms after merge/deploy:

- `https://humandesignengine.com/sanctuary-demo/` returned `200`, but the form POST target was not enough by itself.
- `POST https://humandesignengine.com/api/demo/start` initially returned `405`/Access-shaped behavior.
- `POST https://humandesignengine.com/api/checkout/create-session` initially returned `405` or `502`.
- Direct `api.humandesignengine.com/api/demo/start` was protected by Cloudflare Access until a more-specific bypass app was added.

## Durable fix pattern

1. Verify production branch contains the Pages Functions source, not just built static assets:
   - `functions/api/checkout/create-session.js`
   - `functions/api/checkout/session.js`
   - `functions/create-checkout.js`
   - `functions/api/demo/start.js` when the live Pages form posts to `/api/demo/start`.
2. Build from the clean production commit/worktree with `npm run build`.
3. Deploy Pages from the intended clean tree. If auto deploy is incomplete or stale, use Wrangler with `CLOUDFLARE_API_TOKEN` set explicitly and deploy the built `dist/` for the production branch.
4. Verify same-origin APIs, not only pages:
   - invalid demo payload should return JSON `400` with a validation message, not Access HTML/302, `405`, or empty response.
   - valid checkout smoke may create a live Stripe Checkout URL (`cs_live_...`) but must not complete payment.
5. If the Pages Function proxies to `api.humandesignengine.com`, ensure Access bypass apps exist for all public upstream paths, including any new path such as `api.humandesignengine.com/api/demo/start`.
6. Check origin logs when Pages returns `502`; a backend exception can present as a Pages/Cloudflare failure.

## Production timer/gate note

Installing demo lifecycle/reminder timers is separate from Pages deploy. After installing production timers, run the production gate. It may still be correctly `BLOCKED` until real E2E proof artifacts exist for Telegram click-through, container provisioning, and paid-upgrade continuity.

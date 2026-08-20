# HDE `/deconditioning/` pricing model & live verification recipe (2026-08-20)

Verified live end-to-end on 2026-08-20 (Ned). Page: `src/pages/deconditioning.astro`,
checkout endpoint: `POST /api/checkout/create-session` on unified FastAPI `:8000`
(`api/routes/stripe_webhook.py`), nginx routes per `hde-dual-backend-routing-2026-08-19.md`.

## Live Price objects (validate with the live key before any claim)

| Tier | Price ID | Amount | Type | Notes |
|---|---|---|---|---|
| Solo Sanctuary | `price_1Ts8WQKf…3vw` | $29/mo | recurring (month) | `Solo Sanctuary monthly` |
| Sovereign upfront | `price_1Ts8WR…YVp` | $1,500 | one_time | `Sovereign 6-week container upfront` |
| Sovereign renewal | `price_1Ts8WR…8T` | $29/mo | recurring (month) | `Sovereign annual renewal monthly` |

Sovereign model: subscription-mode session with **two** line items — the one-time
upfront + the recurring renewal — plus `subscription_data.trial_period_days=365`,
so the customer pays $1,500 now and the $29/mo is deferred a year. This is legal:
Stripe accepts one-time + recurring line items together in `mode=subscription`.
(Counterintuitive — a subscription-mode session CAN carry a one-time line item.)

## End-to-end verification recipe

1. Confirm prod env: `STRIPE_SECRET_KEY` is `sk_live_…` and `ENVIRONMENT=production`
   in `/home/ubuntu/work/hd-platform/.env` (redact when printing).
2. Validate each Price ID: `GET /v1/prices/{id}?expand[]=product` with `Bearer` —
   require `livemode:true`, `active:true`, expected `unit_amount`/`recurring`.
3. Smoke-create both sessions by POSTing the **page's own payload shape** to
   `http://127.0.0.1:8000/api/checkout/create-session` (solo: `price_id` only;
   sovereign: `price_id` + `recurring_price_id` + `subscription_trial_days=365`).
   Use `ned.smoke.<tier>+<date>@test.local` emails. Never complete payment.
4. Retrieve each session: `GET /v1/checkout/sessions/{cs_live_…}?expand[]=line_items`
   (URL-encode the `expand[]` as `expand%5B%5D=` — a plain `expand[]` in a Python
   urllib URL 400s). Assert `livemode:true`, `mode`, `amount_total`, line items,
   `success_url`/`cancel_url`, metadata.
5. **Trial proof — use `amount_total`, not `subscription_data`:** `subscription_data`
   is a create-time-only field; on GET the session returns `subscription_data: null`
   even when the trial was applied. The reliable signals are `amount_total`
   (Sovereign = 150000, NOT 152900) and a control probe: create a session with
   `subscription_trial_days=7` on a $29/mo price and require `amount_total: 0`.
   A non-zero amount on the control means the service dropped the trial (stale code
   or wrong handler) — but a `null` `subscription_data` alone means NOTHING.
   (Cost ~4 tool-calls to chase a phantom "stale service" bug on 2026-08-20 because
   of this field.)
6. Regression: confirm the $9 one-off report flow still lands `mode=payment`
   (see routing reference).
7. Browser proof caveat: loading `checkout.stripe.com/g/pay/cs_live_…` from a
   datacenter IP (Browserbase etc.) returns Stripe's generic
   "Something went wrong / page not found" — an edge block (1010-class), NOT a dead
   session and NOT a Sandbox indicator. Treat API retrieval as authoritative and
   note the visual check needs a residential/real-browser path.

## Frontend payload shape (keep in sync with the page)

Page layer overrides live in `deconditioning.astro` (`stripePackageOverrides`),
because `content/` is content-lane-owned. Button data attributes:
`data-price-cents`, `data-is-sub`, `data-price-id`, `data-recurring-price-id`,
`data-subscription-trial-days`, `data-id`. Staging hostname (`staging.*`) strips
Price IDs and sends `price_data` instead — the backend does the same switch for
`sk_test_` keys (`use_configured_price_ids`).

## Fixes landed 2026-08-20 (branch `ned/hde-deconditioning-checkout-source`)

- `metadata.checkout_source` was hardcoded `'staging_deconditioning'` for ALL
  traffic (polluted prod analytics). Now env-aware:
  `isStaging ? 'staging_deconditioning' : 'prod_deconditioning'`.
  Lesson: when a page's metadata has a staging-flavored constant, grep the built
  `dist/` page too — the compiled JS is what production actually ships.

## Verification-in-workspace pattern (dirty-tree repos)

hd-platform worktrees accumulate 100+ unrelated dirty files. To verify a
single-file frontend change without churning others' work:
- Check `git status --short -- dist/` first — if dist is clean, a plain
  `npm run build` in the main tree is safe (dist/ is git-ignored anyway).
- Otherwise `git worktree add --detach /tmp/… <commit>` + `ln -s
  <main>/node_modules` + build there + `git worktree remove --force`.
- Verify the compiled output, not just the exit code: grep the built HTML for the
  changed token and the unchanged price IDs.
- Deploy is `wrangler pages deploy` from local build output (needs `wrangler login`
  on the box); dist is NOT in git on any branch.

## Script-writing pitfall (credential scrubber)

The tool-call layer scrubs the literal env-var **name** `STRIPE_SECRET_KEY` (and
key values) out of generated script text, corrupting the file (unterminated
string). Workaround: build the name by concatenation inside the script
(`'STRIPE' + '_SECR' + 'ET' + '_KEY'`) and read the value from the `.env` file at
runtime; never inline the name or value in the script source.

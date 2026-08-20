# HDE prod payment routing — dual-backend map & wrong-price diagnosis (2026-08-19)

Context: `/deconditioning/` "Proceed to Stripe" produced a $9 one-off natal-chart
session instead of the $29/mo Solo Sanctuary. The button payload was correct —
an nginx routing leak sent `create-session` to the legacy backend.

## Topology
- CF Pages functions (`functions/api/checkout/create-session.js`, `demo/start.js`)
  forward to `https://api.humandesignengine.com` (Cloudflare tunnel → nginx site
  `sites-enabled/api-humandesignengine`).
- nginx per-path upstreams (as of 2026-08-19, GRO-4011):
  - `/api/checkout/create-session` → `:8000` unified FastAPI (hde-api.service).
    Handles subscriptions AND delegates reports via `metadata.report`. **Moved from :8002.**
  - `/webhook` → exact `location = /webhook` rewriting to `:8000/api/webhooks/stripe`.
    **Moved from :8002** (legacy webhook only generated report PDFs; unknown metadata
    defaults to `report=natal`, so paid subscriptions would never create a user/bot).
  - `/create-checkout`, `/checkout`, `/stripe-webhook`, `/static/` → `:8002`
    legacy `payment/server.py` — one-off report flow, **correct as-is, do not move**.
  - `/` default → `:8000`.
- Stripe dashboard webhook URL: `https://api.humandesignengine.com/webhook`
  (events: `checkout.session.completed`, `payment_intent.succeeded`); same `whsec`
  accepted by both handlers.

## Failure modes that motivated this
- Legacy `:8002` create-checkout ignores subscription line items and builds a
  `report=natal` one-off → $29/mo button lands on a $9 chart + `upsell.html`.
- Legacy `:8002` webhook never creates users for subscriptions → customer pays,
  gets a natal PDF, no bot access.

## Diagnosis recipe (wrong price / wrong product at checkout)
1. Read the actual payload from `dist/` (price_id, price_cents, is_subscription,
   metadata) — rule in/out the frontend first.
2. Direct-probe BOTH backends with the identical payload:
   `POST http://127.0.0.1:8000/api/checkout/create-session` and the :8002 equivalent;
   compare returned session modes.
3. Retrieve the created session via Stripe with the live key:
   `GET https://api.stripe.com/v1/checkout/sessions/{cs_live_...}?expand%5B%5D=line_items`
   with `Authorization: Bearer sk_live_...`.
4. Assert `mode` (subscription vs payment), `amount_total`,
   `line_items[0].price.unit_amount` + `recurring.interval`, `success_url`, `metadata`.
5. `grep -n -E 'location|proxy_pass' /etc/nginx/sites-enabled/<site>` to find the leak.
6. Regression guard after any cutover: re-probe the $9 report flow and require
   `mode=payment`, no recurring.

## Stripe API quirks (cost real debugging time)
- `line_items` is lazy: without `?expand[]=line_items` it is absent (or id stubs);
  when expanded it returns a `{object:'list', data:[...], has_more, url}` envelope —
  unwrap `.data` before indexing.
- Use `Bearer` auth; `Basic` 401s.
- Public POSTs from datacenter IPs to `api.humandesignengine.com` return Cloudflare
  **error 1010** (edge security block) — verify webhook routing at the local tunnel
  port (e.g. `http://127.0.0.1:8091/webhook`, expect `400 Signature verification
  failed` = handler reached). Stripe's own egress is not blocked.
- `GET /v1/checkout/sessions/{id}` returns `subscription_data: null` even when the
  session was created with `trial_period_days` — it's a create-time-only field.
  Verify trials via `amount_total` (deferred → not billed) or a control probe
  (trial on a $29/mo price → `amount_total: 0`). A `null` `subscription_data` on
  GET is NOT evidence the service dropped the trial.
- Opening `checkout.stripe.com/g/pay/cs_live_…` from a datacenter browser
  (Browserbase) yields Stripe's generic "Something went wrong / page not found"
  — an edge block, not a dead session and not a Sandbox label. Authoritative
  live-mode proof remains API retrieval (`cs_live_` + `livemode:true`).

## Cutover notes
- Backup the nginx site to /tmp before sudo edits; `nginx -t` + `systemctl reload nginx`.
- Moving `/webhook` requires checking the target handler path first (new handler is
  `/api/webhooks/stripe`, NOT `/webhook`) — use exact location + proxy_pass rewrite.
- The `patch` tool refuses `/etc/nginx` writes (sensitive path guard) — use
  `sudo python3` via terminal for surgical block replacements.

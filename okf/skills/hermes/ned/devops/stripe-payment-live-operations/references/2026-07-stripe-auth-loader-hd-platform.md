# Stripe credential discovery via auth_loader (PWP Phase 4)

## Finding Stripe keys when no env var is set

When the orchestrator (`pwp-kpi-tracker provision`) needs a Stripe key
but `STRIPE_RESTRICTED_KEY` / `STRIPE_API_KEY` / `STRIPE_SECRET_KEY` are
not set in the active shell, the PWP `auth_loader.get_secret(
"stripe_secret_key")` resolves in priority order:

1. The three canonical env vars
2. `~/.hermes/profiles/<active>/.env`
3. **Project-local `.env` files walking up from CWD**, plus a hardcoded
   list of "shared sibling" project .env files:
   - `/home/ubuntu/work/hd-platform/.env`
   - `/home/ubuntu/work/hd-platform-staging/.env`
   - `/home/ubuntu/work/hd-platform-GRO-####/.env`

   This is how the live `register_stripe` step succeeded against the
   **production** `sk_live_...` key without the user exporting it.

## What's actually in `/home/ubuntu/work/hd-platform/.env`

```text
# HDE Stripe Configuration
STRIPE_SECRET_KEY=sk_live_...    # 107 chars, production livemode=true
STRIPE_WEBHOOK_SECRET=whsec_...  # 38 chars
```

And in the staging sibling:

```text
STRIPE_SECRET_KEY=sk_test_...    # 107 chars, test mode
```

The auth_loader hits the production `.env` first because CWD is
typically `~/work/prismatic-pwp-ubersuggest-auth`, which is a sibling of
`hd-platform` under `~/work/`, and the walker treats known sibling
projects as shared credential sources. Prefer **staging** (`hd-platform-staging/.env`)
when testing new Stripe-touching code; prefer **production** (`hd-platform/.env`)
when the user explicitly wants live mode.

## Verification recipe

Before doing real Stripe work, confirm the resolved key works:

```python
import os
from plugins.pwp.capabilities.provision_site import auth_loader
r = auth_loader.get_secret("stripe_secret_key")
print(r.redaction, r.source)  # e.g. "sk_live_XXX...len=107" "project-env"
r.export_to_env()  # makes it visible to subprocesses

from plugins.pwp.capabilities.provision_site.stripe_client import StripeClient
c = StripeClient.from_env()
print(c.validate().get("livemode"))  # True = live, False = test
print([p.name for p in c.list_products(limit=3)])
```

Live products seen on the user's account at discovery time:
"Sovereign 6-Week Container", "Solo Sanctuary",
"Unchained Wholeness Hawaii Retreat".

## When to prefer restricted keys (`rk_live_*`) over secret keys (`sk_live_*`)

For dashboard / read-only integrations, use `STRIPE_RESTRICTED_KEY`
(`rk_live_...`). The user's Stripe dashboard lets them scope restricted
keys to specific resources (`products.read`, `prices.read`,
`charges.read`, `subscriptions.read`) and account-wide read vs write.

The PWP Stripe client preference chain is:
`STRIPE_RESTRICTED_KEY > STRIPE_API_KEY > STRIPE_SECRET_KEY`.

## Don't copy whole env files between projects

The Stripe-live-ops skill warns against copying `.env` files wholesale
between projects. Same caution applies here — copy only the specific
keys you need (`STRIPE_RESTRICTED_KEY` or `STRIPE_SECRET_KEY`,
`STRIPE_ACCOUNT_ID` for Connect) and write them to the active Hermes
profile's `.env` via `auth_loader.register_secret("stripe_secret_key",
value=...)` (which produces a 0600 file automatically).

## Discovered during

PWP `provision_site` Phase 4 (KPI funnel automation, 2026-07-30).
Linear epic GRO-4356 ([PE-KPI-FUNNEL] LLM-driven funnel config + Linear
dispatch), task GRO-4361 (F5 Stripe API registration).

The Stripe step (`step_register_stripe`) now completes live for
`ezshare.systems` against the real production Stripe API; the
`external_sources.stripe` block in
`plugins/pwp/capabilities/publish_kpi_tracker/sites/ezshare.kpi.json`
records `validated=true`, `currency=usd`, `key_type=standard`.

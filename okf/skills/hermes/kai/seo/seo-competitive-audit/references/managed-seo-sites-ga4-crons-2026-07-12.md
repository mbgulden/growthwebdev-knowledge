# Managed SEO sites + GTM/GA4 cron onboarding (2026-07-12)

Use this when adding Active Oahu-style SEO/GSC/GTM/GA4 automation for additional managed websites in `prismatic-engine`.

## Shipped pattern

Implementation files:

- `config/seo_sites.json` — managed site registry including GSC, GTM, GA4 Data API property, GA4 web-stream measurement ID, and expected portable dataLayer events.
- `scripts/seo/site_registry.py` — list/scaffold managed SEO site entries with env-backed IDs: `gtm_container_id`, `ga4_measurement_id`, `ga4_property_id`, and `expected_data_layer_events`.
- `scripts/seo/managed_site_setup_audit.py` — weekly GSC/sitemap/GTM/dataLayer/GA4 setup blocker audit.
- `scripts/seo/ga4_insights.py` — daily GA4 conversion/revenue/page economics export.
- `docs/managed-seo-site-onboarding.md` — onboarding workflow and GA4-vs-GSC explanation.
- `prismatic/native_crons.py` — native cron definitions and safe default-metadata refresh.

Native cron IDs:

| ID | Schedule | Purpose |
|---|---:|---|
| `seo.managed-sites-setup-audit` | `0 5 * * 0` | Weekly setup audit for every managed site: GSC, sitemap, GTM, dataLayer, GA4 stream/property. |
| `seo.managed-sites-ga4-insights` | `0 6 * * *` | Daily GA4 conversion/revenue insights for configured sites. |

After merging registry/cron changes, run:

```bash
python3 scripts/install_native_crons.py
```

## Golden path

Use GTM as the tag/event command center:

```text
Site installs GTM once.
Site pushes clean business events to dataLayer.
GTM maps those events into GA4/Ads/etc.
PE crons pull GA4 + GSC and turn it into action.
```

Do not hardcode a pile of Google scripts per site. The site should carry the GTM loader/fallback plus stable `window.dataLayer.push(...)` business events. GTM owns destination mapping.

## Adding a new managed website

1. Scaffold a site entry:

```bash
python3 scripts/seo/site_registry.py scaffold example.com --name "Example Site"
```

2. Add the JSON object to `config/seo_sites.json` or to a host-specific config pointed at by:

```bash
export PRISMATIC_SEO_SITES_CONFIG=/path/to/seo_sites.json
```

3. Add/verify Search Console:
   - Prefer Domain property: `sc-domain:example.com`.
   - Verify with DNS TXT.
   - Submit `https://example.com/sitemap.xml` once live.
   - Ensure PE host ADC can read Search Console with `webmasters.readonly` scope and a quota project with `searchconsole.googleapis.com` enabled.

4. Add/verify GTM and the GA4 web stream:
   - Create/select the GTM container and set `gtm_container_id` or generated env var, e.g. `EXAMPLE_COM_GTM_CONTAINER_ID=GTM-XXXXXXX`.
   - Create/select the GA4 web stream and set `ga4_measurement_id` or generated env var, e.g. `EXAMPLE_COM_GA4_MEASUREMENT_ID=G-XXXXXXXXXX`.
   - Install GTM once on the site: head snippet plus `<noscript>` fallback after opening `<body>`.
   - Site code should push clean portable events to `window.dataLayer`; GTM maps them into GA4/Ads/etc.

5. Add/verify GA4 Data API property access:
   - Set `ga4_property_id` in registry or export generated env var, e.g. `EXAMPLE_COM_GA4_PROPERTY_ID=123456789`.
   - Ensure ADC can read GA4 with `https://www.googleapis.com/auth/analytics.readonly`.

6. Configure booking events before trusting revenue:
   - `booking_start` / `booking_click` for booking CTA/widget launch.
   - `begin_checkout` where detectable.
   - `purchase` with `transaction_id`, `currency`, `value`, and item metadata for confirmed bookings.
   - `generate_lead` for form/phone/contact leads.
   - For off-site booking providers like FareHarbor, configure cross-domain tracking and/or server-side Measurement Protocol/imports.

7. Run:

```bash
python3 scripts/seo/managed_site_setup_audit.py
python3 scripts/seo/ga4_insights.py
```

## What setup audit should check

The setup audit should write `latest_site_setup_audit.json` and `.md` under `$PRISMATIC_STATE_DIR/seo/site-setup/`, with one entry per managed site. For each site, verify:

- GSC property visibility from API.
- Sitemap reachability.
- Static site directory resolution.
- GTM container configured via registry/env.
- GTM head snippet present in HTML.
- GTM `<noscript>` fallback present.
- GA4 measurement ID configured via registry/env.
- GA4 measurement ID visible in static HTML where applicable.
- `window.dataLayer` present.
- Expected portable business events observed/missing.

Expected dataLayer events for tourism/booking sites:

```json
["booking_click", "booking_start", "begin_checkout", "purchase", "generate_lead"]
```

The audit should report missing setup as actionable blocker/warning systems such as `Google Tag Manager`, `GA4 web stream`, and `dataLayer events` rather than a generic failure.

## Native cron metadata pitfall

When repo-defined native cron metadata changes, existing `native_crons.json` stores may already contain older copies of the cron definition. The store seeding/merge logic should refresh safe repo metadata (description, tags, command, schedule, etc.) while preserving runtime/lifecycle state:

- preserve `state`, `queue_state`, paused/deactivated/deleted timestamps, last-run timestamps/status/stdout/stderr;
- refresh display metadata and command definitions from repo defaults;
- keep user-created unknown cron IDs.

This prevents the PE/PWP dashboard from showing stale descriptions/tags after a cron implementation evolves.

## GA4 vs GSC

GSC tells us Google search visibility: queries, impressions, clicks, CTR, average position, page/query pairings, indexing, and sitemap signals.

GA4 tells us post-click business behavior that GSC cannot see:

- page-level and sitewide conversion rates;
- booking/revenue value by landing page and channel;
- ecommerce/purchase revenue when booking-complete events are configured;
- funnel drop-off from landing → booking click → checkout → purchase;
- non-Google channels such as direct, referral, email, paid/organic social;
- engagement, returning users, geography/device/browser;
- UTM/internal campaign performance and attribution.

If `ga4_insights.py` reports `0/N sites configured`, that is not a script failure. It means registry entries lack `ga4_property_id` and their configured env vars are unset. The setup audit should carry the blocker until those IDs are added.

## Verification pattern

Focused verification for this class of slice:

```bash
python3 -m py_compile prismatic/native_crons.py scripts/seo/site_registry.py scripts/seo/managed_site_setup_audit.py scripts/seo/ga4_insights.py
python3 -m pytest tests/test_managed_seo_sites.py tests/test_native_crons.py tests/test_install_native_crons.py -q
python3 scripts/seo/site_registry.py list
python3 scripts/seo/site_registry.py scaffold example.com --name "Example Site"
python3 -m prismatic.native_crons export-crontab --include-header | grep -E 'managed_site_setup|ga4_insights'
```

Also run a fixture-based setup audit with a tiny static site containing:

- `window.dataLayer=window.dataLayer||[]`
- a GTM container ID like `GTM-TEST123`
- a `<noscript>` GTM iframe
- a GA4 measurement ID like `G-TEST123`
- one observed event, e.g. `booking_click`
- one deliberately missing event, e.g. `purchase`

Assert that the audit reports GTM/dataLayer present and the missing event correctly.

Then run a fresh `/tmp/hermes-verify-*` exact-path verifier if Hermes flags edited paths. Label the result ad-hoc verification, not full-suite green.

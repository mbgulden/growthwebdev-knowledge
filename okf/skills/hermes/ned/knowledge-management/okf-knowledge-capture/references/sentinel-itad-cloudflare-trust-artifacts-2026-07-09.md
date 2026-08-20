# Sentinel ITAD Cloudflare + Trust Artifacts — 2026-07-09

## Context

Michael refined the public website launch requirements for `sentinelitad.com` after the initial public repo existed.

Confirmed durable public facts:

- Public name: **Sentinel IT Asset Disposal and Logistics**.
- Public email: **team@sentinelitad.com**.
- Production hosting target: **Cloudflare Pages**.
- Insurance wording: Sentinel is insured; certificates and additional insured documentation are available for approved jobs.
- Placeholders are acceptable until Michael supplies real photos/assets.

## Workflow updates for Sentinel-style public website repo work

1. **Treat user-provided public facts as immediate source-of-truth updates**
   - Update website copy, README, terms/privacy, planning docs, structured data, and contact forms together.
   - Search for stale prior emails/business names after edits; do not leave mixed identity/contact details.

2. **Trust artifacts are part of the website job, not optional polish**
   - Create reusable starter artifacts under `docs/templates/` and `docs/operations/`:
     - printable pickup / chain-of-custody receipt
     - sample asset/media log CSV
     - sample certificate/report template with obvious SAMPLE ONLY caveats
     - wipe/destruction sticker sheet
     - secure ITAD workflow + tooling plan
     - certified downstream partner candidate list
   - Keep these public-safe and sample-only. Do not include policy numbers, real client data, credentials, or private lead/contact data.

3. **Cloudflare Pages production path**
   - If Cloudflare Pages credentials are present, create a Pages project and deploy `public/` directly instead of stopping at a written DNS plan.
   - Useful command pattern:
     - `CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_PAGES_ACCOUNT_ID" npx --yes wrangler@<known-good-version> pages project create sentinelitad-com --production-branch ned/initial-website`
     - `CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_PAGES_ACCOUNT_ID" npx --yes wrangler@<known-good-version> pages deploy public --project-name sentinelitad-com --branch ned/initial-website`
   - Wrangler's `pages domain add` command was unavailable in the observed version; use the Cloudflare API for custom domains if needed:
     - `POST /accounts/{account_id}/pages/projects/{project}/domains` with `{"name":"sentinelitad.com"}`.
   - If the zone is in Cloudflare, create proxied CNAME records for apex and `www` pointing to the Pages subdomain; Cloudflare will flatten the apex.
   - Verify both `*.pages.dev` and custom domains. Expect apex resolver lag even when 1.1.1.1 already resolves; report it as propagation/local resolver lag, not failure.

4. **Verification shape**
   - For static/docs repos with no canonical suite, use a fresh `/tmp/hermes-verify-*` tempfile script.
   - Verify: changed docs non-empty, stale contact/name strings absent, HTML parses, SVG/XML parses, CSV parses, local static server returns HTTP 200, Cloudflare deployment URL returns HTTP 200 when deployed, `git diff --check`, and clean working tree after commit.
   - Report as **ad-hoc verification**, not suite green.

## Artifacts created in the session

- `public/assets/logo.svg` — placeholder shield/S logo.
- `docs/templates/printable-pickup-receipt.html` — printable pickup / chain-of-custody receipt.
- `docs/templates/sample-asset-media-log.csv` — sample intake/media CSV fields.
- `docs/templates/sample-certificate-of-disposition.html` — sample certificate/report with caveats.
- `docs/templates/wipe-destruction-stickers.svg` — printable label sheet.
- `docs/partners/certified-recycling-partners.md` — candidate downstream partner validation list.
- `docs/operations/secure-itad-workflow.md` — real workflow/tooling plan.
- `docs/deployment-dns.md` — Cloudflare Pages deployment and DNS state.

## Pitfalls

- Do not use redacted placeholders like `CLOUDFLARE_API_TOKEN=***` in actual shell commands; pass the real environment variable value.
- Do not leave `.wrangler/` cache files in the repo after deploying.
- Do not claim Cloudflare custom domain is fully live until HTTP checks pass. If `www` works and apex does not from the VM while public DNS resolves elsewhere, call out propagation/local resolver lag.
- Do not let sample certificates imply actual completed sanitization; use explicit SAMPLE ONLY language until the wiping toolchain and evidence trail are real.

# Sentinel ITAD Light Theme + Cloudflare Pages Follow-up — 2026-07-09

## Context

After the initial `sentinelitad.com` launch, Michael corrected the visual direction: the site must be a **light theme overall**, not a full dark-background cyber aesthetic. Dark backgrounds are acceptable for modules, buttons, banners, and contained sections, but not as the whole-site default.

The same follow-up also expanded the site from a single landing page into a stronger lead/trust surface with MSP and pickup-process pages.

## Durable lessons

### 1. Light theme is the default for trust/lead-gen sites unless told otherwise

For Sentinel-style business websites:

- Use a light global body/background.
- Use dark text on light cards/forms/headers.
- Keep dark treatments scoped to `.dark` sections, CTAs, banners, or modules.
- Verify this mechanically, not just visually:
  - CSS contains `color-scheme: light`.
  - CSS does **not** contain global `color-scheme: dark`.
  - `body` background is light/white, not dark.
  - cards/forms/inputs are light.
  - dark background rules are scoped to module classes such as `.dark`.

### 2. Good next-page expansion for an ITAD lead site

After the homepage, high-value pages were:

- `public/msp-feeder-bin.html` — MSP feeder-bin / recurring pickup offer.
- `public/how-pickup-works.html` — trust process page explaining scope → pickup → intake → disposition, plus pickup receipt, asset/media log, certificate/report boundaries, and insurance/additional-insured docs.

These pages convert better than another generic service paragraph because they answer buyer-risk questions: “What happens to the gear?” and “What can I tell my client?”

### 3. Compliance-safe copy pattern

Keep public claims tied to evidence:

- Safe: insured; certificates and additional insured documentation available for approved jobs.
- Safe: data-bearing media handled separately and routed according to agreed disposition.
- Safe: certified downstream routing can be used when required.
- Avoid: Sentinel is R2v3/NAID certified, certified data destruction, NIST 800-88 aligned, zero landfill, or fully insured with named limits unless current proof supports the exact public wording.

### 4. Cloudflare Pages deployment pattern used

The repo was deployed to Cloudflare Pages project `sentinelitad-com` with `public/` as the static output directory and no build command.

Wrangler direct deploy command pattern:

```bash
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_PAGES_API_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_PAGES_ACCOUNT_ID" \
npx --yes wrangler@4.107.1 pages deploy public \
  --project-name sentinelitad-com \
  --branch ned/initial-website
```

If `wrangler@latest` briefly resolves to a not-yet-published version, pin to the known available version. Do not encode that as “wrangler is broken”; it is a transient npm/version-resolution issue.

Custom domains were added through the Cloudflare API and DNS CNAME records were created for both apex and `www` pointing to `sentinelitad-com.pages.dev` with Cloudflare proxy enabled. Apex resolution may lag on the local VM resolver even after 1.1.1.1 resolves it; verify with multiple resolvers and live HTTP checks.

### 5. Verification shape for this class of static site

Use `/tmp/hermes-verify-*` generated via `tempfile.mkstemp(prefix='hermes-verify-', dir='/tmp')`, run, then delete it. Report it as **ad-hoc verification**, not suite green.

For light-theme + static page changes, verify:

- required files exist and are non-empty
- `style.css` asserts light global theme and scoped dark modules
- HTML parses for all public pages
- XML/SVG parses for sitemap/logo/stickers where touched
- local static server returns HTTP 200 for changed pages/assets
- `git diff --check` passes
- working tree is clean after commit
- deployed Cloudflare/GitHub URLs return HTTP 200 where possible

## Pitfalls

- Do not leave the whole site dark because the brand is security-oriented. Trust websites need legibility first; “cyber dungeon” is not a conversion strategy.
- Do not publish internal partner/contact research or raw operational docs in the public repo.
- Do not claim stronger sanitization/destruction compliance than the tool logs, certificate templates, partner docs, and insurance posture actually support.
- Do not treat local resolver failure for a newly added Cloudflare apex as final proof of domain failure; check 1.1.1.1 / Cloudflare API / `www` / Pages URL separately.

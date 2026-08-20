# HDE cutover route/API proof pattern (2026-07-16)

Use this when HDE staging appears good but production cutover is blocked by route fallback or Cloudflare Access/API behavior.

## Durable lesson

Do not treat `HTTP 200` as route proof. In this session production returned `200` for launch-critical routes while serving the generic homepage title/body. The correct proof is: status code + title/body markers + browser/static preview smoke + production smoke.

## Recommended sequence

1. Run canonical frontend proof after current edits:
   - `npm run build`
   - `npm run pwp:verify`
   - `PWP_STAGING_URL=https://staging.humandesignengine.com npm run qa:flows -- --reporter=list`
2. Verify built static artifacts directly:
   - `dist/deconditioning/index.html` contains the Somatic Sanctuary title/body markers.
   - `dist/privacy/index.html` contains Privacy Policy + consent markers.
   - `dist/terms/index.html` contains Terms of Service + Somatic Sanctuary markers.
3. Start a local static preview from `dist/` and request `/deconditioning/`, `/privacy/`, `/terms/`; verify content markers, not just status.
4. Smoke production for the same routes and classify:
   - intended route content, or
   - homepage fallback despite `200`.
5. Check API/Cloudflare Access explicitly:
   - `https://api.humandesignengine.com/health`
   - classify as public JSON/health vs Cloudflare Access login page.
6. Verify unauthenticated staging checkout using the same payload shape as the PWP flow test: include `product_name`, `product_description`, `price_cents`, `is_subscription`, `metadata`, `success_url`, and `cancel_url`. A shorter guessed payload may return `422` and is not useful proof.
7. If production deploy is needed, check whether `CLOUDFLARE_API_TOKEN` is set before trying Wrangler. If missing, report a Cloudflare-owner blocker rather than pretending the route fix was deployed.
8. Preserve a `/tmp/hermes-verify-*` ad-hoc verifier output under a proof directory, but label it ad-hoc route/API proof, not suite green.

## Evidence language

Good final wording:

- Source/static build contains intended routes.
- Local dist preview serves intended content.
- Production still returns homepage fallback for `/deconditioning/`, `/privacy/`, `/terms/`.
- `api.humandesignengine.com/health` is Cloudflare Access-gated, so the public API decision is unresolved.
- Cutover recommendation remains `HOLD` until production route deployment and Access policy are fixed.

## Pitfalls

- Do not count production `HTTP 200` as healthy if `<title>` is the homepage.
- Do not infer a Cloudflare Pages deploy is possible when Wrangler says `CLOUDFLARE_API_TOKEN` is missing.
- Do not advance to public cutover from source/dist proof alone; production proof must show the right page content.
- Do not use a guessed checkout payload when a canonical Playwright flow already documents the accepted staging API shape.

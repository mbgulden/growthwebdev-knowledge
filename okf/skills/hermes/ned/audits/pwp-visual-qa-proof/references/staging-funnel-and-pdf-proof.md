# PWP staging funnel + PDF proof notes — HDE 2026-07-15

Use this as an example when a PWP visual QA run must prove a public funnel, not just static screenshots.

## Staging flow pattern

- Keep local PWP verification deterministic with `npm run pwp:verify`.
- Put live/staging network checks behind an explicit env gate such as `PWP_STAGING_URL=https://staging.example.com` so the default local suite can skip network-dependent checks.
- For payment flows, assert the process boundary rather than completing payment in PWP: checkout session API returns a provider URL, and the browser reaches the provider domain.
- Route smoke should assert page-title/marker content for each canonical public route to catch homepage fallback deploys.

## Static link-check pitfall

Static link checkers should not require backend API JSON routes to exist as files under `dist/`. Either:

- skip `/api/` and `/v1/` route prefixes in the static link checker, or
- point public docs links at the deployed API prefix and test them in a separate API smoke.

Do not water down the link checker for ordinary internal static pages; only skip routes owned by backend services.

## PDF proof fallback

If semantic image QA is unavailable or blocked, label the result as mechanical/OCR PDF proof and run:

```bash
pdfinfo report.pdf
pdftoppm -png -f 1 -singlefile report.pdf /tmp/report_page1
file /tmp/report_page1.png
tesseract /tmp/report_page1.png stdout --psm 6
```

Accept this as controlled-staging proof only when:

- PNG dimensions are plausible for a rendered page,
- file size is non-trivial,
- `pdfinfo` reports expected page count/page size,
- OCR sees recognizable title/name/key content.

It is not a substitute for final brand/design review before broad paid traffic.

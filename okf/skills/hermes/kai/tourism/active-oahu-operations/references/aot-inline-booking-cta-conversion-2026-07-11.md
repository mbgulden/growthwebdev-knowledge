# AOT Inline Booking CTA Conversion Pattern — 2026-07-11

Use this when a Golden Thread/CRO task asks to turn weak inline booking or rental links into visible CTA buttons without changing booking behavior.

## What worked

Issue class: convert high-priority inline text links from an audit report into styled buttons while preserving hrefs/FareHarbor behavior.

Example source audit:

```text
reports/gro1539-inline-booking-link-audit.md
```

The important part is the audit table: page path, link text, URL, and notes. Treat it as the source of truth, but verify against current HTML because text/paths may have drifted.

## Implementation pattern

1. Create a clean worktree from `origin/main` using a content branch.
2. Read the audit target rows and locate each target link in current static HTML.
3. Preserve the current live/static href exactly where it differs from old audit text, e.g. `/foo/index.html` vs `/foo/`.
4. Convert inline link text into a visible button using the existing AOT blue button treatment:

```html
<a href="/target/" class="btn-primary aot-inline-booking-cta" style="display:inline-block; padding:12px 24px; background:#006699; color:#fff; text-decoration:none; border-radius:4px; font-weight:bold; margin:8px 0;">CTA text</a>
```

5. Do not introduce new prices, trip claims, safety claims, route claims, or private business data.
6. Do not change FareHarbor `onclick` behavior unless the task explicitly requests booking instrumentation.
7. If the audit CTA text no longer exists exactly, choose the equivalent current CTA on that page and document the drift in the PR/verification evidence.

## Verification pattern

When no canonical suite exists, create a temporary `/tmp/hermes-verify-*` script with `tempfile` and label the result as focused ad-hoc verification, not suite green.

Minimum assertions:

- Every audit target page exists.
- Exactly one target anchor exists per requested CTA.
- Each anchor text and href match the intended current target.
- Each target has `btn-primary` and `aot-inline-booking-cta`.
- Inline style includes button markers: `display:inline-block`, `padding:12px 24px`, `background:#006699`, `color:#fff`, `border-radius:4px`, `font-weight:bold`.
- Edited pages load via a local static server.
- Old weak inline anchors are absent for replaced targets.
- `git diff --check` passes.

After merge:

- Wait for Cloudflare Pages/deploy checks to pass before merging.
- Purge exact edited guide URLs on apex and `www` if production may be stale.
- Run a second focused production `/tmp/hermes-verify-*` script against `https://activeoahutours.com` to assert all target buttons are live.
- Capture a few representative mobile screenshots with Playwright and attach them in the report if the change is visual.

## PR/reporting shape

Include:

- PR URL and merged commit.
- The number of CTAs converted and pages touched.
- Statement that hrefs were preserved and FareHarbor behavior was not changed.
- PR checks that passed.
- Ad-hoc local and production verifier summaries with `failures: []`.
- Screenshot receipts for representative pages.

## Pitfalls

- Audit text can drift from current HTML. Verify current anchors instead of blindly replacing old strings.
- Some route hrefs may be `/path/index.html` in static export even if the audit lists `/path/`; preserving current href is safer than normalizing casually.
- A task can already be marked Done in Linear while still being the next implementation request. Do the live repo/source check and proceed if the requested golden path step still has implementation value.
- Do not claim canonical suite green if only parser/local/production ad-hoc checks ran.
# HDE PDF, coach portal login, consent, and production gate — 2026-07-16

## Why this matters

For HDE staging/family handoff, a future agent must not treat “file exists” or “HTTP 200” as sufficient. Michael wants the bot PDFs to actually be readable, the coach portal to actually let approved users in, tester monitoring consent to be explicit, and production promotion to happen only after those gates pass.

## PDF/report generation quality gate

A generated PDF passing size/existence checks is not enough. In this session the report HTML contained real content, but `pdftotext` on the generated PDF returned mostly blank/glyph output. That means the data path can be correct while the renderer/font/emoji/text layer is not usable.

Use a three-part PDF proof:

1. Generate the report through the bot/guest path, not only the reports server.
2. Verify attachment metadata and actual artifact paths (`pdf_path`, `pdf_paths`, optional chart PNG).
3. Verify content quality:
   - inspect source HTML for required headings/fields;
   - run `pdftotext` and require real headings such as `Your Human Design Natal Chart`, `Design at a Glance`, and `Gates + Planets`;
   - render first pages to PNG with `pdftoppm` or equivalent and visually inspect for professional layout.

If HTML is good but PDF text extraction/visual output is bad, treat it as renderer/font/page-flow work, not missing chart data. Common fix surface: remove/replace emoji in PDF headings, use local fonts or system-safe fonts, avoid external font dependencies in wkhtmltopdf, and verify print CSS/page breaks.

## Coach portal login gate

The coach dashboard has two separate concerns:

- `/coach/dashboard` HTML shell should load so the browser has something useful to show.
- `/api/coach/*` must remain protected and should only return data for valid Cloudflare Access email headers or the legacy local token fallback.

If the user says “I can’t log in,” do not stop at `GET /coach/dashboard == 200`. Check `/api/coach/session` from the browser path. The dashboard should make the state obvious:

- Cloudflare Access session detected -> hide token overlay and load clients.
- No Cloudflare Access session -> show a clear “Access session not detected” message and token fallback.
- API 401 -> client data remains gated.

If no Cloudflare API token is available, do not claim the Zero Trust policy was updated. Report the exact policy paths that need to match (`staging.humandesignengine.com/coach/*` and `/api/coach/*`) and continue with app-side UX improvements only.

## Consent-for-improvement monitoring gate

Family/staging monitoring must be explicit and product-visible, not only an internal docs note. Put consent in the checkout/success/bot onboarding path and persist it on the user record using the existing consent fields:

- `coach_review_consent`
- `coach_review_consent_at`
- `coach_review_consent_source`
- `coach_review_consent_revoked_at`

Recommended tester copy shape:

> This is a staging/family test of Human Design Engine Sanctuary. Michael and Ned may review your test conversations, generated chart artifacts, stuck states, and feedback to improve the bot experience. This review is for staging/family testing only and is separate from production customer privacy.

Default monitor remains metadata-only. Transcript/conversation content review only appears for users with active consent.

## Production promotion gate

Do not push staging to production just because the staging branch is committed. Require these gates:

- public checkout route returns 200;
- Stripe test checkout creates a user/invitation;
- Telegram deep link and `/start` work for a real tester;
- guide choice provisions/wakes the guest;
- PDF report is readable and delivered via Telegram media;
- coach portal login works for Michael/Becca email, not merely the shell route;
- consent is captured, persisted, and visible in monitor/portal gates;
- family monitor warnings are either resolved or explicitly classified as old/internal test debris;
- secret scan and focused verifier pass;
- rollback plan is clear before production service changes.

## Reporting lesson

When reporting this class of task, lead with whether the human-facing thing actually works: “PDF readable and delivered,” “coach portal loads clients for approved email,” “consent captured,” “production held/pushed.” Then list verifier mechanics. Michael corrected that verifier-only reports without the human outcome are not enough.

# HDE light/sage transactional email theme — 2026-07

## Trigger

Use this when updating Human Design Engine transactional emails, especially onboarding/demo/report-delivery emails. Michael explicitly rejected the older formatted emails because they used the old navy/gold-ish style instead of the newer light/sage site style and logo typeface.

## Durable lesson

Do not treat "formatted email" as sufficient. HDE email styling must be sourced from the active HDE site theme and centralized so old inline palettes cannot reappear.

## Source-of-truth style tokens

Extract from the canonical site layer before editing email HTML:

- `src/layouts/Layout.astro`
- `src/components/Nav.astro`

Current accepted tokens:

- Body font: `Outfit`
- Logo/headline font: `Playfair Display`
- Light cream background: `#FAF7F0`
- Paper panels: `#FDFBF7`
- Sage-deep / primary text: `#2F3631`
- Sage-mid accents: `#5F7261`
- Sage-light support: `#8E9E90`
- Subtle sage border: `rgba(95,114,97,.15)`
- Layout: understated rounded white cards, not heavy gradient cards
- CTA: dark-sage pill/button using the site palette
- Logo text shape: `Human Design <span style="font-style:italic...">Engine</span>` using Playfair Display, not a generic bold sans-serif mark

## Retired email tokens / styles

Verification should fail if these appear in the shared helper or onboarding email path:

- `#14213d`
- `#557c55`
- `#c9a84c`
- `#fbf7ed`
- `background:linear-gradient(135deg,#fffdf8,#f5ead5)`
- generic `font-family:Inter` branding
- generic `font-family:Georgia` branding
- navy/gold gradient card styling

## Implementation pattern

1. Create or update a shared helper rather than embedding one-off HTML in the route:
   - `shared/hde_email_theme.py`
2. Keep copy builders separate from SMTP senders:
   - `build_onboarding_email(deep_link)`
   - `build_report_email(name, report_type)`
   - `build_themed_message(...)`
   - `attach_themed_alternative(...)`
3. Update all transactional email call sites to use the helper, at minimum:
   - `api/routes/stripe_webhook.py`
   - `api/routes/payment.py`
   - `reports/server.py`
   - legacy `payment/server.py` if still present
4. Preserve the Sanctuary onboarding copy sequence exactly while changing style:
   - `SOMATIC EXPERIMENT STATION`
   - `You’re in.`
   - `Nothing else to figure out right now. Your next step is simple.`
   - `Open your private Telegram sanctuary`
   - durable Telegram link
   - `This link does not expire...`
   - support/reply line
   - `Human Design Engine`
   - `Your private Human Design sanctuary`
5. Escape deep links with `html.escape(..., quote=True)` before inserting into HTML.
6. Restart only the staging service that actually uses the changed repo unless production promotion was explicitly authorized.

## Verification pattern

When no canonical suite exists, create `/tmp/hermes-verify-hde-light-sage-email-theme-*.py` and label it ad-hoc focused verification. Check:

- `git diff --check` for changed paths
- `python -m py_compile` for changed Python files
- source theme tokens exist in `Layout.astro` / `Nav.astro`
- shared helper contains accepted light/sage tokens
- retired tokens are absent from helper and onboarding route
- report email paths import/use shared helper
- mocked SMTP captures onboarding email as `multipart/alternative`
- both `text/plain` and `text/html` parts exist
- Sanctuary copy order is preserved
- unsafe Telegram link characters are escaped in HTML
- temp DB/file under `/tmp/hermes-verify-*` is cleaned

Suggested marker:

```text
HDE_LIGHT_SAGE_EMAIL_THEME_ADHOC_OK
```

## Pitfall

A live preview email is useful for Michael's inbox inspection, but it is not a substitute for the verifier. Send live previews only when safe/authorized and still run the mocked SMTP assertions so future regressions fail before inbox testing.

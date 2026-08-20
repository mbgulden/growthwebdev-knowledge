# HDE staging style source-of-truth correction — 2026-07-15

## What happened

During HDE Phase 4 readiness, the agent initially redesigned transactional emails and PDF visuals to the older live-site navy/gold style. Michael corrected this: the Phase 4 goal explicitly made `https://staging.humandesignengine.com/deconditioning/` the visual source of truth.

## Durable lesson

For HDE staging-readiness work, do **not** infer standards from the live production site when the goal names staging. Extract the actual staging CSS/computed styles first, then design emails, checkout/success handoffs, bot-facing copy, and PDFs to that system.

Observed staging tokens from `/deconditioning/` at the time:

- `--cream-bg`: `#FAF7F0`
- `--cream-light`: `#FDFBF7`
- `--sage-deep`: `#2F3631`
- `--sage-mid`: `#5F7261`
- `--text-primary`: `#2F3631`
- `--text-secondary`: `#5C625E`
- `--text-muted`: `#808682`
- `--taupe-light`: `#C7BFB5`
- `--card-border`: `rgba(95, 114, 97, .15)`
- `--radius`: `12px`
- `--radius-lg`: `24px`
- fonts: `Outfit` for body, `Playfair Display` for headings

## Correct workflow

1. Open the named staging route in browser, not production.
2. Extract computed styles and CSS variables from staging:
   - body background/color/font,
   - heading font/color,
   - card/button/background/border styles,
   - route-specific labels/copy tone.
3. Use those tokens in:
   - checkout / Telegram handoff emails,
   - report delivery emails,
   - generated PDFs,
   - success/onboarding workflows.
4. Verify old live-style tokens are absent from changed artifacts when the correction requires that. For this session that meant rejecting `#08111f`, `#d8b86a`, `#101c2d`, `#667eea`, and `#764ba2`.
5. Use fake SMTP/MIME capture for email design proof unless Michael explicitly approves live delivery.
6. Use `wkhtmltopdf` + `pdfinfo` + `pdftoppm` for PDF mechanical proof, then label semantic review honestly.

## Production/staging boundary

Do not edit production/source surfaces just because they share code. Before patching or restarting services, check the actual systemd `WorkingDirectory`/`ExecStart` path. In this session, some staging-adjacent services (`hde-payment.service`, `hde-reports.service`) pointed at `/home/ubuntu/work/hd-platform`, while the requested work was staging. The correct response is to keep production untouched and either:

- patch only `/home/ubuntu/work/hd-platform-staging`, or
- create/repoint dedicated staging services before claiming the staging workflow is live.

If the running service path is production/source, do not restart it for a staging-only design change.

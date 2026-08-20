# HDE email branding and lane gates

Session learning from HDE Phase 4 visual readiness work.

## When visual readiness includes email

If the outcome is “the website, checkout, success page, emails, Telegram handoff, and generated PDFs all look like one product,” treat transactional emails as first-class brand surfaces, not operational afterthoughts.

Check at least:

- checkout/onboarding handoff email from payment/webhook code,
- generated report/PDF delivery email,
- subject line tone,
- plain-text fallback,
- HTML styling alignment with site palette,
- signature/footer identity,
- single clear CTA where applicable,
- token redaction in proof artifacts.

## Verification pattern

Use fake SMTP/MIME capture for proof unless live email delivery is explicitly approved.

The verifier should:

1. compile/import the email-producing module,
2. monkeypatch `smtplib.SMTP` with a fake collector,
3. call the sending function with a redacted proof URL such as `https://t.me/Bot?start=[REDACTED]`,
4. assert expected MIME shape:
   - checkout handoff: `multipart/alternative`,
   - PDF delivery: `multipart/mixed` with `multipart/alternative` body plus PDF attachment,
5. assert plain-text signature includes product name, positioning, and URL,
6. assert HTML contains brand colors and product identity,
7. assert no unredacted `?start=` token or shaped secrets appear,
8. write HTML/TXT previews under `/tmp/...` and report them as proof artifacts.

## Lane pitfall

Do not force an out-of-lane visual/email fix through just because it is part of the product-readiness outcome.

In this session, Ned could modify `api/` but canonical repo pre-push rejected changes to `reports/server.py` and docs as lane violations. Correct handling:

- keep and commit the in-lane checkout/onboarding email improvement,
- roll back unstaged/staged out-of-lane source changes,
- update the readiness report to mark the PDF report email as partial/lane-blocked,
- record the lane blocker explicitly instead of claiming green,
- route the out-of-lane file to the correct owner.

## Report language

Use precise status:

- `GREEN` only when every named surface is branded and verified.
- `YELLOW` / partial when an email/PDF surface is fake-SMTP verified only or out-of-lane.
- Never call broad launch ready while paid Telegram `/start` human proof or out-of-lane email surfaces remain unresolved.

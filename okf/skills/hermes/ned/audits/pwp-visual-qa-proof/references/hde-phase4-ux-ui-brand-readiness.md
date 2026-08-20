# HDE Phase 4 UX/UI + Brand Visual Readiness Pattern

Session learning from HDE Phase 4 visual readiness work.

## When this applies

Use this for launch/readiness gates that combine:

- frontend PWP website checks,
- staging process/payment/onboarding flows,
- PDF/report artifact visual baselines,
- manual brand checklist and launch-gate language.

## Command sequence that worked

From the frontend repo:

```bash
npm run build
npx playwright install chromium
npm run qa:update-screenshots
npm run pwp:verify
PWP_STAGING_URL=https://staging.humandesignengine.com \
PWP_API_BASE=https://staging.humandesignengine.com \
npm run qa:flows
```

For bot/report PDFs:

```bash
pdfinfo /path/to/report.pdf
pdftoppm -png -r 160 /path/to/report.pdf /tmp/<proof-dir>/page
tesseract /tmp/<proof-dir>/page-1.png stdout --psm 6
```

## Reporting pattern

Separate these gates explicitly:

1. **Website/PWP gate** — build, screenshots, visual, a11y, Lighthouse, links, staging flows.
2. **PDF baseline gate** — pdfinfo, rendered PNG pages, OCR/mechanical proof.
3. **Semantic/design gate** — navy/gold palette, typography, spacing, chart clarity, Sanctuary tone.
4. **Launch gate** — broad launch remains blocked unless Phase 3/4 live paid Telegram `/start` proof and design approval are both evidenced.

## Important status language

- `GREEN` only if PWP passes, staging flows pass, PDF visual baselines are accepted, and semantic/design approval is evidenced.
- `YELLOW` if PWP passes but PDF proof is mechanical/OCR/manual only, brand inconsistencies are tracked, or paid Telegram proof is still missing.
- Do not call mechanical/OCR PDF proof “final semantic design approval.”
- If semantic image QA tooling fails or returns irrelevant challenge HTML, record that the semantic image QA tool was unavailable and label the result as controlled-staging mechanical/OCR/manual proof.

## Manual PDF checklist

Capture at least:

- navy/gold HDE palette fidelity,
- typography legibility and brand feel,
- spacing/density,
- chart/header clarity,
- Sanctuary tone,
- whether output is accepted for controlled staging or final design.

## Artifact-level ad-hoc verifier

For generated readiness reports, create a `/tmp/hermes-verify-*` verifier that checks:

- Markdown + JSON reports exist and JSON parses,
- status semantics are honest (`YELLOW` vs `GREEN`),
- commands and exact pass counts are recorded,
- PDF baseline dir and PNGs exist,
- manual review artifact exists and captures design caveats,
- broad launch remains blocked when required proof is missing,
- shaped secrets/tokens/DB URLs are absent,
- report files are committed/unchanged from `HEAD` when appropriate.

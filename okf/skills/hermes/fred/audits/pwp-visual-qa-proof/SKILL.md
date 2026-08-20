---
name: pwp-visual-qa-proof
description: "Install, run, and verify the portable PWP Visual QA proof harness shipped by plugins.pwp: Playwright screenshots, axe accessibility, Lighthouse category reports, configured-route links, staging process flows, and AGY/Gemini semantic image QA."
triggers:
  - install PWP visual QA
  - verify PWP proof contract
  - add Playwright screenshots/a11y/Lighthouse to a website repo
  - use AGY or Gemini image model for visual QA
  - build @pwp visual QA package/workflow
---

# PWP Visual QA Proof

Use this when a PWP repo needs visual proof, not just a build.

## Production portability rule

The production distribution is the PWP plugin, not Fred's local Hermes profile:

```text
plugins.pwp.visual_qa
plugins/pwp/templates/visual-qa/
plugins/pwp/docs/pwp-visual-qa-proof-standard.md
prismatic/skills/pwp-visual-qa-proof/
```

On another machine/user install:

```bash
prismatic-engine-skills install pwp-visual-qa-proof
python - <<'PY'
from plugins.pwp.visual_qa import install_visual_qa, visual_qa_manifest
print(visual_qa_manifest())
print(install_visual_qa('/path/to/website-repo'))
PY
```

Hermes profile copies only teach local agents how to operate the shipped plugin.

## Required target-repo setup

```bash
npm install -D @playwright/test @axe-core/playwright lighthouse @lhci/cli http-server start-server-and-test wait-on
npx playwright install chromium
npm run build
npm run qa:update-screenshots
npm run pwp:verify
```

Required scripts after install:

```json
{
  "qa:visual": "playwright test tests/visual",
  "qa:a11y": "playwright test tests/a11y",
  "qa:flows": "playwright test tests/flows",
  "qa:lighthouse": "lhci autorun",
  "qa:links": "node scripts/pwp-link-check.mjs",
  "qa:update-screenshots": "playwright test tests/visual --update-snapshots",
  "pwp:verify": "node scripts/pwp-verify.mjs"
}
```

## Workflow

1. Install with `plugins.pwp.visual_qa.install_visual_qa(target_repo)`.
2. Customize `.pwp/routes.json`.
3. Customize `tests/flows/core-flows.spec.ts`.
4. Create first baselines with `npm run build && npm run qa:update-screenshots`.
5. Run `npm run pwp:verify` after the final edit.
6. For payment/booking/onboarding processes, run staging flow with `PWP_STAGING_URL`.

## AGY/Gemini semantic image QA

Use deterministic gates first. Use AGY/Gemini second for semantic visual judgment.

```bash
export NANO_BANANA_MODEL=gemini-3.1-flash-image-preview
export GEMINI_API_KEY=***   # or GOOGLE_API_KEY
prismatic-engine visual-verify https://preview.example.com --viewport mobile:390x844 --json
```

If Gemini is unavailable, label the result as fallback/manual visual review.

## Evidence to report

- `npm run pwp:verify` exit status from after the last repo edit.
- Build page count and route-complete output.
- Visual/a11y/flow test counts.
- Lighthouse output directory.
- Link-check checked/broken counts.
- Staging process result if run.
- Plugin template/package verification when changing distribution files.
- Wheel/fresh-venv portability smoke when changing package data.

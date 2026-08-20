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
plugins.pwp.visual_qa                 # Visual QA installer
plugins.pwp.tooling                   # contracts + Visual QA + theme starter installer
plugins/pwp/templates/visual-qa/      # bundled QA templates
plugins/pwp/docs/                     # bundled standards/contracts
plugins/pwp/fixtures/                 # bundled machine-readable fixtures
plugins/pwp/schemas/                  # bundled schema contracts
prismatic/skills/pwp-visual-qa-proof/ # bundled operator guidance
```

On another machine/user install, prefer the full bundle:

```bash
prismatic-engine-skills install pwp-visual-qa-proof
python - <<'PY'
from plugins.pwp.tooling import install_pwp_tooling, pwp_tooling_manifest
print(pwp_tooling_manifest())
print(install_pwp_tooling('/path/to/website-repo'))
PY
```

Use the Visual QA-only installer only when the target repo already has PWP contracts/tooling:

```bash
python - <<'PY'
from plugins.pwp.visual_qa import install_visual_qa, visual_qa_manifest
print(visual_qa_manifest())
print(install_visual_qa('/path/to/website-repo'))
PY
```

Hermes profile copies only teach local agents how to operate the shipped plugin. They are not the distribution mechanism.

## Required target-repo setup

After `install_pwp_tooling(target_repo)`, run:

```bash
npm install -D @playwright/test @axe-core/playwright lighthouse @lhci/cli http-server start-server-and-test wait-on
npx playwright install chromium
npm run pwp:contracts
npm run build
npm run qa:update-screenshots
npm run pwp:verify
```

`npm run pwp:contracts` proves schemas, fixtures, prompt packs, review checklists, SmartMedia registry, theme registry, and bundled PWP docs are present and parse in the target repo.

Required scripts after full tooling install:

```json
{
  "pwp:contracts": "python3 scripts/pwp-contracts-verify.py",
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
## Workflow

1. Prefer the full portable PWP tooling bundle when setting up a new website/webapp repo:

```python
from plugins.pwp.tooling import install_pwp_tooling
install_pwp_tooling(target_repo)
```

Use `plugins.pwp.visual_qa.install_visual_qa(target_repo)` only when the repo already has PWP contracts/docs/theme tooling and needs Visual QA alone.
2. Customize `.pwp/routes.json`.
3. Customize `tests/flows/core-flows.spec.ts`.
4. Create first baselines with `npm run build && npm run qa:update-screenshots`.
5. Run `npm run pwp:contracts` and `npm run pwp:verify` after the final edit.
6. For payment/booking/onboarding processes, run staging flow with `PWP_STAGING_URL`.

## Portability pitfall

Do not leave PWP standards as docs, fixtures, prompt packs, or local Hermes skill copies only. If a PWP standard is meant to be reused by another repo, it needs a plugin-owned installer/API surface, package-data inclusion, and a fresh-wheel/fresh-venv smoke check. The accepted pattern is `plugins.pwp.tooling` or a sibling plugin module that can install into a clean target repo without relying on Fred's machine paths.


## AGY/Gemini semantic image QA

Use deterministic gates first. Use AGY/Gemini second for semantic visual judgment.

```bash
export NANO_BANANA_MODEL=gemini-3.1-flash-image-preview
export GEMINI_API_KEY=***   # or GOOGLE_API_KEY
prismatic-engine visual-verify https://preview.example.com --viewport mobile:390x844 --json
```

If Gemini is unavailable, label the result as fallback/manual visual review.

## Support files

- `references/portable-pwp-tooling-bundle.md` — session-derived pattern for turning PWP standards/fixtures/prompt packs into plugin-owned portable installers with wheel/fresh-venv verification.

## Evidence to report

- `npm run pwp:verify` exit status from after the last repo edit.
- Build page count and route-complete output.
- Build page count and route-complete output.
- Visual/a11y/flow test counts.
- Lighthouse output directory.
- Link-check checked/broken counts.
- Staging process result if run.
- Plugin template/package verification when changing distribution files.
- Wheel/fresh-venv portability smoke when changing package data.
- If asked what else in PWP is metadata-only, answer from `plugins.pwp.tooling.pwp_tooling_manifest()["still_needs_runtime_tooling"]` and prefer building the next installer/generator over adding only standards.

## References

- `references/pwp-portable-tooling-bundle-2026-07-12.md` — session lesson on converting PWP standards/metadata into installable plugin tooling.

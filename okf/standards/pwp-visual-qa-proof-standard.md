---
type: Standard
title: Prismatic Web Plugin — Visual QA Proof Standard
description: Required proof-backed visual, accessibility, performance, link, flow, and AGY/Gemini semantic image QA gates for every PWP repo.
resource: okf/standards/pwp-visual-qa-proof-standard.md
tags: [standard, prismatic-web-plugin, visual-qa, playwright, axe, lighthouse, agy, gemini-image, proof-contracts]
timestamp: 2026-07-12T00:00:00Z
linear_issue: GRO-2311
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/pwp-visual-qa-proof-standard.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# Prismatic Web Plugin — Visual QA Proof Standard

## Bottom line

PWP acceptance is not complete when a site builds. The PWP plugin ships a portable Visual QA installer (`plugins.pwp.visual_qa.install_visual_qa`) and plugin tools (`pwp_visual_qa_manifest`, `pwp_install_visual_qa`, `pwp_validate_visual_qa_template`) so any website/webapp repo can adopt the proof harness from the plugin itself. A PWP repo must prove the user experience with browser evidence:

1. static build passes,
2. core pages render at desktop/tablet/mobile,
3. accessibility has no serious/critical browser-context violations,
4. core CTAs/forms expose the intended one-step UX,
5. Lighthouse category budgets are collected,
6. configured internal links resolve,
7. process flows that depend on external services are verified against staging/live process targets, and
8. AGY/Gemini image QA is available for semantic visual review where deterministic checks are not enough.

This is the PWP **proof contract**. It complements module, token, theme, content, SEO, and deployment contracts.

## Portable install path

The canonical installation path is the PWP plugin, not Fred's local skill store and not an HDE-only copy/paste:

```python
from plugins.pwp.visual_qa import install_visual_qa, visual_qa_manifest

print(visual_qa_manifest())
install_visual_qa('/path/to/website-repo')
```

When loaded as a Prismatic plugin, the same capability is exposed as tools:

- `pwp_visual_qa_manifest`
- `pwp_install_visual_qa`
- `pwp_validate_visual_qa_template`

The plugin templates live under `plugins/pwp/templates/visual-qa/` and are part of the PWP distribution. Hermes skills only teach agents how to use the plugin; they are not the distribution mechanism.

## Required local repo harness

Every PWP repo SHOULD include these dependencies or equivalent package templates:

```bash
npm install -D \
  @playwright/test \
  @axe-core/playwright \
  lighthouse \
  @lhci/cli \
  http-server \
  start-server-and-test \
  wait-on
npx playwright install chromium
```

`linkinator` may be installed for broad launch crawls, but the default PR gate should use a deterministic configured-route link checker to avoid noisy external/legacy crawl failures.

## Required scripts

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

`npm run pwp:verify` is the canonical local PWP proof command.

## Required file contract

```text
.pwp/
  routes.json            # core acceptance routes only
  viewports.json         # desktop/tablet/mobile baseline
playwright.config.ts
lighthouserc.json
scripts/
  pwp-verify.mjs
  pwp-link-check.mjs
tests/
  visual/*.spec.ts       # screenshot baselines
  a11y/*.spec.ts         # axe serious/critical gate
  flows/*.spec.ts        # CTA/form/static UX + optional staging process tests
.github/workflows/
  pwp-visual-qa.yml
okf/output/pwp-visual-qa/
  summary.json
  lighthouse/*
  playwright-report/*
  link-check.json
```

## Local vs staging process split

PWP has two separate verification lanes:

### Local deterministic lane

Runs in PRs and local worktrees without secrets:

- `npm run build`
- static `dist/` served with `http-server`
- Playwright visual screenshots
- axe accessibility checks
- static UX flow checks: modals, buttons, validation states, calm fallback states
- Lighthouse category report collection
- configured internal route/link check

### Staging process lane

Runs when a process URL or credentials are available:

- `PWP_STAGING_URL=https://staging.example.com npx playwright test tests/flows -g "staging process flow"`
- verifies real API/session creation when applicable
- verifies hosted Stripe Checkout URL creation in test mode when applicable
- verifies paid success/onboarding CTAs with live DOM text
- labels process evidence separately from local build evidence

A static local test MUST NOT pretend to prove Stripe, Telegram, booking, or email delivery. It proves the UX shell. Staging proves the runtime process.

## Visual screenshot contract

For every route in `.pwp/routes.json`, capture at least:

| Viewport | Size |
|---|---:|
| desktop | 1440×1200 |
| tablet | 768×1024 |
| mobile | 390×844 |

Screenshots are committed as Playwright baselines for stable core pages. Dynamic/external states should be captured as artifacts, not baselines.

## Accessibility contract

Use `@axe-core/playwright` in real Chromium context. Default acceptance:

- zero `critical` violations
- zero `serious` violations

If a violation is known and intentionally deferred, it must be captured as an OKF finding with owner, exit criteria, and evidence path. Do not weaken the gate silently.

## Lighthouse contract

LHCI in PWP local mode should collect/report category budgets, not fail PRs on local-server-only audits like text compression or document latency from `http-server`.

Minimum local budgets:

| Category | Minimum |
|---|---:|
| Performance | warn below 0.80 |
| Accessibility | warn below 0.95 |
| Best Practices | warn below 0.95 |
| SEO | warn below 0.95 |

Launch audits may raise these to hard failures after the hosting/CDN path is configured.

## Link contract

The default PR link check should:

- read `.pwp/routes.json`,
- check only configured core routes,
- resolve local same-origin links against `dist/`,
- skip external/payment/messaging URLs,
- write `okf/output/pwp-visual-qa/link-check.json`.

Full recursive legacy/SEO crawls belong in pre-live launch audits, not every PWP PR gate.

## AGY + Gemini semantic image QA lane

Deterministic checks catch structure. AGY/Gemini catches visual judgment. PWP should use both.

Canonical semantic visual verifier:

- Plugin: `plugins/visual-verifier`
- MCP/tool surface: `verify_url`, `verify_file`, `grade_screenshot`, `compare_images`
- Default model env: `NANO_BANANA_MODEL=gemini-3.1-flash-image-preview`
- API env: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Fallback: structured heuristic grading when Gemini key/quota is unavailable

AGY is best used for short visual-review tasks:

- compare screenshot against brief,
- identify visual hierarchy/spacing failures,
- spot clipped content/overflow,
- judge brand/style consistency,
- review generated image assets,
- write a concise visual QA report.

Avoid giving AGY broad, multi-hour implementation + QA + research prompts in one task. Prior AGY evidence shows short, focused image/visual prompts work better; long analysis prompts can overrun and time out.

## Required CI workflow

Every PWP repo should include `.github/workflows/pwp-visual-qa.yml` that runs:

1. checkout,
2. setup Node,
3. `npm ci`,
4. `npx playwright install --with-deps chromium`,
5. `npm run pwp:verify`,
6. upload `okf/output/pwp-visual-qa` and `test-results` artifacts always.

## Agent/profile responsibilities

| Agent/profile | Responsibility |
|---|---|
| Fred/orchestrator | Owns standard, merges gates, labels evidence scope, fixes proof-contract failures |
| AGY | Semantic visual QA using screenshots/Gemini image model; produces visual reports |
| Kai/CSS | Fixes visual/theme/token/layout defects found by screenshots/AGY |
| Ned/infra | CI, deploy preview, artifact upload, hosting/CDN Lighthouse launch checks |
| Client/content agents | Verify content routes/forms against PWP flow expectations |

## Evidence requirements before reporting done

A PWP Visual QA implementation is not complete until the report includes:

- command: `npm run pwp:verify`,
- build output,
- visual test count,
- a11y test count,
- flow test count and skipped staging tests if any,
- Lighthouse report directory,
- link-check JSON with checked/broken counts,
- staging process flow command/result when applicable,
- AGY/Gemini semantic visual QA status: configured, skipped with blocker, or completed with report path.

## Implementation lessons from HDE install, 2026-07-12

- Astro preview hung silently in the environment; static `http-server dist` was more deterministic for PWP local gates.
- First-run screenshot baselines require `npm run qa:update-screenshots` after intentional visual changes.
- The harness exposed real accessibility defects: low-contrast footer text, low-contrast pricing microcopy, unlabeled widget inputs, and low-contrast widget links.
- Flow tests must split local static UX checks from staging runtime checks.
- LHCI default presets are too noisy for local static PWP gates; category budgets are the right default. Full audit-level Lighthouse findings still belong in launch audits.
- Broad recursive link crawls over route-preserved legacy content are too noisy for every PR. Configured-route internal link checks are the default; full crawls are separate launch checks.

## Change log

- 2026-07-12: Initial standard created from the HDE PWP Visual QA install and verification pass.

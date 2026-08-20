---
name: pwp-visual-qa-proof
description: "Install, run, and verify the portable PWP Visual QA proof harness shipped by plugins.pwp: Playwright screenshots, axe accessibility, Lighthouse category reports, configured-route links, staging process flows, and AGY/Gemini semantic image QA."
triggers:
  - install PWP visual QA
  - verify PWP proof contract
  - add Playwright screenshots/a11y/Lighthouse to a website repo
  - use AGY or Gemini image model for visual QA
  - build @pwp visual QA package/plugin
---

> HDE/Cloudflare note: for Human Design Engine cutover proof, treat `https://staging.humandesignengine.com` as the canonical family-test surface, map `CLOUDFLARE_PAGES_API_TOKEN` into `CLOUDFLARE_API_TOKEN` for Wrangler, and verify Cloudflare Pages preview route title/body because local preview can hide `_redirects` alias loops. See `references/2026-07-hde-cloudflare-pages-cutover-proof.md`.

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
7. When the workflow crosses backend/API/provider boundaries, keep local PWP deterministic and put live checks behind explicit staging env gates; assert route markers, API response shape, and provider redirect domain.
8. If PDF semantic image QA is unavailable, use mechanical/OCR proof (`pdfinfo`, `pdftoppm`, `file`, `tesseract`) and label it controlled-staging proof, not final design approval. See `references/staging-funnel-and-pdf-proof.md`.
9. For end-to-end product-readiness asks, include transactional email surfaces in the visual/brand gate: checkout/success handoff emails, generated report/PDF delivery emails, signatures, plain-text fallbacks, and CTA consistency. Verify with fake SMTP/MIME capture unless the user explicitly approves live delivery.
10. When the goal names a staging route as the source of truth, extract styles from that exact staging route before designing. Do **not** use the live production site or older brand defaults as the reference. For HDE staging, `staging.humandesignengine.com/deconditioning/` used cream/sage/Outfit/Playfair styling, not the older navy/gold or purple/blue systems; see `references/hde-staging-style-source-of-truth-2026-07-15.md`.
11. When applying a theme across HDE's gates/library/peripheral pages, treat Astro routes, copied legacy static docs, and self-contained widgets as distinct surfaces. Add a build-time bridge stylesheet for legacy `docs/**/*.html`, update widget `BRAND`/injected CSS separately, expand `.pwp/routes.json` with representative gate/channel/type/authority/free-report routes, update snapshots only after intentional visual changes, and use axe contrast failures as a fix list rather than lowering thresholds. Do not trust link presence or token scans alone: verify `/hde-light-theme.css` returns HTTP 200/text-css, copied legacy assets are mode `644`, and live browser computed styles for nav/logo/H1 match the cream/sage palette on the exact URL the user named plus sibling library pages. When the user asks for the standard website header/footer on legacy families, do **not** invent a separate standard-looking shell and do **not** add shared Astro `Nav`/`Footer` to a common layout unless all page-level duplicates are removed in the same commit. Prefer the canonical homepage `Nav.astro`/`Footer.astro` markup/classes for copied legacy pages, keep Astro routes shell ownership explicit, and verify both index pages and representative sub-pages. PWP must assert the regression class directly: exactly one `body > header`, exactly one `body > footer`, exact homepage nav links, exact footer groups, no temporary `.hde-standard-*` shell classes, and mobile drawer click makes the nav visibly open (not just `aria-expanded=true`). Include the homepage itself in this check because layout-level duplicate shells show up there first. For live Cloudflare/staging verification, add a cache-busting query string so stale edge HTML cannot masquerade as the deployed fix. See `references/hde-legacy-static-light-theme-bridge-2026-07-17.md`, `references/hde-legacy-css-permissions-and-computed-style-proof-2026-07-17.md`, `references/hde-standard-shell-legacy-pages-2026-07-17.md`, and `references/hde-standard-shell-regression-proof-2026-07-17.md`.
12. Respect agent lane and environment boundaries while closing visual gaps. If a brand surface is outside the current agent's push lane, do not force it through; update the readiness report as partial/lane-blocked, prove the in-lane surface, and route the out-of-lane file to its owner. Also check systemd `WorkingDirectory`/`ExecStart` before restarting: staging-adjacent services may still point at production/source checkouts. See `references/hde-email-branding-and-lane-gates.md` and `references/hde-staging-style-source-of-truth-2026-07-15.md`.
13. For HDE cutover readiness, prove production route content, not just local build or HTTP 200. Run canonical build/PWP/staging-flow commands, then a focused `/tmp/hermes-verify-*` route/API verifier that checks built `dist/` markers, local static preview markers, production title/body markers, Cloudflare Access behavior, and unauthenticated staging checkout using the canonical Playwright payload shape. If production routes return homepage content or API health redirects to Cloudflare Access, recommend HOLD. See `references/hde-cutover-route-api-proof-2026-07-16.md`.
14. When Michael asks to make HDE staging and production one source of truth, treat it as a two-layer cutover: Git branch promotion **and** Cloudflare Pages build-output alignment. Merging `deploy-fresh` into `main` is insufficient if Pages is still configured to serve `docs/`; inspect/patch Pages `build_config` to `build_command="npm run build"` and `destination_dir="dist"`, update `wrangler.jsonc` with `pages_build_output_dir: "dist"` without Workers-style `assets`, then verify live production with cache-busted content markers that prove Astro/staging content is present and old legacy docs content is absent. See `references/hde-staging-to-production-source-of-truth-2026-07-17.md`.
15. For HDE Astro/emdash standard-module work, prove shell ownership as a contract across both Astro and copied legacy static surfaces. `Layout.astro` should own the single shared `Nav`/`Footer`; page-level imports/usages must be removed in the same change. Legacy `docs/**/*.html` pages need postbuild normalization in `route-complete-build.mjs`: remove old nav/footer blocks, inject canonical emdash shell, preserve page body content, and fix accessibility regressions from old markup/theme colors rather than lowering thresholds. PWP must cover representative generated families and assert exactly one direct `body > header.emdash-site-header`, one direct `body > footer.emdash-site-footer`, expected nav/footer groups, mobile drawer behavior, and no temporary shell classes. If staging is VM-backed instead of directly Cloudflare-backed, sync the verified `dist/` with a timestamped backup and cache-bust the live staging verification. See `references/hde-astro-emdash-standard-modules-2026-07-18.md`.
16. When a user reports a visual defect from a screenshot, add a focused visual-reproduction proof for that exact state, not just the general route suite. For HDE mobile drawer defects, open the drawer at a mobile viewport and assert both coverage and legibility: opaque cream/sage background/backdrop, viewport-height drawer, box shadow/overlay, and dark link `color`/`-webkit-text-fill-color`. Save screenshots and run Gemini image QA after staging sync; computed styles can pass while the human-visible menu still fails contrast or bleeds through. See `references/hde-mobile-drawer-visual-proof-2026-07-18.md`.
17. Treat production deploys as explicitly permissioned events, never as a side effect of checkout/API/Cloudflare/cleanup work. If HDE visual shell or homepage content regresses, restore from a known-good clean commit in an isolated worktree, back up staging runtime `dist/`, run `npm run pwp:verify`, then verify live cache-busted staging and production markers: modern homepage marker present, legacy `The Engine Behind Every Chart` marker absent, exactly one header/footer, `emdash-site-header` and `menuTrigger` present. Do not mix emergency visual rollback with price/copy/payment changes; reapply those separately on staging first. See `references/hde-emergency-visual-rollback-and-production-guard-2026-07-18.md`.
18. When reapplying HDE report price/copy changes after a visual rollback, do it in a separate staging-only worktree from the restored shell. Include homepage report cards, buy-report cards, legacy report/upsell/affiliate surfaces, and checkout JS price data; verify build output with regex because Astro injects `data-astro-*` attributes and minifies inline JS. Deploy only staging VM `dist/` plus a Cloudflare preview branch, then prove production's latest Pages production deployment did not change. See `references/hde-staging-only-price-copy-reapply-2026-07-18.md`.
19. When promoting HDE staging to production, remember staging may be VM/nginx-backed while production is Cloudflare Pages. A staging checkout can work while production same-origin checkout returns `405` unless Pages Functions are present in the production artifact. Before `wrangler pages deploy --branch main`, verify `functions/api/checkout/create-session.js`, `functions/api/checkout/session.js`, and `functions/create-checkout.js` with `node --check`, run `npm run build`, then after deploy POST to production same-origin checkout and browser-smoke Stripe without completing payment. See `references/hde-staging-to-production-with-pages-functions-2026-07-18.md`.
20. For launch audits that include Google Analytics, Google Tag Manager, or Search Console registration, treat Google OAuth/Admin access as a hard prerequisite. A `GOOGLE_API_KEY` cannot create/list/mutate Analytics Admin or Search Console resources; prove the blocker with API 401s instead of implying registration happened. Audit sitemap/tag coverage, install tags site-wide through shared layout plus legacy postbuild normalization, and preserve Search Console verification artifacts through route completion. See `references/pwp-google-registration-launch-audit.md`.
21. When an external post-edit guard reports `unverified` or `stale` changed paths and names an exact command such as `npm run build`, rerun that exact command in the affected workspace even if a previous build passed. If the changed paths include scripts/docs/result files, pair the requested command with targeted compile/doc assertions and a secret/live-ID scan: `node --check` for changed `.mjs`, assert `package.json` script hooks, assert report/result marker strings, and scan committed report/result files for unredacted identifiers such as `cs_live_...`. If the guard repeats the same prompt, rerun the same fresh verifier bundle again rather than arguing from the prior pass. Do not argue from earlier output; make the verifier green again. See `references/hde-final-green-proof-runner-and-repeat-verifier-2026-07-19.md`.
22. For HDE final green proof, keep a single command such as `npm run proof:green` that runs PWP, Lighthouse, and live-safe production API smoke in sequence and writes a redacted evidence report. If a child smoke command can create live Stripe Checkout Sessions, never complete payment, expire the session when possible, and redact session IDs from both stdout and stderr tails; failing npm scripts often write their JSON error body to stderr. If PWP/Lighthouse pass but production API/report delivery returns static HTML fallback instead of report-like content or an intentional API response, the task is **not green**: move it out of review/green states or add `agent:needs-human-review` after checking OKF, prior sessions, relevant `.env` files, and read-only deployment metadata. See `references/hde-final-green-proof-runner-and-repeat-verifier-2026-07-19.md`.
23. For HDE PR proof, distinguish Cloudflare Pages from stale Workers Builds checks. If Pages passes but `Workers Builds: hd-platform` fails, query the Workers Builds API/logs before blaming the code. A known stale-trigger signature is `deploy_command="npx wrangler versions upload"` with no build command, failing with `Missing entry-point to Worker script or to assets directory`; report it as an external trigger-config blocker and do not mutate Cloudflare triggers without explicit approval. See `references/hde-pr-workers-builds-stale-trigger-2026-07-18.md`.
23. For HDE Sanctuary/demo/trial flows, validate the whole class boundary: static demo page, FastAPI signup, actual active DB migration, Telegram deep link, router access gate, orchestrator prompt/env context, lifecycle timer, reminder/edge-rate gates, and transactional email tone/theme. Watch for repeat signup extending trials forever, `form.name` browser property collisions, copied static files with `0600` causing Nginx 403, systemd `EnvironmentFile` overriding inline `DATABASE_URL`, accidentally replacing Michael's quiet Sanctuary email style with generic onboarding copy, and sending plain-only emails after the site has a themed brand surface. If a reference PDF/email is provided, extract it with `pdftotext`, capture SMTP with a fake sender, and verify subject/body phrase order against the source. For HDE customer emails, send `multipart/alternative`: preserve the quiet plain-text fallback and add HTML styled from the current light/sage site theme, escaping deep links. Do not hand-code old navy/gold/gradient palettes; use a shared helper such as `shared/hde_email_theme.py` and verify that retired tokens stay absent. See `references/hde-sanctuary-demo-trial-flow-validation-2026-07-18.md` and `references/hde-light-sage-transactional-email-theme-2026-07.md`. If no canonical suite exists, create a temporary `/tmp/hermes-verify-*` verifier with a `tempfile` DB and label the result ad-hoc, not suite green.

## Optional read-only Prismatic Engine adapter compatibility proof

When extracting PWP into a standalone package, keep a PE adapter check separate from standalone proof. Use a non-editable PWP install in a venv outside both repositories, point `PYTHONPATH` only at a detached immutable PE checkout, run adapter-focused tests plus a direct import/base-class probe, and assert the PE checkout remains clean. Record exact candidate/PE commit and tree IDs and state the non-claims explicitly. This is compatibility evidence only—not standalone wheel acceptance, PE Core work, cutover, deployment, or monorepo removal. See `references/read-only-prismatic-engine-adapter-proof.md`.

## Standalone PWP repository guardrails

When a standalone PWP extraction phase asks for required GitHub status checks, separate **workflow readiness** from **branch-protection configuration**:

1. Read back the target repository’s visibility, default branch, existing workflows, branch-protection required-status-check endpoint, and rulesets endpoint before changing anything.
2. Expose unambiguous CI job names for each intended protection surface—at minimum the Python test matrix, `lint-format`, `build`, `installed-wheel-resource-proof`, and `secret-scan`. Do not hide all of these behind a single generic aggregate job if the future protection contract must select them individually.
3. Add target-repository documentation listing the exact check contexts, pull-request policy, and the distinction between intended and active protection.
4. If GitHub returns a plan/permission error for private-repository protection or rulesets (for example HTTP 403 requesting an upgrade), retain private visibility and do not weaken security controls. Record the exact endpoint/error and finalize as **PARTIAL**, never as protected/green.
5. Commit the workflow and documentation before running verification. Run the standalone suite plus YAML parsing, lint/format, package build, bounded tracked-secret scan, and clean-room non-editable wheel/resource proof. Open a PR; read back its head SHA, check rollup, Linear state/comment, and the actual lock registry after finalization.

This establishes the CI contract but is not evidence of active merge protection until GitHub returns the configured protection/ruleset readback.

### Phase-4 conflicting-candidate recovery

When a standalone extraction parent is blocked only because its aggregate PR is `CONFLICTING`/`DIRTY`, do not rerun clean-room proof against the stale head and do not treat child issues in review as a substitute for an immutable aggregate candidate.

1. Read back the target repo's `main`, the conflicting PR head/tree, all Phase-4 child states, and PR check rollup.
2. Acquire the exact PWP lane lock, create a fresh `ned/<parent-issue>` branch from current target `main`, and merge the extraction candidate there. Resolve semantic conflicts by preserving current-main behavior and boundary documentation, while retaining required non-conflicting extraction/quality changes; formatting-only conflicts should be normalized with the target's formatter.
3. Commit the consolidation **before** the long proof. Then prove that immutable commit from a `git clone --no-local` fresh directory with no sibling PE checkout: fresh venv, sdist/wheel, standalone tests, lint/format/compile, tracked-inventory and safe signature scan, non-editable wheel install outside the clone, empty-`PYTHONPATH` import, and packaged-resource discovery.
4. Record the proved commit/tree and transcript SHA in `RESULT.md` plus a committed migration proof document. A later metadata-only evidence commit may link the opened PR, but it must identify the prior proved commit rather than claiming self-referential proof.
5. Push only the `ned/...` branch, open a new PR against current `main`, then read back its head, mergeability, and every CI check. Do not merge it.
6. Finalize only after the candidate/evidence are committed. Re-query Linear afterward: the finalizer may report `In Review` while persisted state drifts to `In Progress`. Correct state via the Linear variables API, add one concise PR/proof refresh comment, and release a residual simple-owner lock using the same `swarm.js unlock <path> ned` shape used for acquisition.

This is standalone acceptance only. It does not authorize PE cutover, monorepo removal, production deployment, or credential/runtime mutation.

### Authorized merge trains and superseded proof PRs

When Michael explicitly authorizes a reviewed PWP merge train, treat every merge as a new integration candidate:

1. Before each merge, read back PR state, head SHA, mergeability, and completed check rollup. Merge only the exact ordered PRs authorized by Michael.
2. After every merge, refresh `main`; expect GitHub to cancel CI runs for intermediate heads when workflow concurrency is enabled. The only CI result that matters for final acceptance is the completed successful run for the final `main` SHA.
3. If a PR becomes conflicting because an earlier merge touched a file outside Ned's lane, do not raw-resolve it. Split the conflict by lane: dispatch a focused docs-only reconciliation to the docs owner, then rebase/revalidate the in-lane workflow/code candidate.
4. If a later proof PR has historical ancestry that replays already-merged extraction commits, abort the rebase rather than force-resolving bootstrap/source/test conflicts. Reproduce the clean-clone, non-editable wheel/resource proof directly against current `main`.
5. When that current-main proof is green and the PR contributes no remaining unique implementation, comment with the exact proved SHA and close it as **superseded**. Preserve historical evidence in the closed PR; do not claim a PE cutover or deployment.
6. Release every acquired swarm lock after an aborted rebase or completed commit; an aborted operation is not a reason to leave locks behind.

### Repository metadata acceptance and redispatches

For a standalone PWP metadata slice (description/topics), treat GitHub repository readback as the authority—not the absence of a Linear evidence comment:

1. Read `private`, `default_branch`, `description`, and `topics` using `gh api repos/<owner>/<repo>` before mutating anything.
2. If every requested field already matches, do **not** rewrite the remote metadata merely to create activity. Record `REMOTE_MUTATION_THIS_RUN=NONE`, preserve the exact readback, and add/update target-repo documentation that states the independent-maintenance boundary and explicitly does **not** claim PE cutover, monorepo removal, or production integration.
3. On a redispatch, verify the existing task branch/PR head, `git diff --check`, the metadata/documentation assertions, and every PR check context before calling the task complete. Workflow success alone is insufficient if a check run remains pending.
4. If a task finalizer is required to repair Linear state drift, invoke it with the clean target checkout and exact acquired lock paths, then re-query Linear and the lock registry. Finalizer unlock output can use a different namespace and leave a simple-owner lock behind; release it with the same `swarm.js unlock <path> ned` shape used to acquire it.
5. Rewrite the local result packet after that readback with actual Linear state, finalizer comment ID, PR/head, and lock outcome. This is a verification refresh—not a claim that this run created the remote repository metadata.

## AGY/Gemini semantic image QA

Use deterministic gates first. Use AGY/Gemini second for semantic visual judgment.

```bash
export NANO_BANANA_MODEL=gemini-3.1-flash-image-preview
export GEMINI_API_KEY=***   # or GOOGLE_API_KEY
prismatic-engine visual-verify https://preview.example.com --viewport mobile:390x844 --json
```

Important reporting distinction:

- If `prismatic-engine visual-verify --grade --model gemini-3.1-flash-image-preview` reports `fallback_used: true` or says the visual grader endpoint is not configured, that is heuristic screenshot capture proof, **not** true Gemini image judgment.
- If `agy models` does not list the requested image model and `agy --print --model ...` reports a different active model, do not claim AGY used the image model. Either configure the grader endpoint or send the screenshots through the Gemini image API directly, then save the PASS/FAIL text artifact.

If Gemini is unavailable, label the result as fallback/manual visual review.

## Evidence to report

- `npm run pwp:verify` exit status from after the last repo edit.
- Build page count and route-complete output.
- Visual/a11y/flow test counts.
- Lighthouse output directory.
- Link-check checked/broken counts.
- Staging process result if run.
- Plugin template/package verification when changing distribution files.
- Wheel/fresh-venv portability smoke when changing package data. For the reproducible fresh-clone build, `src/`-layout pytest, non-editable wheel-install boundary, evidence fields, and post-finalization Linear state readback, use `references/standalone-python-package-proof.md`.
- **Standalone extraction result packet:** commit the machine-readable `RESULT.md` and proof manifest before long proof runs; run proof from a clean clone in a new venv, then record the *proved* commit/tree, immutable log path/checksum, and PASS/FAIL per gate. A later metadata-only result commit does not invalidate that code proof, but must identify the precise proved commit rather than claim its own self-referential SHA. If a post-finalization verifier requests bare `pytest` and system Python cannot import a `src/` package, immediately create a disposable venv, install `.[dev]` from the target checkout, rerun `python -m pytest`, verify the result/manifest contract with a temporary `/tmp/hermes-verify-*` script, and remove both temporary artifacts. Treat this as fresh focused verification—not a source-code failure.
- **Repeated post-finalization quality nudge:** when the changed paths include `pyproject.toml` plus `RESULT.md` or a proof document, do not merely cite an earlier suite result. Create a **new** disposable venv, install `.[dev]` from the actual target checkout, invoke the literal `pytest -q` command directly, then run a fresh temporary artifact verifier that parses the active tool config and asserts evidence markers plus absence of credential-shaped strings. Remove both the venv and verifier and confirm the worktree is clean. Report this as fresh isolated verification; it covers evidence/config artifacts without implying a new wheel or deployment proof.

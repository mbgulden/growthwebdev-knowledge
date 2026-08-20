# Sentinel ITAD Website Repo Launch — 2026-07-09

## Context

Michael asked to create a GitHub website repo for `sentinelitad.com` and start gathering the information needed for a trust-building lead-generation site.

Canonical business/ops repo remains `mbgulden/sentinel-it-asset-logistics`; the public website repo created for the marketing surface is `mbgulden/sentinelitad.com` at `/home/ubuntu/work/sentinelitad.com`.

## Durable workflow pattern

1. **Check before creating**
   - Search GitHub for likely names (`sentinel-itad-website`, `sentinelitad.com`, etc.).
   - Search local worktrees for existing Sentinel website material.
   - Reuse prior prototype/static assets if available, but reconcile against the current capability caveats in the canonical business repo.

2. **Keep public website separate from private operations**
   - Marketing site repo: `sentinelitad.com`.
   - Private operations, lead/contact nets, valuation scripts, compliance notes: `sentinel-it-asset-logistics`.
   - The website can link to public facts, but should not expose private lead research, operational scripts, `.env`, raw Drive exports, or internal contact databases.

3. **Use compliance-safe copy by default**
   - Do not claim Sentinel is R2v3, NAID, fully insured, or certified for data destruction until supporting evidence exists.
   - Current safe posture: secure local IT asset recovery, data-bearing media awareness, documented intake, value recovery where practical, and responsible downstream routing.
   - Stronger wording like “NIST 800-88 aligned” belongs only where an actual wipe/destruction process and evidence trail exist.

4. **Seed a useful static site, not just an empty repo**
   Minimum useful public repo contents:
   - `public/index.html` — landing page with trust-forward copy and lead capture.
   - `public/terms.html` — service notes and certification limits.
   - `public/privacy.html` — form/privacy baseline.
   - `public/thanks.html` — form completion page.
   - `public/robots.txt` and `public/sitemap.xml` — discovery plumbing.
   - `public/CNAME` — target custom domain marker.
   - `docs/website-brief.md`, `docs/content-checklist.md`, `docs/launch-backlog.md`, `docs/deployment-dns.md`, `docs/intake-questions.md`.

5. **Deploy and verify actual Pages output**
   - Add a GitHub Pages workflow using `actions/configure-pages`, `actions/upload-pages-artifact`, and `actions/deploy-pages` with `path: public`.
   - Push to the working branch and watch the workflow completion.
   - Smoke test deployed URLs (`/`, `/privacy.html`, `/robots.txt`, `/sitemap.xml`) with real HTTP 200 checks.
   - If a custom domain does not resolve, document DNS records instead of changing live DNS without approval.

## Ad-hoc verification pattern when no canonical suite exists

The system repeatedly requested fresh evidence because the repo has no canonical test/lint/build command. The durable fix is a focused temporary script under `/tmp` using `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`, then delete it.

Recommended checks for this class of static marketing repo:

- changed files exist and are non-empty
- HTML files parse with `html.parser.HTMLParser`
- `sitemap.xml` parses with `xml.etree.ElementTree`
- `robots.txt` points to sitemap
- `CNAME` contains the intended domain
- required trust/lead/compliance copy is present
- no merge markers or masked placeholders remain
- local `python3 -m http.server --directory public` smoke test returns 200 for changed public pages
- `git diff --check` passes
- working tree is clean after commit/push
- deployed Pages URLs return 200 after workflow completion

Report this as **ad-hoc verification**, not suite green.

## Pitfalls observed

- A first local server smoke test hit an unrelated process on the chosen port and returned WebSocket `426 Upgrade Required`. Retry on a different high port and bind `127.0.0.1`; the lesson is port hygiene, not that local serving is broken.
- GitHub Pages custom domain API may reject `cname` updates before DNS/certificate exists. Keep `public/CNAME`, document DNS, and wait for domain resolution before forcing settings.
- Search/hygiene checks for phrases like “Sentinel is R2v3 certified” must distinguish negated safe-copy rules from positive certification claims. Avoid over-broad false positives that fail on `Do not claim Sentinel is R2v3 certified`.

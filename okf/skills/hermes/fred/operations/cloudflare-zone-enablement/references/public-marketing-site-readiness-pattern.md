# Public Marketing Site Readiness Pattern (Small Static Site + Cloudflare Pages)

**Date:** 2026-07-27
**Verifying context:** Sentinel ITAD — `mbgulden/sentinelitad.com` (Astro static, deployed to CF Pages). Michael's actual request: *"I need to have my website actually be legit so I can share it with some IT professionals that do IT installs."*
**Skill scope:** the ordered checklist + reusable artifacts for getting a small public marketing site to the "shareable with IT pros" bar without overengineering.

## When to use this pattern

A small static marketing site (1–10 pages, one call-to-action form, no auth, no app logic) where the work is **not** building features but getting all the layers underneath one lead-capture button to actually work. Typical entrepreneur/sole-prop scenario: domain + Cloudflare Pages project already deployed, but the contact form silently drops submissions and the founder section is anonymous.

## The pattern, in order

### 1. Audit each layer before changing anything

| Layer | How to verify | What to record |
|---|---|---|
| Site serves | `curl -sS https://<domain>/` | HTTP status, size, presence of contact form |
| Contact form action | read HTML, note the `action="..."` URL | Identify the form backend (FormSubmit, Mailto:, custom Worker, etc.) |
| Form backend reachability | probe the action with a known test payload, capture response status | Whether submission would actually deliver |
| DNS + email deliverability | `dig @1.1.1.1 <domain> MX +short`, `TXT +short` | MX records exist? SPF in place? |
| Email Routing rule | list `/zones/:id/email/routing/rules` | Any forwarding rules active? Destination verified? |
| Founder / About section | grep for "founder", "about", operator name | Person or just brand? |
| Phone routing | ask the operator (don't call) | Forwarded to cell or voicemail? |
| GitHub webhook | check CF Pages deploy history, see if recent commits auto-deployed | Healthy or Dashboard-click-only? |

Save the audit as a single Markdown document under an `audit-YYYY-MM-DD/` folder in the repo. Use a checklist table at the top of the doc so future sessions can see at-a-glance what's broken vs. fixed.

### 2. Form action triage (the most common silent killer)

The contact form is usually the break point. Triage:

- **FormSubmit / Getform / Formspree** — these services require one-time email confirmation on the destination address before they'll deliver. Probe by POSTing a known payload; if you get back their marketing homepage, **the form backend is unactivated**. Either click the activation link in the destination inbox, or swap to a durable backend.
- **Mailto:** — opens the user's email client. No data leaves the browser unless the visitor actually hits send in their mail app. Test by clicking the link and verifying the mailto opens correctly. Many visitors won't follow through.
- **Custom Worker / endpoint** — verify the Worker resolves, handles POST, replies 303 redirect to /thanks, and forwards to a verified destination address.

### 3. DNS + Email Routing fix (most common: domain has no MX records)

When the contact email is at the custom domain (e.g., `team@sentinelitad.com`) and the DNS has no MX records, that address cannot receive mail — even the form backend can't deliver there. Fix:

- Cloudflare Email Routing has two halves: (a) MX records (`route{1,2,3}.mx.cloudflare.net` at priorities 10/20/30) + (b) an SPF TXT record (`v=spf1 include:_spf.mx.cloudflare.net ~all`) + (c) a routing rule mapping address → verified destination.
- The zone-level PATCH endpoint for enabling Email Routing is unreliable (returns `success: true` but does not flip `enabled`). Use the DNS records endpoint to create MX/SPF, then the routing rules endpoint for forwarding.
- Destination addresses must already be added + verified via `/accounts/:id/email/routing/addresses` before custom rules will create.
- Always verify externally with `dig @1.1.1.1 <domain> MX +short` after the mutation. Local API readback can race propagation.

See `cloudflare-zone-enablement` for the full Cloudflare Email Routing playbook.

### 4. Founder Note / About section (the trust-builder)

A faceless marketing site + a "Request a quote" button is a 30%-conversion-rate penalty vs. one with a named operator. If the site is owner-operator, **the founder section is more important than another landing page**.

Founder Note recipe:
- 50–100 words: name + years of experience + the operator's relationship to the work (not the company's positioning — the person's).
- 2–3 bullets of recent work or pickup areas (only true ones — never fabricate).
- A coverage area list (primary service area, secondary, long-distance).
- Style: matches existing site's section/eyebrow classes. 6–10 lines of CSS only.

Avoid: stock-founder photos, lists of certifications the founder doesn't actually hold, "passionate about" boilerplate.

### 5. Phone forwarding

Real-talk with the operator: does the public number ring their cell? In CA / Meridian-on-the-road scenarios, a Hawaiian-origin number is fine for branding, but **only if it forwards**. Otherwise every call goes to a voicemail box that nobody checks.

Cost-free options, ranked:
- **Forward from Hawaiian carrier to cell** (5 min, no external service)
- **Google Voice** (free, US number, but signup can friction in 2026 — have a fallback)
- **TextNow / Hushed** (free, monthly minute caps)
- **Replace public number with cell** (1 min, but exposes personal cell to web scrapers)

### 6. Commit, build, push — then expect CF Pages to deploy (or not)

- Always commit on a feature branch. Merge to production branch with `--no-ff`. Push both.
- Always run `npm run build` (or repo equivalent) + repo's canonical verifier script before pushing.
- After push, verify `git ls-remote origin <production-branch>` shows your new SHA.
- **CF Pages auto-deploy is best-effort.** See `cf-pages-deploy-diagnostic-when-webhook-dies.md` for the diagnostic flow when the live site doesn't update.

### 7. End-to-end smoke (the operator-only step)

For email forwarding: send a test from a non-Michael account to the public address, check the destination inbox. The VM usually can't SMTP outbound (port 25 blocked), so this check has to be Michael's.

For the contact form: open the live site in an incognito tab, submit a test, confirm the operator received it.

Do **not** claim the work is "done" until both smoke steps pass.

## Reusable artifacts (saved in `audit-YYYY-MM-DD/`)

- `README.md` — the audit + live evidence + decision points
- `founder-note-snippet.html` — drop-in HTML + minimal CSS with `[BRACKETED]` placeholders for Michael-supplied facts
- `cloudflare-worker-form.js` — durable replacement for FormSubmit.co (or any third-party form backend). Includes Turnstile spam protection, KV rate limiting, origin guard, structured email body, and the HTML form-update snippet.
- `phone-forwarding-checklist.md` — 3 options ranked by effort + carrier-specific steps
- `DEPLOY_NOW.md` — if commit lands but Pages doesn't deploy: step-by-step manual fallback

The `audit-YYYY-MM-DD/` folder should be **uncommitted** to the public repo — it's operator-facing planning/audit, not site content. When the audit is closed, archive or delete it.

## Pitfalls (specific to this pattern)

- **Don't claim "Done" without a self-test by the operator.** Email forwarding and form submission are the two layers where the only end-to-end check is a real human from a real network.
- **Don't fabricate operator details.** If you don't know the operator's name, ask. If they didn't supply years of experience, leave it out.
- **Don't try to coerce a too-narrow API token into creating Pages deployments.** The Dashboard UI is the universal fallback when the token can't.
- **Don't over-claim compliance.** "Trusted", "certified", "guaranteed" — if there's no documentation behind the claim, leave it out. Marketing copy that's honest converts better than copy that overpromises and burns trust.
- **Don't forget to verify the form after activation.** "I clicked the activation link" is not "the form works end-to-end." Run a self-test.

## Related references

- `cf-pages-deploy-diagnostic-when-webhook-dies.md` — what to do when `git push` succeeds but the live site doesn't change.
- `cloudflare-zone-enablement` (SKILL.md) — the canonical Cloudflare DNS + Email Routing playbook used in step 3.
- `cloudflare-zone-enablement-sentinelitad-2026-07-27.md` — the worked example for Sentinel ITAD.
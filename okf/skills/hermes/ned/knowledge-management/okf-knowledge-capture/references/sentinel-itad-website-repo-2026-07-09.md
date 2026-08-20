# Sentinel ITAD Website Repo Seeding — 2026-07-09

## Context

User asked to create a GitHub website repo for `sentinelitad.com` and start gathering the information needed for a superb trust-signal / lead-generation website.

Loaded skill: `okf-knowledge-capture`.

## Reusable pattern

1. **Source-map before creating website copy**
   - Check GitHub for an existing website repo first.
   - Check local workspaces for existing public site prototypes and canonical business docs.
   - For Sentinel, the canonical business repo remained `/home/ubuntu/work/sentinel-it-asset-logistics`; the website repo became a separate public marketing surface.

2. **Separate public site from private business ops**
   - Public repo: static marketing site, lead capture, launch checklist, website brief.
   - Canonical ops repo: operating docs, private lead/contact research, valuation scripts, compliance notes.
   - Link the public repo README back to the canonical ops repo rather than copying private/operational material wholesale.

3. **Compliance-safe website posture**
   - Use public copy like “secure local IT asset recovery,” “data-bearing media handling,” “documented intake,” and “responsible downstream routing.”
   - Avoid unsupported claims: R2v3/NAID certification, certified data destruction, insurance status, fully operational wiping tooling.
   - Put explicit caveats in README, website brief, checklist, terms page, and public page copy.

4. **Seed artifacts that reduce future ambiguity**
   - `README.md` with repo purpose, deployment target, and compliance wording rule.
   - `public/` static HTML/CSS site.
   - `public/CNAME` for the intended custom domain.
   - `docs/website-brief.md` with target audience, SEO terms, trust signals to collect, and capability caveat.
   - `docs/content-checklist.md` and `docs/launch-backlog.md`.
   - GitHub Pages workflow if no deployment path exists.

5. **Verification pattern for no-suite static/doc repos**
   - Create a temporary verifier with `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")`.
   - Verify artifact presence, HTML parsing, required public copy, compliance caveats, CNAME, local static HTTP serving, `git diff --check`, and clean git state.
   - Remove both the current verifier and any stale failed `/tmp/hermes-verify-*` file created during the attempt.
   - Report explicitly as **ad-hoc verification**, not suite green.

## Pitfall encountered

An over-broad negative certification check falsely flagged the phrase “Do not claim Sentinel is R2v3 certified” as a positive certification claim. Future verifiers should distinguish **negated safety rules** from **unqualified positive claims**. Check for exact unqualified phrases or parse surrounding context instead of naive substring bans.

## Useful verification checks from the session

- HTML parse with Python `html.parser.HTMLParser` for each public page.
- Required strings in `public/index.html`: brand, location, contact, lead CTA, data-bearing media wording, explicit no-overclaim language.
- Required strings in `public/terms.html`: R2v3/NAID non-claim, storage-media special handling, downstream partner routing caveat.
- `public/CNAME` equals `sentinelitad.com`.
- Local static server smoke test via `python3 -m http.server <port> --bind 127.0.0.1 --directory public` and HTTP 200 checks for `/`, `/terms.html`, `/thanks.html`, `/style.css`, `/CNAME`.
- `git diff --check` and clean `git status --short --branch`.

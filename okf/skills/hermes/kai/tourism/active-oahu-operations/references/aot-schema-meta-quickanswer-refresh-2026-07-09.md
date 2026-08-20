# AOT schema/meta/quick-answer refresh pattern (GRO-3652, 2026-07-09)

Use this when continuing the Compounding SEO Content Engine lane after guide/content refreshes. The class of work is: verify or add titles, meta descriptions, H1/H2 structure, quick-answer blocks, and JSON-LD schema on refreshed guide/rental pages, then ship through PR + Cloudflare Pages + production marker verification.

## Pages touched in the reference run

- Kailua Beach Park guide
- Lanikai Beach guide
- Snorkel gear rental page

## What worked

1. **Audit the refreshed pages structurally first**
   - Parse target HTML with BeautifulSoup.
   - Extract title, meta description, H1/H2/H3 outline, `.aot-quick-answer` count/text, and JSON-LD `@type`s.
   - Use this to decide whether the page needs copy edits, heading fixes, schema, or only verification.

2. **Keep structured data mirrored to on-page content**
   - For guide pages: add `Article` plus `FAQPage` when the page contains or is being given Q&A-style planning guidance.
   - For rental/product pages: preserve existing `Product` schema and add `FAQPage` when adding quick-answer / FAQ conversion support.
   - Do not introduce schema claims that are absent from visible page copy.

3. **Use quick-answer blocks as the GEO/conversion bridge**
   - Pattern: `<div class="aot-quick-answer" aria-label="..."><strong>Quick answer:</strong> ...</div>`
   - Place near the intro or primary commercial intent section.
   - Keep language operator-local, practical, and conservative around ocean conditions/safety.

4. **Fix heading semantics while staying scoped**
   - Align H1 with the refreshed title/search intent.
   - Promote article-section headings from visual H4/H5 to H2/H3 where they were being used as actual content sections.
   - Do not alter header/footer promo/phone H4s unless they are part of the article outline defect.

5. **Verification pattern**
   - Create `/tmp/hermes-verify-*` scripts via `write_file` or tempfile-safe creation.
   - Verify:
     - target HTML parses
     - exactly one H1 per target page
     - title exists and is not excessive
     - meta description is in a sane length window (roughly 120–170 chars unless the page intentionally needs otherwise)
     - expected quick-answer blocks exist
     - expected schema types exist and all JSON-LD parses
     - known old/bad heading markup is gone
     - `git diff --check` passes
   - After merge, repeat with production URLs and cache-busting query params after Cloudflare Pages confirms the main commit and exact URLs are purged.

## Gotchas from the run

- A first verifier failed because `git diff --check` caught `space before tab in indent` on replaced H1 lines. Treat `git diff --check` as mandatory even for content-only HTML changes.
- When replacing large WordPress/Kadence paragraphs, exact full-string replacements can fail because source copy differs subtly from prior assumptions. Use a narrowly scoped regex keyed to the unique block class/data attribute, then verify the rendered marker.
- Some pages already have only Organization schema from older exports. Adding Article/FAQPage as a separate marked block before `</head>` is safer than rewriting legacy schema.
- Keep “no price / booking target changes” explicit in PR body and Linear comment for SEO/content tasks that touch commercial pages.

## PR / Linear reporting checklist

- PR body should say “focused ad-hoc verification, not canonical suite green.”
- Include fact-check gates: no prices changed, no booking links changed, schema mirrors visible content, ocean/parking/safety copy is conservative.
- Linear close comment should include PR URL, production deploy commit, pre-PR verifier, PR checks, Cloudflare deploy confirmation, exact URL purge, and production verifier result.

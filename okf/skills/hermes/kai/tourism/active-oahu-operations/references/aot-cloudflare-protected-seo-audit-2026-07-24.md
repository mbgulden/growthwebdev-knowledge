# Cloudflare-Protected Live SEO Audit Pattern (2026-07-24)

## What happened

A live sitemap audit of `activeoahutours.com` received 50 initial `200` responses, then Cloudflare returned `429` challenge pages for the remaining 214 of 264 sitemap URLs. Browser automation showed “Performing security verification.” Subsequent Lighthouse runs for priority landing pages therefore audited the challenge page: apparent SEO failures (`is-crawlable`, meta description, HTTP status) were artifacts of the `429`, not evidence that the underlying pages lacked metadata or were non-indexable.

The homepage Lighthouse run completed before the block and was valid: Performance 94, Accessibility 95, Best Practices 81, SEO 100. GSC had current data through 2026-07-21, showing Google had crawled/served pages recently; that is useful counterevidence but does not replace Cloudflare verified-bot validation.

## Durable workflow

1. Start with low-volume health probes for apex, `www`, mirror, robots, and sitemap.
2. Crawl conservatively and record each response status, final URL, and timestamp. Do not classify a burst of challenge/429 responses as per-page defects.
3. On the first challenge response, stop the high-volume crawl. Save a **valid pre-block sample** separately from blocked rows.
4. For Lighthouse, inspect `finalUrl`, `http-status-code`, `is-crawlable`, page title, and response body before treating the category score as a page grade. A Cloudflare challenge invalidates content/SEO conclusions for that run.
5. Check Cloudflare Security Events / relevant WAF or rate-limit rules using the time window and Ray IDs. Verify Googlebot/Bingbot verified-bot treatment and that no intended user/QA traffic is unintentionally challenged. Do not weaken protection globally merely to make a crawler green.
6. Rerun only after an approved safe audit path exists (allowlisted audit IP, controlled low-rate window, or verified edge configuration), then report clean-crawl results separately.
7. Use GSC page/query data for own-site prioritization while live crawl is constrained. State query row-limit caps explicitly; GSC query exports can truncate at 5,000 rows.

## Reporting language

Say: “The later rows were Cloudflare challenge responses and are not evidence those pages are broken.”

Do not say: “The site is blocked from indexing” based only on Lighthouse auditing a challenge page. The honest claim is: “Verified-bot behavior requires an edge-event review and clean retest.”

## Related findings from this run

- Sitemap included final-route cleanup candidates: redirecting `.html`/legacy paths and an author archive redirect.
- GSC showed meaningful historical `www` page rows despite current apex resolution; verify single-hop deep-path redirects and page canonicals before attempting host cleanup.
- For Hawaiʻi place terms in demand, use correct visible forms such as `Mokoliʻi` and `Kāneʻohe` plus natural plain-form search bridges; preserve URL and brand identifiers.

# GSC Property Types — The `sc-domain:` vs `https://` Trap

## The Mistake (Cost 30 Minutes on 2026-06-19)

When you query the Google Search Console API for `activeoahutours.com` data, you MUST use the right property identifier. There are two types of properties and they hold different data.

### Type 1: URL Prefix Property
- **Format:** `https://example.com/` (with trailing slash)
- **Tracks:** A specific URL exactly as registered (protocol + hostname + path)
- **Verification method:** HTML file upload, HTML tag, or DNS TXT record
- **Data scope:** Only that exact URL/protocol
- **Example:** `https://activeoahu.com/` tracks ONLY the HTTPS variant of the WooCommerce shop

### Type 2: Domain Property (NEW, recommended)
- **Format:** `sc-domain:example.com` (with `sc-domain:` prefix, NO protocol, NO path)
- **Tracks:** ALL URLs across all subdomains, protocols, and paths
- **Verification method:** DNS TXT record only
- **Data scope:** DNS-level — covers http, https, www, non-www, all subdomains
- **Example:** `sc-domain:activeoahutours.com` tracks the entire marketing site

## Why the Trap Exists

A single Google account can have BOTH types registered for the same domain. The OAuth user (`mbgulden@gmail.com`) has:
- `https://activeoahu.com/` (URL Prefix, the WooCommerce shop) → returns product data
- `sc-domain:activeoahu.com` (Domain property) → returns marketing site data

If you query the wrong one, you get someone else's data (or the wrong site's data).

## The Symptom (How to Detect)

You pull "1,357 clicks" but every page in the result is `/product/water-bottle/` or `/product/alkaline-water/` — those are shop products, not your marketing site.

**Real example:** In the AOT SEO initiative, the first GSC pull was against `https://activeoahu.com/` (the shop), showing 47 clicks and weird product queries like "kirkland alkaline water." The CORRECT pull was `sc-domain:activeoahutours.com`, showing 1,357 clicks and proper SEO queries like "sharks cove snorkeling."

## Diagnose-and-Fix Sequence

### 1. List ALL properties on the OAuth account

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/webmasters/v3/sites"
```

Returns the full list. Look for:
- Format: `https://example.com/` → URL prefix property
- Format: `sc-domain:example.com` → Domain property
- Both can coexist for the same domain

### 2. Identify which property holds the data you want

For SEO analysis of a marketing site:
- ✅ Use `sc-domain:example.com` (catches all variants)
- ❌ Don't use `https://example.com/` (only HTTPS variant)

For checking a specific URL:
- Use the URL prefix property

### 3. URL-encode the value when passing in API calls

The `sc-domain:` prefix contains a colon which must be URL-encoded:

```python
from urllib.parse import quote

SITE = "sc-domain:activeoahutours.com"
url = f"https://www.googleapis.com/webmasters/v3/sites/{quote(SITE, safe='')}/searchAnalytics/query"
```

Without URL-encoding, the colon breaks the URL parsing and you get a 404.

### 4. Verify the data looks right

Spot-check a few queries:
- For a marketing site: should have brand + product/service queries
- For a shop: should have product + transactional queries
- For a blog: should have informational + question queries

If the query mix looks wrong (e.g., "kirkland water" on a tour site), you're looking at the wrong property.

## When to Use Which

| Scenario | Property type |
|---|---|
| Track www + non-www + subdomains | `sc-domain:example.com` |
| Track specific subdomain only | `https://sub.example.com/` |
| Track specific protocol (http-only) | `http://example.com/` |
| Track specific path (e.g., /blog) | `https://example.com/blog/` |
| Default for SEO work | `sc-domain:example.com` |

**Default to `sc-domain:` for SEO work.** It's the modern Google recommendation and most flexible.

## Common Mistake: GSC Sites.list Returns 9 Domains but You Only Have 1

If you have `https://activeoahu.com/` and `https://www.activeoahu.com/` as URL prefix properties, the GSC API returns BOTH separately. This can make it look like you have 9 properties when really you have 1 site tracked 3 different ways.

**Verify with a quick DNS lookup:**

```bash
dig activeoahutours.com NS +short
# Look for: gabriella.ns.cloudflare.com, brian.ns.cloudflare.com
# If those nameservers, the site is on Cloudflare

dig activeoahu.com NS +short
# Look for the same nameservers — if different, separate infrastructure
```

## When You're Working with Multiple Sites (Michael's Setup)

For each site, run the DNS lookup first to confirm ownership and infrastructure:

```bash
SITES="activeoahutours.com activeoahu.com growthwebdev.com"
for site in $SITES; do
  echo "=== $site ==="
  echo "Nameservers:"
  dig $site NS +short | head -2
  echo "A records:"
  dig $site A +short | head -3
  echo
done
```

Then map the DNS to the right Cloudflare account (see `cloudflare-api-auth-patterns` for the multi-account pattern).

## Reference Implementation

The AOT SEO initiative (June 19, 2026) pulled data for `sc-domain:activeoahutours.com` correctly the first time after the property-type distinction was identified. The 1,357-click baseline, 1,000-query inventory, and all subsequent GSC-driven analysis depends on this distinction.

## Related

- `google-api-setup` skill: GSC webmasters OAuth scope setup
- `cloudflare-api-auth-patterns` skill: multi-account Cloudflare pattern
- `okf-knowledge-ingestion` skill: ingesting research into OKF bundle

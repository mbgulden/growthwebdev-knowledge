# Internal Link Graph & Content Inventory Audit

## Purpose

Crawl a static HTML site to build a complete internal link graph, identify orphan pages (no inbound links), and catalog content quality issues (missing titles, descriptions, schema).

## Method

Use shell commands (grep, find, sed) — NOT Python. The static site has 200+ HTML files; a shell-based crawl is faster and more reliable.

### Step 1: Find all HTML files

```bash
find /site/path/ -name "*.html" -not -path "*/wp-content/*" -not -path "*/fonts/*" | sort
```

### Step 2: Extract per-page metadata

For each HTML file, extract:
- `<title>` tag content
- `<meta name="description">` presence and content
- `<h1>` tag presence and content
- Count of `<script type='application/ld+json'>` blocks (schema count)
- File size
- All `href=` values that point to other pages on the same site (internal links)

### Step 3: Build the link graph

1. For each page, record all outbound internal links
2. Invert the map: for each page, list all pages that link TO it
3. Pages with zero inbound links = **orphans**

### Step 4: Identify quality issues

| Issue | Command |
|-------|---------|
| Missing `<h1>` | `grep -L '<h1' *.html` |
| Missing meta description | `grep -L 'name="description"' *.html` |
| No schema | Pages with 0 `application/ld+json` blocks |
| Largest pages | Sort by file size, flag over 100KB |
| Duplicate titles | Group by title text, flag duplicates |

## Output Format

### Link Graph (JSON)

```json
{
  "page_path": "/activities/page-name/",
  "title": "Page Title",
  "file_size_kb": 45,
  "has_h1": true,
  "h1_content": "Primary Heading",
  "has_meta_description": true,
  "meta_description": "Description text",
  "jsonld_count": 2,
  "internal_links": ["/related-page/", "/another-page/"]
}
```

### Inventory Report (Markdown)

```
# Content Inventory Report

## Summary
- Total pages: 212
- Pages missing <h1>: 15
- Pages missing meta description: 104
- Orphan pages: 22
- Avg schema per page: 1.21
- Pages over 150KB: 20

## Orphan Pages
1. /page/path/ — zero inbound links
2. /page/path/ — zero inbound links

## Fix Recommendations
- Orphan pages: Add links from related content pages (contextual, not spam)
- Missing meta descriptions: Write unique 150-160 char descriptions
- Missing schema: Add relevant schema type per page topic
```

## Fixing Orphans

For each orphan page:
1. Understand the page's topic (read H1 + first paragraph)
2. Find 1-3 pages that SHOULD naturally link to it (pages on related topics)
3. Add contextual inline links — NOT footer/breadcrumb spam
4. Example: A Chinaman's Hat orphan → link from Kaneohe Sandbar page that mentions nearby locations

**Anchor text rule:** Use descriptive anchor text matching the orphan page's primary keyword. Never "click here" or "learn more".

## Real-World Stats (Active Oahu, June 2026)

- 22 orphans identified from 212 pages
- 12 source files modified to add links
- 21 English pages missing meta descriptions (83 Japanese pages also missing — separate pass)
- 37 pages with zero schema
- 2 files with leading-space filename artifacts (`.html` vs `index.html`)

## Files

- Full link graph: `cron/output/seo-audit/internal_link_graph.json`
- Inventory report: `cron/output/seo-audit/content_inventory_report.md`

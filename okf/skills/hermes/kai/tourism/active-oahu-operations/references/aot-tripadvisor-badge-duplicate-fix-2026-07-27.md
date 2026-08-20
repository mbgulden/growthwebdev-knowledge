# TripAdvisor Badge Duplicate Fix — 2026-07-27

## What happened

The HIGH-03 injection script (`fix_trust_signals.py`) ran multiple times across the same pages, causing:
- 2–3 badge copies stacked in `.social-links` on many pages
- An orphaned/fragmented badge between the `</div>` closing `.social-header` and the next `<section>`
- Count was still showing 356 instead of actual 440 reviews

## Key lesson

**Use idempotent guards.** Before injecting a badge, check if one already exists in the target context. The HIGH-03 script checked `tripadvisor-inline-badge` site-wide but did not check the specific `.social-links` context before each injection.

## The fix

### Design decision: badge BELOW the button

Michael preferred the badge positioned **below** the Book Online button in `.social-links` — one compact vertical unit rather than inline beside it. This saves horizontal space in the header row.

### Compact badge (55px star SVG, not 80px logo)

The original 80px wide TripAdvisor logo SVG was being squished. Replaced with a compact 5-star polygon SVG:

```html
<a href="https://www.tripadvisor.com/Attraction_Review-g60659-d5079465-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html"
   target="_blank" rel="noopener" class="tripadvisor-badge"
   style="display:block;text-align:center;margin-top:6px;"
   aria-label="See TripAdvisor reviews (4.8, 440 reviews)">
  <div class="tripadvisor-inline-badge" style="display:inline-flex;align-items:center;gap:4px;padding:2px 6px;font-size:11px;background:#f8f9fa;border:1px solid #e9ecef;border-radius:3px;">
    <svg viewBox="0 0 88 14" width="55" height="10" aria-hidden="true" style="vertical-align:middle">
      <polygon fill="#34E0A1" points="8,0 9.5,5 15,5 11,8 12.5,14 8,10.5 3.5,14 5,8 1,5 6.5,5"/>
      <polygon fill="#34E0A1" points="22,0 23.5,5 29,5 25,8 26.5,14 22,10.5 17.5,14 19,8 15,5 20.5,5"/>
      <polygon fill="#34E0A1" points="36,0 37.5,5 43,5 39,8 40.5,14 36,10.5 31.5,14 33,8 29,5 34.5,5"/>
      <polygon fill="#34E0A1" points="50,0 51.5,5 57,5 53,8 54.5,14 50,10.5 45.5,14 47,8 43,5 48.5,5"/>
      <polygon fill="#34E0A1" points="64,0 65.5,5 71,5 67,8 68.5,14 64,10.5 59.5,14 61,8 57,5 62.5,5"/>
      <polygon fill="#FFF" points="78,0 79.5,5 85,5 81,8 82.5,14 78,10.5 73.5,14 75,8 71,5 76.5,5"/>
    </svg>
    <span class="tripadvisor-badge-rating" style="font-weight:700;color:#34E0A1;font-size:12px;">4.8</span>
    <span class="tripadvisor-badge-reviews" style="color:#666;font-size:11px;"> · 440 reviews</span>
  </div>
</a>
```

### Clean `.social-links` structure (badge BELOW button)

```html
<div class="social-links"> 
<a href="https://fareharbor.com/embeds/book/activeoahutours/?u=f9b48d18-715e-4919-9c8e-077c045cf4bf&from-ssl=yes"
   class="pull-right btn btn-small btn-primary"
   onclick="FH.open({'shortname':'activeoahutours','fallback':'simple'}); return false;">
  <strong><span class="glyphicon glyphicon-calendar"></span> Book Online </strong>
</a>
<!-- Badge BELOW the button -->
<a href="https://www.tripadvisor.com/Attraction_Review-g60659-d5079465-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html"
   target="_blank" rel="noopener" class="tripadvisor-badge"
   style="display:block;text-align:center;margin-top:6px;"
   aria-label="See TripAdvisor reviews (4.8, 440 reviews)">
  ...compact badge...
</a>
</div>
```

## Duplicate detection pattern

To find duplicate badge anchors in `.social-links`:

```python
import re
with open('site/index.html') as f:
    c = f.read()

sl_start = c.find('<div class="social-links">')
sl_end = c.find('</div>', sl_start)
sl_block = c[sl_start:sl_end+6]
anchors = re.findall(r'<a[^>]*class="[^"]*tripadvisor-badge[^"]*"[^>]*href', sl_block)
# Should be 0 (badge goes BELOW social-links, not inside it)
print(f'Badges in .social-links: {len(anchors)}')
```

## Count verification

```bash
# Live site — total TripAdvisor anchors
curl -sS "https://activeoahutours.com/" -H "Cache-Control: no-cache" | \
  grep -o 'tripadvisor.com/Attraction_Review-g60659-d5079465' | wc -l

# origin/main (before CF Pages deploy lag)
git -C /home/ubuntu/work/active-oahu-tours-mirror show origin/main:site/index.html | \
  grep -c '440 reviews'

# Check for stale 356 count (should be 0)
git -C /home/ubuntu/work/active-oahu-tours-mirror show origin/main:site/index.html | \
  grep -c '356 reviews'
```

## Related PRs

- PR #107: Original HIGH-03 badge injection (162 badges, 356 count)
- PR #120: Compact badge design + 356→440 count fix
- PR #121: Badge BELOW Book Online button + duplicate removal in header

# AOT HIGH-01/HIGH-02: Schema openingHours + Alt Text — 2026-07-27

## HIGH-01: Schema.org openingHoursSpecification

### What
Added `openingHoursSpecification` to the TravelAgency JSON-LD schema in `site/index.html`, plus enhanced the Organization schema in `site/_templates/head.html` with `foundingDate`, `telephone`, and `address`.

### Files Changed
- `site/index.html` — TravelAgency schema block
- `site/_templates/head.html` — Organization schema block

### Business Hours (from `/contact-us/` page)
- Mon–Sat: 08:00–17:00
- Sunday: Closed

### PR
PR #105 — merged fast-forward to `origin/main`

### Verification
```bash
curl -sS https://activeoahutours.com/ | python3 -c "
import sys, re, json
c = sys.stdin.read()
schemas = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', c, re.DOTALL)
ta = next((d for d in [json.loads(s) for s in schemas] if d.get('@type') == 'TravelAgency'), None)
ohs = ta.get('openingHoursSpecification', [])
print(f'openingHoursSpecification entries: {len(ohs)}')
for oh in ohs:
    print(f'  {oh.get(\"dayOfWeek\")}: {oh.get(\"opens\")}-{oh.get(\"closes\")} {oh.get(\"description\",\"\")}')
"
# Expects: 7 entries, Mon-Sat 08:00-17:00, Sunday Closed
```

---

## HIGH-02: Descriptive Alt Text for Tour Images

### What
Replaced filename-style alt text with descriptive alt text on 88 HTML files.

### Changes
- `alt="kailua-lanikai-kayak-rental-mokes-oahu"` → `alt="Kayakers paddling toward the Mokulua Islands off Kailua Beach"` (88 files)
- `alt="mokolii-kayak-rentals-delivered"` → `alt="Mokoliʻi Island (Chinaman's Hat) viewed from Kailua kayak launch"` (2 files)

### Root Cause
These were inherited from the `body_bottom.html` template which had `alt` attributes set to URL/path-style kebab-case strings instead of describing what the image shows.

### Implementation
`/tmp/fix_alt_text.py` — regex replacement of `alt="..."` attribute values only (not URLs or other text):
```python
ALT_MAP = {
    'kailua-lanikai-kayak-rental-mokes-oahu': 'Kayakers paddling toward the Mokulua Islands off Kailua Beach',
    'mokolii-kayak-rentals-delivered': "Mokoliʻi Island (Chinaman's Hat) viewed from Kailua kayak launch",
}
```

### Scope
88 HTML files across EN and JA sites — all template-inherited via `body_bottom.html` and other shared templates.

### PR
PR #106 — merged fast-forward to `origin/main`

### Verification
```bash
# No filename alts on origin/main
git show origin/main:site/index.html | grep -c 'alt="kailua-lanikai-kayak-rental-mokes-oahu"'
# expect: 0

# Live site (may lag)
curl -sS https://activeoahutours.com/ | grep -c 'alt="kailua-lanikai-kayak-rental-mokes-oahu"'
# expect: 0
```

---

## Combined Sprint Results (July 27)

| # | Task | PR | origin/main | Live |
|---|------|-----|-------------|------|
| CRIT-01 | Booking calendar iframe | #104 | ✅ | ✅ |
| CRIT-02 | Booking CTA `target=_blank` | #104 | ✅ | ✅ |
| CRIT-03 | Heading H5→H3 hierarchy | #104 | ✅ | ✅ |
| HIGH-01 | Schema `openingHours` | #105 | ✅ | ✅ |
| HIGH-02 | Descriptive alt text (88 files) | #106 | ✅ | ✅ |
| HIGH-03 | TripAdvisor trust badge (162 pages) | #107 | ✅ | ⏳ CF cache |

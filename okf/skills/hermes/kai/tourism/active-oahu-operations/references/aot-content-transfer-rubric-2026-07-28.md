# AOT Content Transfer Rubric — Homepage Baseline
**Date:** 2026-07-28
**Session:** Phase 7 Astro homepage content transfer
**Status:** Baseline established; rubric pattern defined

## What happened

Built an Astro prototype with ~40% of real homepage content (7 images, 17 headings, 40 links).
Michael corrected: "ALL the photos and at least half the content is not on the home page."

Root cause: Did not extract and count actual content from the live source before building.
Assumed the prototype captured the essence without exact replication.

## Correct pattern (from now on)

### Step 1: Fetch real source HTML
```bash
curl -sS "https://activeoahutours.com/?cb=rubric" > /tmp/live_homepage.html
wc -c /tmp/live_homepage.html  # ~109KB for homepage
```

### Step 2: Count ALL element types in source
```python
import re
with open('/tmp/live_homepage.html') as f:
    html = f.read()

images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
headings = [(m.lastindex, re.sub(r'<[^>]+>','',m.group(0)).strip()[:80])
             for m in re.finditer(r'<h([1-6])[^>]*>(.*?)</h\1>', html, re.DOTALL)]
text_blocks = [re.sub(r'<[^>]+>','',m.group(0)).strip()
               for m in re.finditer(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
               if len(re.sub(r'<[^>]+>','',m.group(0)).strip()) > 30]
links = [m.group(1) for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
         if m.group(1) and not m.group(1).startswith('#')
         and len(re.sub(r'<[^>]+>','',m.group(0)).strip()) > 2]
print(f"Images:{len(images)}, Headings:{len(headings)}, Text:{len(text_blocks)}, Links:{len(links)}")
```

### Step 3: Document element counts BEFORE building
Put exact counts in the PR/Linear description before claiming done.

### Step 4: Deploy staging
- Copy real HTML to worktree site/ page
- Add `<meta name="robots" content="noindex,nofollow" />`
- Commit, push, wait for CF Pages deploy

### Step 5: Run exact element-level comparison
```python
import urllib.request, re
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")
live = fetch("https://activeoahutours.com/")
staging = fetch("https://<preview-url>/")

li = set(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', live))
si = set(re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', staging))
missing = li - si
extra = si - li
print(f"Images: {'OK' if not missing and not extra else 'MISMATCH'} | live={len(li)} staging={len(si)}")
if missing: print(f"  MISSING: {sorted(missing)}")
if extra: print(f"  EXTRA: {sorted(extra)}")
```

### Step 6: Report with exact counts
"✅ 22/22 images, ✅ 44/44 headings, ✅ 37/37 text blocks, ✅ 49/49 links — zero missing."

## Homepage baseline counts (2026-07-28)

Source: `https://activeoahutours.com/` — 109,417 bytes

| Element | Count |
|---------|-------|
| Images | 22 |
| Headings | 44 |
| Text blocks (>30 chars) | 37 |
| Links | 49 |
| JSON-LD blocks | 1 |
| kb-row-layout sections | 12 |

Key sections: Deal Banner, Header, Nav, Hero (h1+h2), E-Bike Kau Kau, Popoia, Mokulua Islands, Daily/Multi-Day rentals, Feature icons, Awards, Testimonials, Footer, 11 gallery thumbs.

CSS links: Kadence Blocks, `activeoahu/css/style.css?v=7` (NOTE: no hyphen — NOT `active-oahu`)

## CF Pages deploy monitoring

```python
import urllib.request, json, time
headers = {"X-Auth-Email": email, "X-Auth-Key": api_key}
# Poll GET /accounts/{id}/pages/projects/active-oahu-tours-mirror/deployments
# Wait for latest_stage.name == "deploy" and status == "success"
# Deploy time: 30-90s after push
```

## Additive-only rule

- Valid additive: staging has noindex meta the live doesn't have
- Invalid subtractive: staging is missing ANY element live has (even 1 image/heading)

Zero missing = done. Any missing = NOT done, fix first.

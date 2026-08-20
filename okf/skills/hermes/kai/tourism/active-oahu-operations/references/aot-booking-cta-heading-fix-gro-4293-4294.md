# AOT Booking CTA + Heading Hierarchy Fixes — GRO-4293/4294

## GRO-4293: Broken FareHarbor Booking CTAs

**Problem:** Booking links opened in new tabs instead of the FareHarbor lightframe overlay. Root cause: `target="_blank"` on FareHarbor links combined with JS that should call `FH.open()` + `return false`. When JS throws exceptions, `return false` never fires and the link falls through to `target="_blank"`.

**Scope:** 267 FareHarbor links across 33 tour pages.

**Fix:** Remove `target="_blank"` from FareHarbor links. The lightframe requires same-window navigation. Keep `target="_blank"` on social/newsletter links.

**Script:** HTMLParser-based replacement:
```python
import re
from pathlib import Path

def fix_booking_ctas(html_path):
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Remove target="_blank" from FareHarbor links only
    fixed = re.sub(
        r'(<a[^>]+href="https://fareharbor\.com/[^"]*"[^>]*)\s*target="_blank"',
        r'\1',
        content
    )
    # Also replace broken aot-lazy-fh-calendar divs with direct iframe
    fixed = re.sub(
        r'<div[^>]+class="aot-lazy-fh-calendar"[^>]+data-src="([^"]+)"[^>]*>.*?</div>',
        lambda m: f'<iframe src="{m.group(1)}" width="100%" height="700" frameborder="0" style="border: 0; max-width: 100%;" title="Booking Calendar" loading="lazy"></iframe>',
        fixed,
        flags=re.DOTALL
    )
    return fixed
```

**Verification:**
```bash
# No FareHarbor links with target="_blank"
grep -rn 'fareharbor.com' site/activities/ --include="*.html" | grep 'target="_blank"'  # expect 0
# Correct iframe count on rentals page (2)
grep -c 'fareharbor.com/embeds/calendar/' site/rentals/index.html  # expect 2
```

## GRO-4294: Heading Hierarchy H5→H3

**Problem:** Heading hierarchy skipped levels (H1→H5, H1→H4) throughout 134 pages, 898 tags total.

**Three distinct H5 cases — each handled differently:**

### Case 1: Plain H5 (no class, no Kadence)
Theme CSS: `h5{font-size:16px}`. H3 defaults to ~20px. When converting to H3, add explicit `style="font-size:16px"` to preserve visual appearance.

```python
# Add inline font-size to preserve 16px visual appearance
fixed = re.sub(r'<h5>', '<h3 style="font-size:16px">', content).replace('</h5>', '</h3>')
```

### Case 2: Class H5 (`.package-front-text`, `.package-margins`, `.section-title`)
CSS class controls margins/color, NOT font-size. Safe to H5→H3 with just the tag change.

```python
# Tag change only — class preserves styling
fixed = re.sub(r'<h5 ', '<h3 ', content).replace('</h5>', '</h3>')
```

### Case 3: Kadence H5 (has `data-kb-block="kb-adv-heading..."`)
Kadence block CSS controls font-size via the block ID in `style.css`. Inline styles are preserved. H5→H3 is safe without additional inline styles.

```python
# Tag change only — Kadence CSS controls size
fixed = re.sub(r'<h5 ', '<h3 ', content).replace('</h5>', '</h3>')
```

### Full H5→H3 fix script
```python
import re
from pathlib import Path

def fix_h5_to_h3(content):
    # Case 1: Plain H5 (no class, no data-kb-block) → add inline font-size:16px
    def plain_h5_to_h3(m):
        return f'<h3 style="font-size:16px"{m.group(1)}>'
    content = re.sub(r'<h5(?![^>]*class)(?![^>]*data-kb-block)([^>]*)>', plain_h5_to_h5, content)
    content = content.replace('</h5>', '</h3>')

    # Case 2 & 3: Class H5 and Kadence H5 → simple tag change
    content = re.sub(r'<h5 ', '<h3 ', content)
    content = content.replace('</h5>', '</h3>')
    return content
```

**Scope:** 898 H5 tags across 134 files. Net zero file size change (same number of characters in opening/closing tags).

**Verification:**
```bash
# Count H5 remaining (expect 0)
grep -rnc "<h5" site/ --include="*.html" | grep -v ":0$" | wc -l
# Count H3 headings
grep -rnc "<h3" site/ --include="*.html" | grep -v ":0$" | wc -l
# Check accessibility tree on preview
curl -sS "https://feature-gro-4025.active-oahu-tours-mirror.pages.dev/activities/chinamans-hat-self-guided-oahu-kayak-tour/" | \
  grep -oP '<h[1-6][^>]*>[^<]+</h[1-6]>'
```

## PR #104 Merge History

- **Branch:** `feature/gro-4025` → `main`
- **Squash merged** as single commit `98fcde55e`
- **Files changed:** 169 files, +1712/-1590 insertions
- **Conflicts resolved:** 6 files (always the same 6 — beach-gear-rentals, chinamans-hat, best-beaches-windward-oahu, kailua-beach-park, kaneohe-sandbar, kayak-safety-guide) — resolved with `--theirs` since feature branch had desired state
- **Cloudflare Pages preview:** `https://feature-gro-4025.active-oahu-tours-mirror.pages.dev/`
- **Production live check:** `curl -sS "https://activeoahutours.com/..." | grep -oP '<h[1-6][^>]*>[^<]+</h[1-6]>'`

## Key lesson: Mirror vs Live

The mirror repo (`active-oahu-tours-mirror`) has multiple out-of-sync branches. `origin/main` is what Cloudflare Pages deploys to `activeoahutours.com`. Always `git fetch origin` and compare live `curl` output to `origin/main`, not local files or local branches.

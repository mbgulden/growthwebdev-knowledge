# AOT Modular Adoption Recipes — Rounds 16-18 (2026-07-31)

> **Use this when:** continuing the modular primitives migration for the AOT homepage (the next task after Round 12/13 shipped the primitives), specifically when adopting `<Section>`, `<Card>`, `<Heading>`, `<PriceTag>`, or `<BookingButton>` into the remaining homepage components (Testimonial, FeatureBlock, FeaturedTourHero, FeaturedTours, BeachEquipment, MokuluaFeatureBlock, ClosingCTA, Awards, FooterExtras, DealBanner).
>
> **Important:** this is a follow-on to `references/aot-modular-primitives-design-system-2026-07-31.md` (Rounds 12/13). Read that first for the 3-layer architecture (tokens → primitives → adoption).

## The 6 new pitfalls caught in R16-R18 (in order of impact)

### Pitfall A — "Hero text is too big" trap: NEVER set `html { font-size: 62.5% }` globally

**The wrong fix** (tried first, rejected by Michael):

```css
/* tokens.css — DO NOT DO THIS */
html { font-size: 62.5%; }
```

This shrinks every `rem` on the entire site by 37.5% — every nav link, every paragraph, every testimonial, every card. It "fixes" the hero by breaking the rest of the page silently.

**Michael's actual response** (verbatim, 2026-07-31):

> "No, you made ALL the site text smaller in order to make the header text slightly smaller. Seriously? Please undo that universal change and update just the hero text size…"

**The correct fix** — scoped CSS with `[style*="font-size"]` attribute selector:

```css
/* active-oahu-tours-minimal.css — single rule, scoped to hero */
.hero-banner h2[style*="font-size"] { font-size: 60px !important; }
.hero-banner h1[style*="font-size"] { font-size: 20px !important; }
```

**Why this works:** the Heading primitive writes `style="font-size: 5rem"` as an inline attribute. Inline style beats Astro's scoped CSS because the child's `data-astro-cid-*` differs from the parent's. The `[style*="font-size"]` attribute selector scopes the override to children of `.hero-banner` that have an inline font-size — i.e. ONLY the hero's H1/H2, nothing else.

**Diagnostic ladder after applying:**
1. `getComputedStyle(document.documentElement).fontSize` → must be `16px` (unchanged)
2. `getComputedStyle(heroH2).fontSize` → must be `60px` (fixed)
3. `getComputedStyle(featureBlockH2).fontSize` → must match baseline (e.g. `22.4px`) — UNCHANGED
4. Repeat for `getComputedStyle(navLink).fontSize`, `getComputedStyle(tourPrice).fontSize` — all unchanged

### Pitfall B — Vite barrel-import resolution failure

**The wrong import** (tried first, build failed):

```ts
// In FeaturedTours.astro
import { Section, Heading } from "../primitives";
```

**Build error:**
```
Could not resolve "../primitives" from "src/components/homepage/Testimonial.astro"
```

**Why:** Vite/Rollup don't resolve `index.astro` for directory imports the way they do for `index.ts`/`index.js`. The `primitives/index.astro` file uses `export { default as X } from "./X.astro"` which is valid Astro syntax but Vite's resolver doesn't look for `index.astro` automatically.

**The correct fix** — direct file imports:

```ts
import Section from "../primitives/Section.astro";
import Heading from "../primitives/Heading.astro";
// one import per primitive, no barrel
```

**Verdict on the barrel file:** keep `primitives/index.astro` for documentation purposes (it shows the available primitives in one file) but DON'T use it as an import target. The barrel is a reference doc, not a module.

### Pitfall C — `<Heading>` primitive size map doesn't fit every component

Card.astro line 99 hardcodes `<Heading level={3} size="lg">` for the title (2rem = 32px). When adopting Card in FeaturedTours, the original h3 was `1.1rem` (17.6px) — Card forced it to 32px, which is the wrong visual size.

**The fix** (when Card/Heading is wrong size for a component): add a `titleSize` prop to the primitive instead of overriding with `!important` in the consumer:

```astro
// Card.astro
interface Props {
  // ...
  titleSize?: "sm" | "md" | "lg" | "xl" | "xxl" | "xxxl";
}

// In the template:
<Heading level={3} size={titleSize ?? "lg"} color="body">{title}</Heading>
```

Then the consumer passes `<Card titleSize="sm">` and gets the right size.

**Alternative when only one consumer needs a one-off size:** skip the primitive and use a plain `<h3>` with scoped CSS using design tokens. The primitives pattern is for shared layouts; one-off sizes don't need a primitive.

### Pitfall D — Orphan global CSS with `!important` keeps bleeding into the new component

When migrating a component out of the global stylesheet (`active-oahu-tours-minimal.css`), the orphan global block (usually with `!important` to win over Kadence previously) keeps applying to the new scoped CSS.

**Symptom:** the new component's scoped CSS looks correct in the source, but the rendered DOM still shows the old `!important` values (e.g. h3 = 25.6px when the new component says `1.2rem` / 19.2px).

**Diagnostic recipe:**

```bash
# 1. Confirm the new CSS rule is in the bundle
grep -oE '\.your-component[^{]*\{[^}]+font-size:[^}]+\}' dist/_aot_assets/*.css

# 2. Confirm the orphan CSS is ALSO in the bundle
grep -oE '\.your-component[^{]*\{[^}]+font-size:\s*1\.6rem\s*!important' dist/_aot_assets/*.css
```

If both are present, the orphan wins (because `!important` + later cascade source order). The fix is to delete the orphan block from the global stylesheet.

**Clean-up recipe:**

```bash
# Find the start and end of the orphan block
grep -n "^\.your-component" src/styles/active-oahu-tours-minimal.css
# Delete lines N through M
```

**Verifier pattern (catch this in CI):**

```python
# In your /tmp/hermes-verify-*.py script
check("No orphan CSS bleeding into new component",
      bool(re.search(r'\.your-component[^{]*\{[^}]+font-size:\s*1\.6rem\s*!important', css_text)),
      should_be=False)
```

### Pitfall E — `<Section>` primitive's `container` prop defaults to wrapping in max-width container

`<Section>` defaults to `container={true}`, which wraps children in `.aot-section__container` with `max-width: var(--aot-container-max)` (1100px).

**When to use `container={false}`:** when the original component was full-width (Kadence's `alignfull` class). Examples from R16:
- FeatureBlock: was `alignfull` → set `container={false}`
- FeaturedTours: was `alignfull` → set `container={false}`

**How to detect:** check the production HTML for `class="...alignfull..."` on the section's outer row. If present, the section should span full viewport width.

**The trap:** if you forget `container={false}`, the component shrinks to 1100px and the visual layout breaks (cards get cramped, background images clip).

### Pitfall F — BEM scoping with `__modifier` doesn't get pointer-events from scoped CSS

Inside a component, scoped CSS selectors must use the component's own `data-astro-cid-*` attribute to match nested elements. The extra `__modifier` (BEM-style) classes ARE applied to the HTML but the SCOPED CSS uses `[data-astro-cid-xxx]` selectors. Verify the BEM names match what the consumer expects.

**Verification:**

```bash
# Confirm the BEM class appears in both HTML and (scoped) CSS
grep -oE 'class="[^"]*your-component__cta[^"]*"' dist/index.html
grep -oE '\.your-component__cta\[data-astro-cid-[a-z0-9]+\]' dist/_aot_assets/*.css
```

## The 5 migration recipes (R16-R18 patterns that worked)

### Recipe 1 — Testimonial (simple, single-section)

```astro
---
import Section from "../primitives/Section.astro";

interface Props {
  quote: string;
  attribution?: string;
}

const { quote, attribution } = Astro.props;
---

<Section
  palette="gray"
  region="Customer testimonial"
  padding="md"
  class="testimonial-section"
>
  <blockquote class="testimonial-blockquote">
    <p class="testimonial-quote">"{quote}"</p>
    {attribution && <cite class="testimonial-cite">— {attribution}</cite>}
  </blockquote>
</Section>

<style>
  .testimonial-blockquote {
    margin: 0 auto;
    padding: 0 var(--aot-space-6);
    max-width: 800px;
    text-align: center;
  }
  .testimonial-quote {
    font-family: var(--aot-font-heading);
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--aot-gray-800);
    line-height: 1.4;
    margin: 0 0 0.75rem;
  }
  /* ... */
</style>
```

**Verdict:** worked first try. ~50 lines → ~30 lines.

### Recipe 2 — FeatureBlock (4-col grid with intro column)

```astro
<Section palette="white" region="Features" padding="lg" container={false} class="feature-block">
  <div class="feature-block__grid">
    <div class="feature-block__intro-col">
      <div class="feature-block__inner">
        <h2>{h2}</h2>  <!-- plain h2, not Heading primitive -->
        ...
      </div>
    </div>
    {features.map((feature) => (
      <div class="feature-block__card-col">
        ...
      </div>
    ))}
  </div>
</Section>

<style>
  .feature-block__grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;  /* 4-col on desktop */
    gap: var(--aot-space-4);
  }
  @media (max-width: 768px) {
    .feature-block__grid { grid-template-columns: 1fr; }  /* stack on mobile */
  }
</style>
```

**Verdict:** used plain `<h2>`/`<h3>` instead of Heading primitive because the production sizes (1.4rem / 1.1rem) don't fit the primitive's size map (sm/md/lg/xl/xxl/xxxl = 1/1.25/2/3/4/5 rem). Either add `xs`/`s` to the size map or use plain tags.

### Recipe 3 — FeaturedTourHero (3×, BEM scoping)

```astro
<div class="featured-tour-hero">
  <figure class="featured-tour-hero__figure">
    <img class="featured-tour-hero__image" ... />
  </figure>
  <div class="featured-tour-hero__content">
    <h3 class="featured-tour-hero__heading">{heading}</h3>
    <p class="featured-tour-hero__text">{text}</p>
    <a href={href} class="featured-tour-hero__cta">{cta}</a>
  </div>
</div>

<style>
  .featured-tour-hero {
    display: flex;
    gap: var(--aot-space-5);
    align-items: center;
    padding: var(--aot-space-5) 0;
    border-bottom: 1px solid var(--aot-gray-200);
  }
  /* ... */
</style>
```

**Verdict:** BEM-style scoping with tokens. Required also deleting 70 lines of orphan global CSS to prevent `!important` bleed.

### Recipe 4 — FeaturedTours (3-card grid using Card primitive)

```astro
<Section palette="white" region="Most Popular Experiences" padding="lg" container={false} class="popular-tours">
  <div class="popular-tours__container">
    <h2 class="popular-tours__h2">{h2}</h2>
    <div class="tours-grid">
      {tours.map((tour) => (
        <Card
          href={tour.href}
          image={tour.image}
          imageAlt={tour.imageAlt}
          title={tour.heading}
          subtitle={tour.subheading}
          description={tour.text}
          duration={tour.duration}
          location={tour.location}
          price={tour.price}
          ctaText={`${tour.cta} ➔`}
          bookHref={tour.bookingHref}
          variant="tour"
          class="tour-card"
        >
          {tour.note && <p class="tour-note">{tour.note}</p>}
        </Card>
      ))}
    </div>
  </div>
</Section>
```

**Verdict:** 166 lines → 102 lines (-38%). Card primitive handles image, h3, description, duration, location, price, cta, book button. Consumer only adds the section h2, view-all link, and the optional note via slot.

**Known limitation:** Card primitive hardcodes `<Heading size="lg">` for the title h3, which is 32px (2rem). For FeaturedTours' desired 17.6px (1.1rem), need to add `titleSize` prop (Pitfall C).

### Recipe 5 — Verification script shape

```python
#!/usr/bin/env python3
"""
Round N verification: <module> migration to primitives.
Scope: <what was migrated>
"""
import urllib.request, hashlib, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PREVIEW = "https://content-astro-homepage.active-oahu-tours-mirror.pages.dev"
LOCAL = "/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro/dist"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

def fetch(url): return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), context=ctx, timeout=15).read().decode("utf-8", errors="replace")
def fetch_bytes(url): return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), context=ctx, timeout=15).read()
def sha256(data): return hashlib.sha256(data).hexdigest()

results = []
def check(name, ok, detail=""):
    results.append({"name": name, "ok": ok, "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")

# 1. Hash match
local_html = open(f"{LOCAL}/index.html", "rb").read()
live_html = fetch_bytes(f"{PREVIEW}/")
check("Local matches live", sha256(local_html) == sha256(live_html), f"local={sha256(local_html)[:16]} live={sha256(live_html)[:16]}")

html_text = live_html.decode("utf-8", errors="replace")
m = re.search(r'href="(/_aot_assets/[^"]+\.css)"', html_text)
css_text = fetch(f"{PREVIEW}{m.group(1)}")

# 2. Module-specific checks (classes, sizes, colors)
# 3. Regression checks (Hero h2 still 60px, no orphan CSS)
# 4. Bundle sanity

# Summary
passed = sum(1 for r in results if r["ok"])
print(f"\nPassed: {passed}/{len(results)}")
exit(0 if passed == len(results) else 1)
```

**Why this script shape:** catches both the new module's classes AND the regression of previous modules (especially the Hero h2 isolation fix from R15). A failure in any check blocks the "done" claim.

## File-impact summary (R16-R18)

| Module | Before | After | Line delta | New primitives used |
|---|---|---|---|---|
| Testimonial.astro | 51 | 36 | -29% | `Section` |
| FeatureBlock.astro | 130 | 122 | -6% | `Section` (+ plain h2/h3) |
| FeaturedTourHero.astro | 83 | 110 | +33% | (BEM + tokens only) |
| FeaturedTours.astro | 166 | 102 | -38% | `Section`, `Card`, `BookingButton` (via Card) |
| active-oahu-tours-minimal.css | 1108 | 1038 | -6% | removed 70 lines of orphan CSS |

**Net:** -3 lines across components, but the code is now actually modular (uses Section/Card/Heading primitives) instead of hand-rolled. The FeaturedTourHero line increase is bogus — the same code, just formatted with BEM conventions and design tokens instead of one big style block.

## Browser verification recipe (the visual check)

After every modular migration commit, run from `browser_console`:

```javascript
(function(){
  var heroH2 = document.querySelector('.aot-hero-section h2');
  var moduleEl = document.querySelector('.your-module-class');
  var moduleH = moduleEl ? moduleEl.querySelector('h2, h3') : null;
  var moduleCS = moduleH ? getComputedStyle(moduleH) : null;
  return {
    // Hero h2 must stay 60px (R15 isolation fix)
    heroH2FontSize: heroH2 ? getComputedStyle(heroH2).fontSize : 'none',
    
    // Module-specific checks
    moduleHFontSize: moduleCS ? moduleCS.fontSize : 'none',
    moduleHColor: moduleCS ? moduleCS.color : 'none',
    
    // Global html font-size must NOT have changed (R15 isolation)
    htmlFontSize: getComputedStyle(document.documentElement).fontSize,
  };
})()
```

**Gold values to confirm:**
- `htmlFontSize: "16px"` — global root NOT changed
- `heroH2FontSize: "60px"` — hero h2 fix intact
- Module-specific values match production (e.g., FeatureBlock h2 = "22.4px", Testimonial quote = "20.8px")

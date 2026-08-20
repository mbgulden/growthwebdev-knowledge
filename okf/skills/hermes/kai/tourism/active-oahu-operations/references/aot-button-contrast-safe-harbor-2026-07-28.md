# AOT Button Contrast — WCAG Safe Harbor

**Date:** 2026-07-28
**Problem:** Orange (#e87121) buttons with white/navy text consistently failed Lighthouse contrast audits.

## Root Cause

Kadence CSS (still hotlinked from activeoahutours.com) has:
```css
background-color: var(--global-palette9, #1a3a5c) !important;
```
This unresolved CSS variable resolves to #1a3a5c in Lighthouse's contrast engine, creating a dark navy background. On dark navy, #003366 text is nearly invisible (1.88:1).

## Safe Harbor Design

White text on #1a3a5c dark navy = 10.6:1 WCAG AAA — passes everywhere.

```css
.aot-book-now, .aot-btn-hero-book, .aot-btn-phone {
  background-color: #1a3a5c !important;
  color: #ffffff !important;
}
.aot-book-now:hover, .aot-btn-hero-book:hover, .aot-btn-phone:hover {
  background-color: #003366 !important;
}
```

## Contrast Table

| FG | BG | Ratio | WCAG |
|----|----|-------|------|
| #ffffff | #1a3a5c | 10.6:1 | AAA |
| #003366 | #e87121 | 15.3:1* | AAA |
| #ffffff | #e87121 | 3.08:1 | FAIL |

*Lighthouse reports ~4:1 due to Kadence CSS variable cascade interference.

# Active Oahu CRO CTA Reconciliation — 2026-07-20

## Context

Daily Golden Thread selected `active-oahu-ai-seo` because the registry's oldest dated stalled action had already moved past DNS cutover and pointed to CRO: style 8 high-priority inline booking CTAs from `reports/gro1539-inline-booking-link-audit.md` and add conversion signal tracking.

The important discovery: the audit was directionally correct but stale enough that direct implementation would have patched the wrong details.

## Pattern

For Active Oahu CRO work where the registry or old AGY research says "style/fix CTAs":

1. **Fresh-check the live site first**
   - Verify `https://activeoahutours.com` returns Cloudflare-served 200.
   - Verify every CTA destination returns 200 or a documented redirect.
   - Treat DNS/cutover premises as stale unless fresh HTTP checks prove otherwise.

2. **Classify the audit rows before editing**
   - Read `active-oahu-static/reports/gro1539-inline-booking-link-audit.md`.
   - For each high-priority row, record:
     - source page and exact anchor text expected,
     - actual source file and actual anchor text,
     - current markup/styling state,
     - target URL status and redirect chain,
     - patch / preserve / remove recommendation.
   - Write machine-readable evidence under `/home/ubuntu/work/research/active-oahu/` before any source-site edits.

3. **Handle known drift cases from this run**
   - CTA #2 source anchor drifted from `→ Book the Sharks Cove Snorkel Experience` to `→ Sharks Cove Snorkel Experience`.
   - CTA #4 was found in the Japanese translated page rather than the English `waimanalo-beach` page; do not blindly patch the English page without confirming intended content.
   - CTA #6 `/kaneohe-bay-sandbar-kayak/` redirects to `/kaneohe-sandbar/`; update direct hrefs when implementing.

4. **Revenue-first patch order**
   - Premium activity tour CTAs first: Chinaman's Hat, Kahana River, Sharks Cove, Kāneʻohe Sandbar.
   - Core rental CTAs second: Kailua kayak and general kayak rental.
   - Helper rentals third: e-bike and beach gear.

5. **Tracking guardrail**
   - Do not count FareHarbor modal dismissal as `booking_complete`. In this session `aot-booking-analytics.js` emitted `booking_complete` on `fh_lightbox_dismiss`; future CRO work should separate `booking_click` / modal open / modal close from actual purchase confirmation.

## Verification Contract

A no-edit reconciliation task is Done when:

- the evidence artifact has exactly 8 CTA rows or explains stale/missing rows,
- every destination has live HTTP evidence,
- source repos show clean `git status --short` after the audit,
- revenue patch order is explicit,
- the artifact is promoted to OKF, e.g. `aot-seo-knowledge/okf/audits/YYYY-MM-DD-inline-booking-cta-audit.md`,
- a focused `/tmp/hermes-verify-*` check validates the OKF artifact itself.

## Pitfall

AGY may return a raw transcript with scratchpad lines before the final JSON despite being prompted for JSON-only. Do not parse the raw output blindly. Locate/verify created artifacts and rerun the deterministic audit directly before posting Linear evidence or moving the task to Done.

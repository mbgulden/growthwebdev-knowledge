# HD Education Checkout-First Validation Pattern — 2026-07-13

## Context

Daily Golden Thread selected HD Education because the registry had an undated/stale `next_action` while Linear showed active non-done HD Education issues. Registry still referenced the canceled GRO-202 8-module foundation course path, but current repo artifacts already had an HD Academy MVP catalog and landing/API surfaces.

## Durable lessons

1. **Reconcile stale registry course assumptions against live Linear and repo catalog first.**
   - Registry said: create an 8-module Gumroad course.
   - Live Linear said: advanced practitioner tasks were In Progress, while foundation/LMS/checkout tasks were Backlog.
   - Repo catalog said: `hd-fundamentals` is a 4-week/4-module `$97` launch-ready outline and explicitly gates next-course production on `100 paid students before producing the next course`.

2. **Do not reuse existing payment links unless they match the offer.**
   - Existing Stripe links in `payment-links.txt` were report products, not HD Academy course products.
   - Correct execution was to create a $97 validation CTA in blocker/waitlist mode rather than mis-selling report checkout links as course checkout.

3. **Winning strategy for early education-product validation:**
   - Add a visible `$97 HD Fundamentals` payment-intent / pre-order validation path.
   - Explicitly show a live-checkout blocker when no real course Stripe/Gumroad URL exists.
   - Gate Advanced Practitioner work until 100 paid foundation students are evidenced.
   - Defer LMS and post-purchase automation until buyer intent exists.

4. **AGY execution timeout recovery:**
   - If AGY edits but times out before final evidence, inspect the changed paths, run bounded direct verification, and post the rubric evidence yourself.
   - Do not claim AGY passed from narrative output alone.

5. **Verification artifacts used:**
   - Static Python test for landing/catalog markers.
   - Playwright flow for `/academy/` CTA → modal → blocker copy → waitlist-mode submit.
   - `npm run build` for Astro build/postbuild.
   - Focused `/tmp/hermes-verify-*` script for OKF/registry/research-input artifacts after post-turn verification nudges.

## Suggested task framing

Top task: `Add $97 Academy pre-order checkout gate to landing page`

Rubric:
- Unit: static/build test proves CTA exists, says `$97 HD Fundamentals`, and advanced-course CTA is not primary.
- Integration: browser/link check proves the CTA route/modal resolves and documents the exact checkout blocker if no live URL exists.
- Revenue: visible payment-intent path exists, or a blocker artifact is ready for Michael/Fred to add the real checkout URL.
- Assumption: validates checkout-first demand before producing course assets or building LMS.

Exit criterion: Academy landing exposes one clear `$97 HD Fundamentals` validation CTA with measurable hooks; live checkout works or the only remaining blocker is the missing real course checkout URL, documented with evidence.

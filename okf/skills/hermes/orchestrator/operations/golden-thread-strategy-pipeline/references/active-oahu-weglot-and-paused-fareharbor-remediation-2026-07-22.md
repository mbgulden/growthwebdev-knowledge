# Active Oahu Weglot Removal + Paused FareHarbor Remediation (2026-07-22)

## Context

AGY Golden Thread Project Review surfaced two Active Oahu Website Overhaul remediation rows:

- Verify FareHarbor item IDs and implement homepage booking product grid.
- Confirm/externalize a hardcoded Weglot key.

Michael corrected the remediation contract:

- Active Oahu no longer uses Weglot.
- Weglot remediation should remove legacy Weglot markup/scripts/styles/API initializer blocks, not configure or externalize a key.
- FareHarbor item-ID/product-grid remediation under `active-oahu-website-overhaul` is paused unless Michael explicitly reopens it.

## Pattern

When converting AGY Golden Thread rows into remediation work:

1. Treat AGY rows as stale hints, not authoritative tasks.
2. Apply current operator overrides before creating Linear issues or emitting future cron rows.
3. For Weglot on Active Oahu:
   - Create removal work only.
   - Preserve static English/Japanese navigation and booking CTAs.
   - Do not reintroduce Weglot, externalize Weglot keys, or build new Weglot config.
4. For the paused FareHarbor/product-grid row:
   - Do not create or route fresh item-ID/product-grid work.
   - Update registry/digest sources so the stale row stops reappearing.
5. If editing the cron sanitizer, verify with a fresh `/tmp/hermes-verify-*` tempfile script that checks:
   - `py_compile` passes.
   - Module imports without running `main`.
   - FareHarbor/product-grid rows are suppressed.
   - Weglot rows are rewritten to removal.
   - Unrelated rows, such as HD Talent Hiring remediation, are preserved.

## Verification lesson

If the first tempfile verifier has a syntax/quoting error, do not stop at the failed proof. Create a fresh OS-safe `hermes-verify-*.py`, avoid nested triple-quote/newline interpolation traps by building sample Markdown with `"\n".join([...])`, run it, clean it up, and report the successful run explicitly as ad-hoc targeted verification, not suite green.

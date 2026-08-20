# Dashboard production hardening and real-record proof

Session-derived checklist for Prismatic dashboard hardening slices where the task includes production-safe assets, real governance records, branch protection, and rendered proof.

## Branch protection gate

- Treat provider-side branch protection as its own gate, separate from local tests and PR merge proof.
- Read back the protected branch rule after mutation and record: strict up-to-date state, exact required check contexts, stale-review dismissal, conversation-resolution setting, force-push/deletion restrictions, and admin enforcement boundary.
- Preserve solo/operator usability unless Michael explicitly asks for reviewer/CODEOWNERS hardening; do not silently require outside reviews.

## Tailwind/static dashboard asset gate

- Replace browser-time Tailwind CDN with pinned, reproducible build tooling and a committed/generated static CSS asset.
- Preserve the canonical dashboard shell; do not replace it with a mini dashboard to make asset proof easier.
- Verify all layers:
  1. source HTML references `/static/dashboard.css` and has no CDN reference;
  2. deterministic source-to-template build/check passes;
  3. route returns CSS with expected cache headers;
  4. generated CSS contains required utility output;
  5. wheel/package install in a clean external venv still serves the packaged CSS;
  6. alternate-port runtime proof confirms HTTP 200 for root and CSS before production cutover.
- Beware local package-name shadowing when using Python build frontends from inside the repo; use an isolated wheel command or run from outside the source root if necessary.

## Real governance-record materialization

- If dashboard cards stay `CHECKING`, distinguish a broken adapter from an empty production ledger. Inspect the API/card contract before inventing fallback/sample data.
- Seed only exact-artifact-bound real records, and snapshot affected production ledgers first.
- Build disposable fixtures under the effective production/operator `HOME`. Completed-work packets with `source_path` outside `Path.home()` can classify as `manual_review_scope` even when proof files exist.
- Require the full dry-run governance chain to materialize while real side-effect flags remain false: no Linear comment, no branch, no PR creation, no auto-merge, no deployment, no bulk dispatch, no real executor arm.
- Save the record receipt with ID, source commit, classification, chain count, side-effect booleans, and digest.

## Rendered desktop/mobile proof gate

- Static CSS/source checks are not enough for dashboard hardening. Run rendered browser proof at desktop and mobile widths before deployment.
- Prove both content state and geometry:
  - all expected badges leave `CHECKING`;
  - exact real record appears;
  - document `scrollWidth` does not exceed viewport width unless the task explicitly allows scoped horizontal scroll;
  - no Tailwind CDN network request/warning;
  - no page errors;
  - screenshots/geometry JSON are saved for handoff.
- If Playwright selectors time out, first verify selector names against product IDs before calling the UI broken. A wrong harness ID is a verifier bug, not product failure.
- If rendered proof finds overflow, keep the deployment blocked and create a focused follow-up PR. Common fixes: add `min-w-0` at grid/flex boundaries, force long live config strings to wrap/break, and keep wide tables inside bounded `max-w-full overflow-x-auto` containers.

## Deployment boundary

- Do not deploy a static-asset release merely because source/package/HTTP proof passed if rendered desktop/mobile proof finds layout overflow.
- Keep the live gateway on the previous verified release until the overflow repair has browser proof, focused/canonical tests, PR CI, immutable release, alternate-port proof, and explicit authorized cutover.

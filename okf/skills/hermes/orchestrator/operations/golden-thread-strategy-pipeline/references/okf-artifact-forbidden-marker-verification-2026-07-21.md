# OKF Artifact Forbidden-Marker Verification Loop — 2026-07-21

## Context

During a Golden Thread run for HD Enterprise, the durable OKF artifact itself documented the runtime verifier command that scanned a sales kit for forbidden claims. The artifact's code block included the exact forbidden phrases. A post-turn verification nudge then correctly treated those literal phrases inside the OKF artifact as changed-path violations, even though they appeared only inside the verifier snippet.

## Durable Pattern

When an OKF/report artifact must prove that another file no longer contains forbidden phrases, do **not** print the exact forbidden phrases in the artifact's prose or code block if the artifact verifier also checks for their absence.

Use one of these instead:

1. **Category labels in the artifact**
   - `unsupported full compliance phrasing`
   - `unverified customer velocity proof`
   - `refund guarantee phrasing`

2. **External evidence path**
   - Link to the raw execution/verifier output that contains the exact scan, but keep the OKF artifact free of the literal markers.

3. **Runtime-only construction**
   - If a future verifier must include exact strings, construct them inside the temp verifier without writing them into the durable artifact. For example, concatenate parts or keep the exact strings only in `/tmp/hermes-verify-*`, which is removed after the run.

## Focused Verification Shape

For repeated changed-path nudges on an OKF artifact:

- Create a temp verifier via `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
- Check the OKF artifact's contract directly:
  - required sections
  - selected project
  - research/evidence paths
  - Linear IDs
  - rubric PASS markers
  - guardrails
  - no placeholders or forbidden literal markers
- Run it.
- Remove the temp verifier.
- Reply with compact machine-legible proof:
  - `AD_HOC_VERIFICATION=PASS`
  - `VERIFICATION_TYPE=ad-hoc targeted verification, not suite green`
  - `CHANGED_PATHS_CHECKED=...`
  - `CLEANUP=PASS ...`

## Pitfall

Do not make the OKF artifact fail its own no-forbidden-marker check by embedding the exact terms in an example scan list. The artifact can say what categories were checked; the exact strings belong in transient verifier output or raw evidence, not durable prose when those strings are policy-sensitive.
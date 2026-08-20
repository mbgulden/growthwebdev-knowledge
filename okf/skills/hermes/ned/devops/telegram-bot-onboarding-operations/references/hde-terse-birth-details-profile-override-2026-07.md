# HDE terse birth details + expert profile override pitfall — 2026-07

## Trigger
A tester provides complete birth data in compact family-test form, e.g.:

```text
August 2 1952 6:46pm Glendale California
```

The guide may answer with a plausible chart read but generate no PDF/image if the deterministic chart rail only recognizes location after `in`, `birth place`, or similar phrases.

## Root cause pattern
- Date and clock parse successfully.
- Birth place is trailing text after the clock, not introduced by `in` or `birth place`.
- `extract_full_birth_details()` / partial slot extraction returns incomplete details.
- The turn falls through to LLM-only response.
- Later `pdf report` cannot recover a stored profile/chart and may falsely blame report-server auth/licensing.

## Durable fix shape
1. In both full-detail and partial-slot extractors, after parsing date/time, treat trailing words after the clock as the birth place when no explicit location was found.
2. Route complete one-shot birth details through deterministic chart generation before LLM fallback.
3. Persist profile, chart JSON, coach manifest, bodygraph PNG, and PDF.
4. If a human/expert correction says the calculated profile is wrong, store it as a per-person `chart_overrides` entry and regenerate so JSON/PDF/manifest agree.

Example override:

```json
{
  "chart_overrides": {
    "profile": "3/5"
  }
}
```

## Verification recipe
Use a fresh `/tmp/hermes-verify-*` ad-hoc verifier that checks:
- changed guest template compiles;
- live guest runtime and host template match the repo template;
- running container contains the trailing-place parser;
- profile override is present;
- `chart_data.json`, `coach_manifest.json`, and extracted PDF text all show the corrected profile;
- PDF/PNG are valid file types and non-trivial sizes;
- changed files do not contain secret-shaped strings.

Report as focused ad-hoc verification, not suite green.

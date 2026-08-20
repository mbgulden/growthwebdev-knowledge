# HDE Real Calculation Discipline — 2026-07-17

## Trigger

Michael corrected the agent after Ruth Gulden's chart was forced from `3/6` to `3/5` with a per-person override: “We aren’t creating exceptions to the rules, we are using the real human design API calculations. No exception rules. Please look at the calculations.”

## Durable lesson

For HDE chart/profile correctness, **never satisfy an expected profile by adding a customer-specific override**. Human Design mechanics must come from the real calculation engine/API. If the result is wrong, debug the inputs and calculation path:

1. Birth date/time including AM/PM.
2. Birth place parsing and geocoding.
3. Timezone and DST conversion.
4. Whether the engine is falling back to UTC/0,0.
5. Personality Sun line and Design Sun line from the returned planet maps.
6. Whether PDF/report generation is applying any caller-provided `chart_overrides`.

## Ruth-specific finding

Ruth was initially handled as `August 2 1952 6:46pm Glendale California`, but the reference image Michael later supplied said `August 2nd, 1954 - 06:46 PM`, `Birth Date (UTC) August 3rd, 1954 - 01:46 AM`, `Glendale, California, United States`, `America/Los_Angeles`.

Real calculation outcomes observed:

| Input | Result |
|---|---:|
| 1952-08-02 18:46 with unresolved Glendale → UTC fallback | `3/6` |
| 1952-08-02 18:46 Glendale California resolved to America/Los_Angeles | `4/6` |
| 1952-08-02 06:46 Glendale California resolved to America/Los_Angeles | `3/5` |
| 1954-08-02 18:46 Glendale California resolved to America/Los_Angeles | `3/5` |

So `3/6` was wrong because Glendale was unresolved and the engine used UTC fallback. The later `4/6` was a real-engine result for the wrong year (`1952`). The source chart’s `3/5` was explained by the corrected year (`1954`) with the same PM time. If a tester expects a specific profile, confirm the source year/date/AM-PM/location/timezone field-by-field before regenerating/sending a corrected report.

## Required repair pattern

- Add/repair geocoder aliases or external geocode path so the birthplace resolves.
- Ensure `local_to_utc()` receives resolved coordinates/timezone, not just the original unresolved location string.
- Remove per-person `chart_overrides` from active profiles and quarantine artifacts generated from overrides.
- Prevent the reports server from accepting caller-provided `chart_overrides` for natal mechanics.
- Regenerate only after real inputs produce the expected result.

## Verification pattern

Use real `pytest` where available, plus a focused `/tmp/hermes-verify-*` script when the repo has no discoverable tests or the test suite has unrelated failures. Verification should prove:

- Engine resolves the birthplace to the expected timezone.
- The real engine returns the expected profile from Personality Sun line / Design Sun line.
- The old fallback result is distinguishable.
- Guest runtime does not load or send `chart_overrides`.
- Reports server ignores any incoming `chart_overrides` metadata.
- Active customer artifacts do not point to override-generated reports.

Label focused scripts as ad-hoc verification, not suite green.

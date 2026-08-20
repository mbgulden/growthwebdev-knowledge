# HDE chart discrepancy: verify source birth data before overrides

## Trigger

Use this reference when Michael/domain expert says an HDE-generated chart field is wrong, especially Profile/line, and supplies a screenshot or reference chart.

## Session lesson

Ruth’s chart appeared to prove the bot should output `3/5`. The first repair path incorrectly forced a per-person `chart_overrides` value. That masked the real issue and created split-brain artifacts.

The source screenshot later showed the actual reference data was:

```text
Birth Date (Local): August 2nd, 1954 - 06:46 PM
Birth Date (UTC):   August 3rd, 1954 - 01:46 AM
Location:           Glendale, California, United States
Time Zone:          America/Los_Angeles
```

Earlier bot runs had used **1952**, not 1954. That year mismatch explained the profile discrepancy.

## Verified outcomes

Using OpenHumanDesignMCP direct calculation:

| Input | Profile |
|---|---:|
| `1952-08-02 6:46pm Glendale California` | `4/6` |
| `1952-08-02 6:46pm UTC fallback` | `3/6` |
| `1952-08-02 6:46am Glendale California` | `3/5` |
| `1954-08-02 6:46pm Glendale California` | `3/5` |

`Glendale California` must resolve to:

```json
{"timezone":"America/Los_Angeles","utc_offset":-7.0}
```

August civil time in Glendale is PDT (`UTC-7`) even if a family member colloquially says “PST.”

## Correct workflow

1. **Do not add `chart_overrides`** for Profile/Type/Authority/Cross/line mechanics.
2. Extract source birth details exactly. If the user sends an image, use OCR/vision and explicitly compare:
   - year,
   - date,
   - AM/PM,
   - local time,
   - UTC time shown by the reference,
   - birthplace,
   - timezone label.
3. Reproduce with the real engine, not the LLM:
   - import/call `calculate_chart_detailed`, or use the exact app calculation endpoint,
   - print normalized UTC birth time,
   - print Personality Sun and Design Sun gate/line,
   - compare against old fallback behavior if needed.
4. Fix source data/geocoding/timezone conversion/runtime wiring until the real calculation matches the reference, or report the precise disagreement.
5. Quarantine any override-generated artifacts; regenerate clean artifacts only from the corrected source data.
6. Verify with `pytest` where available and a focused `/tmp/hermes-verify-*` script for runtime/artifact state when the repo has no canonical suite.

## Pitfall wording for user-facing replies

Say:

> The source chart says 1954, while the bot had 1952. With 1954/6:46pm/Glendale the engine returns 3/5. The earlier 3/6 was UTC fallback; the 4/6 branch was real for 1952 PM, but it was the wrong year.

Do **not** say “the bot is right” until the source details have been compared field-by-field.

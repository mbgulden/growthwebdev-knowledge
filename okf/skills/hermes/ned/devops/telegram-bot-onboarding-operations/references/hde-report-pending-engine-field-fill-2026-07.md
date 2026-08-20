# HDE report field-gap fill pattern — 2026-07

## Trigger

Use when a generated Human Design PDF/HTML contains user-facing placeholders such as `Pending in engine`, especially in natal report field cards.

## Durable lesson

Do not leave placeholder tombstones in customer PDFs. If the calculation engine does not expose a named secondary/coaching field yet, either derive a transparent value from fields the engine already returns, or show a clear explanatory value tied to available engine data. Keep core mechanics exact: Type/Profile/Authority/Cross/Gates/Lines still come only from the real calculation engine.

## Recommended field fills

- **Bridging Gates**: derive from active gates whose harmonic channel mate is inactive; these are relationship/split-definition connector gates.
- **Melancholy**: derive from active gates in Individual-circuit channels.
- **Fears**: derive from active gates whose center is Spleen.
- **Penta Qualities**: derive from active gates that appear in the engine `PENTA_GATES` list.
- **Genetic Trauma**: use a transparent lens from an existing activation, e.g. Personality Earth gate, rather than fabricating a proprietary trauma field.
- **AstroHD Star Archetype**: use Personality Sun gate as the solar archetype when no richer star-archetype field exists.
- **Distraction / Transference**: tie to returned Perspective/Motivation values, e.g. `Tracked through Perspective: ...`, rather than pretending the engine separated those subfields.
- **Cycle dates**: fill approximate Saturn Return, Second Saturn Return, Uranus Opposition, and Chiron Return dates from birth date using documented year offsets if exact transit-return solving is not yet implemented.
- **Birth/location/timezone**: carry caller-provided local birth date/time, location, timezone plus engine UTC/design dates where available.

## Verification recipe

Use both canonical tests and a focused `/tmp/hermes-verify-*` script.

The focused verifier should:

1. Import the report server and call `compute_and_render()` for a natal chart using sparse-but-valid birth data.
2. Assert changed source no longer contains user-facing `Pending in engine`.
3. Assert the policy doc mentions that reports must not render `Pending in engine`.
4. Read generated HTML and assert:
   - no `Pending in engine`
   - no replacement placeholder like `Not returned by current engine`
   - formerly missing sections exist: Bridging Gates, Melancholy, Fears, Penta Qualities, Genetic Trauma, AstroHD Star Archetype, Birth Date (UTC), cycle dates, Gates + Planets.
5. Run `pdftotext <pdf> -` and assert extracted PDF text also has no placeholders and still has expected headings: `Your Human Design Natal`, `Your Design at a Glance`, `Gates + Planets`.
6. Remove the verifier script and label the result focused ad-hoc verification unless the canonical suite also passed.

## Pitfalls

- Do not solve this by hiding entire sections. The user asked for complete info; derive or explain the field.
- Do not invent chart mechanics. Derived fields must be explicitly based on available engine activations.
- Do not treat PDF file size as quality proof. Inspect HTML and extracted PDF text.
- If Hermes verification nags after a previous verifier, rerun a fresh `/tmp/hermes-verify-*` script against the exact changed paths and summarize it as ad-hoc verification.

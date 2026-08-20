# HDE Natal Chart Field Standard — 2026-07-16

## Trigger

Michael approved the staging cream/sage design direction, then corrected the content layer: HDE natal chart outputs were too shallow and needed a professional, coaching-ready representation of advanced fields plus planet/gate activations. He also called out mojibake/wrong-character artifacts such as corrupted rich-text versions of “You're”.

## Durable lesson

For HDE natal charts, do not stop at Type / Strategy / Authority / Profile / Incarnation Cross. Those are anchors, not the whole coaching object. Becca Gulden’s coaching preference is to go deeper on **planet + gate combinations** because those combinations often reveal the useful current-circumstance, challenge, relationship, opportunity, and gift patterns.

## Required natal field groups

Render the fields in organized, compact groups with short descriptions so the PDF/bodygraph/Telegram answer does not become a cluttered dump.

### Core mechanics

- Profile
- Type
- Definition
- Authority
- Strategy
- Signature
- Not-Self Theme
- Incarnation Cross

### Advanced orientation

- Variables
- Environment
- View / Perspective
- Distraction
- Sense
- Trajectory
- Cognition
- Motivation
- Transference
- Determination

### Coaching / education lenses

- Bridging Gates
- Melancholy
- Fears
- Penta Qualities
- Genetic Trauma
- AstroHD Star Archetype

### Timing and transparency

- Birth Date
- Birth Date (UTC)
- Design Date
- Design Date (UTC)
- Location
- Time Zone
- Saturn Return (UTC)
- Second Saturn Return (UTC)
- Uranus Opposition (UTC)
- Chiron Return (UTC)

## Planet + gate representation

Use a professional activation map with:

- Personality vs Design side,
- Planet,
- Gate.Line,
- Center,
- Gate theme/name,
- short note on the planet’s significance.

Planet significance can be concise, e.g. Sun = visible life-force theme; Earth = grounding/integration; Moon = emotional pull/need; Mercury = communication; Venus = values; Mars = maturation/assertion; Jupiter = growth/opportunity; Saturn = discipline/lessons; Uranus = originality/disruption; Neptune = mystery/sensitivity; Pluto = transformation/depth; Nodes = direction/orientation.

## Mojibake hygiene

Generated chart surfaces should repair or reject common rich-text corruption before display. At minimum, normalize corrupted apostrophes/quotes/dashes and the specific copied corruption Michael flagged for “You're”. Do not preserve corrupted examples inside persistent docs unless quoted as plain explanatory prose, because future verification may treat them as remaining artifacts.

## Implementation pattern used

- `reports/server.py`: helper functions for display-safe text, compact field-card sections, and a planet/gate activation table.
- `api/routes/bodygraph.py`: expose `meta.field_descriptions`, advanced meta fields, and a structured `activations` array so web/bodygraph surfaces can render the same information.
- Missing upstream values should render as `Pending in engine` rather than silently disappearing.
- Channel keys in bodygraph payloads should be JSON-safe strings (e.g. `26-44`) rather than tuple keys.

## Verification pattern

Use a `/tmp/hermes-verify-hde-natal-fields-*.py` focused verifier that:

1. Compiles changed Python files.
2. Builds a sample Michael-style chart fixture with the required advanced fields.
3. Verifies all labels and representative values appear in generated HTML.
4. Verifies the planet/gate activation map appears.
5. Generates a PDF and runs `pdfinfo`, `pdftoppm`, and preferably `pdftotext`.
6. Verifies bodygraph payload has `field_descriptions`, advanced meta, and `activations`.
7. Scans changed artifacts for mojibake and shaped secrets.

Label this as focused ad-hoc verification, not suite green.

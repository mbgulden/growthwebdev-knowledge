# HDE chart/report split-brain and launch-gap proof pattern — 2026-07-16

## Trigger

Use this when HDE Telegram, report PDFs, bodygraph JSON, or coaching surfaces disagree about chart facts, advanced variables, gates, planets, or expert-corrected fields.

## Durable lesson

The HDE chart stack can split into separate truth sources:

1. The guest Telegram runtime can calculate a simplified chart.
2. The report server can recalculate the chart independently for the PDF.
3. Stored person profiles can contain expert-corrected chart fields.
4. The bodygraph renderer can require a different channel shape than the report JSON.

If these are not reconciled, the system can look healthy while producing PDFs/JSON that disagree with the user-facing coaching standard.

## Required fix pattern

- Guest chart generation should call `calculate_chart_detailed`, not the simplified `calculate_chart`, when downstream products need planet/gate coaching content.
- Preserve full `personality_planets` and `design_planets` in `chart_data.json`.
- Preserve known expert corrections in `people/<slug>/profile.json` under `chart_overrides`.
- Merge `chart_overrides` into the generated local `chart_data.json` before saving.
- Pass the same `chart_overrides` to `hde-reports.service` so the PDF report and JSON agree.
- In the report server, merge overrides after raw calculation and before `build_natal_report`.
- Normalize string channels like `1-8 (Inspiration)` into renderer-friendly dicts like `{gates: [1, 8], name: "Inspiration"}` before calling `render_bodygraph`.
- Repair mojibake before rendering and before saving docs; do not keep corrupted examples as literal text in reference files.

## Verification recipe

Use focused ad-hoc verification under `/tmp/hermes-verify-*` and label it as ad-hoc, not suite green:

1. Compile guest runtime and report-server Python files.
2. Restart only the services needed for the path being proved.
3. Trigger the real guest chart function in the guest container, not only a pure unit import.
4. Verify result string contains both `pdf_path=` and `image_path=`.
5. Verify latest PDF and PNG are non-empty/substantial.
6. Read the produced `chart_data.json` and assert:
   - corrected customer fields are present,
   - `personality_planets` exists and has many planet entries,
   - `design_planets` exists and has many planet entries,
   - incarnation cross/advanced variables match the approved standard.
7. Render PDF pages with `pdftoppm`, OCR them with `tesseract`, and assert visible terms such as:
   - `Martyr - Heretic`,
   - `External - Markets`,
   - `Gates + Planets`,
   - `Professional Activation Map`,
   - `Trauma of Rejection`,
   - `Sadalsuud`.
8. Assert OCR has no mojibake markers like `â€`, `Youâ`, or `Â`.
9. Scan changed runtime/report files for token/API-key/DB-URL-shaped secrets.

## Launch-gap audit pattern

When Michael asks what gaps remain before family testing or live launch, do not answer from memory alone. Run a small live-state check first:

- service status for staging API/router/report/payment,
- guest container health,
- Redis queue pending counts, treating stream `length` as history, not backlog,
- staging route smoke for `/deconditioning/` and `/success/`,
- production route smoke for `/deconditioning/`, `/privacy/`, `/terms/`,
- API hostname smoke for Cloudflare Access gating.

Report separately:

- safe for internal staging QA,
- safe for family staging test,
- not safe for public production traffic.

Common blockers:

- production route fallbacks returning homepage content with HTTP 200,
- public API hostname behind Cloudflare Access when browser checkout needs it,
- lack of real human Telegram `/start` proof,
- local live service fix not pushed because lane guard blocks `reports/server.py`,
- staging/source service split where systemd `WorkingDirectory` points at a different checkout than the edited code,
- live Stripe cutover not proven.

## Lane/promotion pitfall

If `reports/server.py` is outside Ned's push lane but the live systemd service uses it, you may verify and restart the local service when explicitly working on runtime proof, but report the persistence gap clearly: the correct lane owner must promote/cherry-pick the local commit or equivalent change so a clean redeploy does not erase the fix.

# HDE family tester identity + artifact cleanup (2026-07)

## Trigger

Use this when family/beta tester logs show successful onboarding/chat but messy chart artifacts: generic `Sanctuary Guest` profile names, stale PDF placeholders, suspicious timezone/geocode fallbacks, or internal Telegram premium alert failures.

## Durable lessons

### 1. Names are identity, not decoration

Do not only rename final PDFs. Fix the root association path:

- Detect explicit self-name statements before LLM fallback, e.g. `my name is Jessica Piscitello` or `this chart is for Jessica Piscitello that's me`.
- If the active/default profile is generic (`Sanctuary Guest`, `user`, `my_human_design`, etc.), migrate the stored profile to the real slug.
- Move/repair all connected state together:
  - `/workspace/people/<old_slug>/profile.json` → `/workspace/people/<real_slug>/profile.json`
  - `/workspace/people/index.json` default/person entry
  - `/workspace/charts/<relationship>/<old_slug>/` → `<real_slug>/`
  - profile `name`, `slug`, `subject_name`, latest chart paths
  - chart JSON / coach manifest display name
- Then regenerate the chart/report so future media names and manifests use the real name.

Verification should prove no stale generic dirs remain and that the next PDF/image path includes the real slug/name.

### 2. Regenerate artifacts after report-quality fixes

When a fix removes placeholders like `Pending in engine`, existing sent PDFs are still stale. Regenerate affected tester reports and QA with `pdftotext`, not just file size:

- no `Pending in engine`
- no `Not returned by current engine`
- no wrong display name such as `Sanctuary Guest`
- includes expected coaching sections such as `Gates + Planets`

### 3. Treat UTC/0,0 as a geocoder failure signal

If a known real place comes back `timezone: UTC` with `lat/lon` near `0,0`, do not accept it as valid. For HDE staging family-test gaps, patch the resolver/gazetteer or add a narrow override in the chart runtime, then regenerate. Example found here: `Provo, UT` had to resolve to `America/Denver`, not UTC.

Do not force chart mechanics directly; fix location/timezone input so the calculation engine naturally returns the chart.

### 4. Premium Telegram alerts: plain text beats Markdown fragility

Onboarding tokens often contain underscores/hyphens. Telegram `sendMessage` with Markdown parse mode can fail with `400 Bad Request`. For internal premium signup alerts:

- Send plain text unless rich formatting is actually required.
- Do not wrap tokens in Markdown code spans.
- Log non-200 Telegram responses explicitly; do not treat a completed checkout/email as proof the internal Telegram alert worked.

## Verification recipe

1. Compile patched guest runtime and webhook files.
2. Deploy the guest runtime template to affected live guest workspaces/containers if the fix must apply immediately.
3. Restart affected guest containers and wait for healthy status.
4. Exercise the name-association canary against the affected guest API.
5. Regenerate reports for affected testers.
6. Run PDF text QA for placeholders/wrong names/required sections.
7. Check `coach_manifest.json` for name, location, timezone, type/profile/authority.
8. Restart the API service if webhook alert code changed.
9. Monkeypatch/smoke-test alert payload construction: one `sendMessage`, no `parse_mode`, token retained as plain text.

## Reporting shape

Report per tester as fixed evidence, not a narrative:

- Jessica: profile/index/artifacts now real-name slug; stale generic dirs absent; regenerated PDF path.
- Ruth: clean regenerated report; correct profile from engine.
- Alicia: clean regenerated report; geocode/timezone corrected.
- Premium alert: plain-text payload verified; service restarted.

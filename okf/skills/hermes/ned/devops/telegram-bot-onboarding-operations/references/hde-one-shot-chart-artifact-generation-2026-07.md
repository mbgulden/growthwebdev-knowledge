# HDE one-shot chart artifact generation pitfall (2026-07)

## Class of issue

In the HDE guest runtime, a tester may paste a complete birth-detail sentence after the guide says it can build a chart. If that turn falls through to the LLM path, the guide can produce a plausible chart summary while no durable artifacts are created: no `chart_data.json`, bodygraph PNG, PDF report, coach manifest, or Telegram media upload.

This is worse than an explicit error because it sounds successful to the tester.

## Reproduction shape

Example user flow:

1. Tester asks what the bot can do.
2. Bot says it can build a chart.
3. Tester sends one sentence with date/time/place, e.g. `06/08/1976 10:38 PM Provo, UT`.
4. LLM summarizes chart traits.
5. Filesystem under `/home/ubuntu/users/guest_<id>/charts/...` has no PNG/PDF/artifact directory.

A later name/profile message may still not backfill artifacts unless deterministic chart generation is explicitly invoked.

## Durable fix pattern

Add a deterministic pre-LLM rail in `guest_agent_server.py`:

- Broaden `extract_full_birth_details()` to accept natural one-shot phrases:
  - `for <First Last> ...`
  - `birth place <City, ST>` / `born in <City, ST>`
  - American date + AM/PM time.
- Add `generate_one_shot_chart_from_details(text)` that:
  - extracts name/date/time/place,
  - creates/updates the people index and default person,
  - calls `generate_chart_for_birth_details(...)`,
  - returns the `__CHART_FILE_PATHS__` metadata so router can upload media.
- In `/api/message`, call the one-shot chart handler inside the explicit structured command branch before `handle_natural_profile_update()` and before LLM fallback.
- Copy the patched runtime to both the repo-local template and live template/runtime as appropriate:
  - `scripts/guest_hermes_template/guest_agent_server.py`
  - `/home/ubuntu/guest_hermes_bot/guest_agent_server.py`
  - affected `/home/ubuntu/users/guest_<id>/guest_agent_server.py`
  - affected container `/workspace/guest_agent_server.py`
- Restart only the affected guest container when doing a targeted rescue.

## Verification recipe

Use focused ad-hoc verification, not full-suite language:

1. Compile repo template, host template, and affected live runtime.
2. POST the one-shot birth-detail message to the affected guest `/api/message`.
3. Assert response includes `image_path`, `pdf_path`, and `pdf_paths`.
4. Check host artifacts exist:
   - `charts/personal/<slug>/chart_*.png`
   - `charts/personal/<slug>/report_*.pdf`
   - `chart_data.json`
   - `coach_manifest.json`
5. Parse `chart_data.json` and manifest; verify the subject name and paths match.
6. Run `pdftotext` and require report headings like:
   - `Your Human Design Natal`
   - `Your Design at a Glance`
   - `Gates + Planets`
7. Use `file` to confirm PNG/PDF types.
8. If rescuing a live tester, send both photo and document through Telegram and record safe `ok/message_id` metadata only.

## Pitfalls

- Do not trust a natural-language chart summary as proof of chart generation.
- Do not trust PDF existence alone; verify text extractability after renderer/font fixes.
- Do not make the user repeat birth details if the recent retained thread has them.
- Do not commit or print tokens; only report safe Bot API `ok` and message IDs.

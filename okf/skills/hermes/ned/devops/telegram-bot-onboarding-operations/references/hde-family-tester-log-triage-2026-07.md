# HDE family tester log triage — 2026-07

Use when Michael asks “how do the logs/conversations look for <tester names>?” after family/beta testers run HDE staging.

## What worked in this session

A useful triage needed four evidence layers, not just `journalctl`:

1. **Systemd health**
   - `hde_router.service`, `hde_api_staging.service`, and `hde-reports.service` active state.
   - Recent service logs around the tester window.

2. **Database truth**
   - Read the actual runtime `DATABASE_URL` from the running service environment; the systemd unit may set SQLite, but the `EnvironmentFile` can override to Postgres.
   - Inspect `users`, `invitations`, and `bot_instances` for tester email, premium/consent, guide name, invitation use, Telegram linkage, workspace path, and status.
   - Mask tokens/customer IDs.

3. **Guest workspace artifacts**
   - `/home/ubuntu/users/guest_<id>/conversation_history.json`
   - `people/<slug>/profile.json`
   - `people/<slug>/latest_chart_data.json`
   - `charts/personal/<slug>/chart_data.json`
   - `coach_manifest.json`
   - generated PDF/image artifacts.

4. **Artifact QA**
   - `pdfinfo`, `pdftotext`, and targeted grep for `Pending in engine`, `Not returned`, wrong display name, Type/Profile/Authority/Strategy, and `Gates + Planets`.
   - Do not treat a sent PDF as clean just because Telegram upload succeeded.

## Durable findings / patterns

- **Existing artifacts can lag behind live fixes.** Ruth and Alicia PDFs still contained `Pending in engine` because they were generated before the report-placeholder fix; regenerate, don’t assume the code fix retroactively cleans already-sent PDFs.
- **Identity propagation matters.** Jessica’s chat accepted “this chart is for Jessica…” but stored/sent artifacts remained `Sanctuary Guest`. Treat that as a product gap, not a cosmetic nit.
- **Timezone labels are QA signals.** Alicia’s Provo chart manifest showed `timezone: UTC`; flag that for parsing/calculation review even if the high-level chart looked plausible.
- **Conversation errors can be phrasing-specific.** Alicia’s explicit “PDF report and image” request was rejected, while a shorter “Generate my chart…” phrasing worked. Log triage should identify brittle intent/parser wording, not only crashes.
- **Premium alert path is separate from customer success.** Jessica’s checkout/onboarding/email succeeded, but internal Telegram premium notification returned `400 Bad Request`; report as an operator-alert gap, not a customer blocker.
- **Early incorrect chart reads are still gaps after later correction.** Ruth’s conversation first reported 3/6 and later 3/5 before current stored data showed 4/6. Flag mixed-profile history and regenerate a clean current report.

## Recommended report shape

```md
🟡 Short version: usable, but not clean.

| Person | What worked | Gap |
|---|---|---|
| Alicia | onboarded, chart generated | PDF placeholders, timezone/parser gap |
| Ruth | onboarded, PDF/image sent | prior wrong profile + stale placeholder PDFs |
| Jessica | premium, onboarding, chat | artifact name still Sanctuary Guest; premium alert 400 |

**Already fixed / not active now**
- Old crash loops that are no longer present.

**Gaps to address**
1. Regenerate stale artifacts after live fixes.
2. Fix identity/name propagation.
3. Fix timezone/location parsing.
4. Patch brittle chart/PDF intent parser.
5. Fix operator premium notification failure.
```

## Privacy posture

For family/beta testers with review consent, summarize conversation quality and gaps. Avoid dumping full transcripts by default; use snippets internally to detect parser/continuity failures and report the operational/product gap.

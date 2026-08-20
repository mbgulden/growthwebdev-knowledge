# AI Consulting Outreach Reconciliation Pattern — 2026-07-08

## Context

Daily Golden Thread selected AI Implementation Consulting. The registry next action said to send Idaho MSP batch 1. The pipeline initially claimed six MSPs had been contacted on July 7, but Michael corrected this on 2026-07-09: **no ITAD or AI Consulting emails had been sent yet**. The correct remediation was to reset those records to unsent/contact_found, guard stale follow-up drafts with DO NOT SEND, and keep all email sending/manual sent-status authority with Michael.

## Durable Lesson

For outbound/revenue projects, **never execute a "send outreach" next action directly from the registry and never infer that email was sent from tracker text alone**. Reconcile canonical pipeline/tracker docs against operational CRM/launcher assets, then require Michael's explicit confirmation before marking anything sent/contacted or scheduling follow-up. The stale tracker state would have caused false follow-ups and damaged trust.

## Verification Pattern

Before generating tasks or executing outreach work:

1. Check canonical tracker/pipeline docs for contact status and follow-up dates.
2. Check CRM/export files for status drift.
3. Check launcher/email assets for name/email mismatches.
4. Treat any mismatch as a blocker task before any fresh-send task.
5. Generate deterministic verification scripts/commands so future agents can prove the CRM, launcher, and follow-up files agree.

## Evidence From Session

- `idaho-pipeline.md` had incorrectly showed 23 Idaho leads and 6 contacted MSPs; after Michael's correction it shows 22 contact_found/ready leads, 1 lost lead, and 0 sent/contacted.
- `leads.json` was reset so no lead has `status=contacted` until Michael explicitly says he sent the email.
- Stale follow-up drafts were guarded with `DO NOT SEND` because no initial email was sent yet.
- Benconnected draft/address data was reconciled to `Ben Moore` / `info@benconnected.com`.
- Execution created/used:
  - `parse_pipeline.py`
  - `generate_launcher.py`
  - `verify_reconciliation.py`
  - `python3 outreach.py verify`

## Done Gate Used

The task is only considered safe after independent verification returns:

```text
python3 generate_launcher.py && python3 outreach.py verify && python3 verify_reconciliation.py
=> PASS
lead_count 23
statuses {'contact_found': 22, 'lost': 1}
sent/contacted leads 0
fresh-send leads 22
follow-up leads 0
```

Plus: if any follow-up draft files remain, they must contain a `DO NOT SEND` guard until Michael records the initial send.

## Pitfall

Do not confuse "revenue first" with "send immediately." For outbound, preserving trust and preventing duplicate/wrong-recipient sends is revenue protection. Reconciliation is the revenue action when the send list is stale.

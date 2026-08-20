# OKF Evidence Placement for Prismatic Governance Work

## Trigger

Use this when a Prismatic Proof Loop, governance audit, remediation, or closeout creates evidence markdown during a Hermes session.

## Rule

Hermes output/cache paths are not canonical:

```text
~/.hermes/profiles/*/output/
~/.hermes/profiles/*/cache/documents/
```

They are useful for Telegram delivery and session scratch only. Durable evidence belongs in OKF.

## Destination map

| Evidence type | Canonical OKF location |
|---|---|
| Security incident / access fix / outage remediation | `okf/audits/incidents/YYYY-MM-DD-slug.md` |
| Operational audit / recurring scan evidence | `okf/audits/YYYY-MM-DD-slug.md` or existing audit subfolder |
| Strategy / architecture / operating doc | `okf/operations/YYYY-MM-DD-slug.md` |
| Standards / rubric / governance policy | `okf/standards/slug.md` |

## Required sequence

1. Write temporary evidence to Hermes output if needed for delivery.
2. Promote or rewrite the durable artifact into the OKF location above.
3. Run a fresh `/tmp/hermes-verify-*.py` verifier against the OKF artifact.
4. Label the result: **ad hoc targeted verification**, not canonical/full-suite green.
5. If OKF has unrelated dirty changes, do not commit opportunistically; report exact git state and the new file path.
6. Link the OKF artifact in Linear/comments/summaries when available.

## Artifact verifier expectations

A good verifier checks the file exists and contains:

- classification / purpose;
- source artifact if any;
- trigger or exit criterion;
- evidence/commands/results;
- verification scope label;
- cleanup status;
- remaining blockers/follow-ups;
- no obvious copied secrets.

Make artifact verifiers Markdown-tolerant. Do not edit the durable artifact just to satisfy a brittle verifier if the content is already correct.

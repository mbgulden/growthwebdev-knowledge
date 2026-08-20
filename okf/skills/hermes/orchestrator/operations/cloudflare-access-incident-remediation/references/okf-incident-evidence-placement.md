# OKF Placement for Cloudflare Access Incident Evidence

Use this when a Cloudflare Access incident/remediation produces an evidence markdown file.

## Canonical location

Durable incident evidence belongs in the workspace OKF, not Hermes profile output:

```text
/home/ubuntu/work/okf/audits/incidents/YYYY-MM-DD-slug.md
```

Hermes paths such as these are ephemeral delivery/session artifacts only:

```text
~/.hermes/profiles/*/output/*.md
~/.hermes/profiles/*/cache/documents/*.md
```

## Minimum OKF incident record

Include:

- OKF classification: domain, type, canonical home, source artifact if any, verification scope.
- Trigger: what alerted or what live behavior was wrong.
- Root cause verified: specific policy/app/routing reason.
- Changes applied: policy/app/rule changes without printing secrets.
- Verification: no-redirect live checks showing Access/deny behavior instead of origin content.
- Safety check: especially webhook paths that must remain deliverable.
- Separate follow-ups: adjacent app-auth issues that should not be mixed into the Access routing fix.
- Retention rule: OKF is canonical; Hermes output is scratch/delivery.

## Verification after writing OKF artifact

After writing/updating the OKF file, create and run a temporary verifier:

```text
/tmp/hermes-verify-<slug>-*.py
```

The verifier should check:

- the OKF file exists;
- required headings/sections are present;
- all protected URLs are documented;
- verification result/status fields are present;
- no obvious Cloudflare tokens/API keys/secrets were copied into the artifact;
- cleanup removed the temporary verifier.

Report this as **ad hoc targeted verification**, not canonical/full-suite green.

## Pitfall from 2026-07-08

A first verifier failed because it expected unbolded labels while the OKF doc used Markdown-bolded labels. A second failed because normalization stripped underscores from JSON keys. The durable lesson is: make artifact verifiers Markdown-tolerant and JSON-key-safe; do not edit the OKF file just to appease a brittle verifier when the artifact content is already correct.

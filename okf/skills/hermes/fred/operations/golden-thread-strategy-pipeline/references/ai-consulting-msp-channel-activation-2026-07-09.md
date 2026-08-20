# AI Consulting MSP Channel Activation — 2026-07-09

## Context

Daily Golden Thread selected `ai-consulting` from `/home/ubuntu/work/project-registry.json` because it was the stalled revenue-priority venture. The active blocker was activation/conversion, not infrastructure. Critical guardrail: agents may prepare and verify outreach assets, but Michael alone sends outbound email and confirms/marks sent/contacted.

## Useful Pattern

When the registry next action says "Michael sends outbound" and sources confirm no sends yet, do **not** create another fresh-send task or mark follow-ups active. Convert the pipeline step into a send-safe enablement artifact with explicit manual-send guardrails and measurable signals.

For this run, the winning strategy was the MSP channel / Trojan Horse wedge. Tasks were created as a parent sprint plus children:

- Parent: MSP channel activation sprint — verified partner kit.
- Child 1: build one-client experiment partner kit.
- Child 2: add MSP partner CTA path to Beyond SaaS materials.
- Child 3: create Michael-only manual-send checklist.
- Child 4: define MSP channel signal tracker and first-touch thresholds.

## Verification Steps That Mattered

Before execution:

1. Query live Linear issues for the selected project and use current state, not stale registry issue IDs.
2. Reconcile outbound state locally:
   - `leads.json`
   - `leads_reconciled.json`
   - one-click launcher presence
   - backup filenames such as `.bak-no-emails-sent-*`
3. Verify that `sent_at`, `contacted_at`, and `status in {sent, contacted}` counts are zero before saying no outreach has happened.
4. Build the marketing site if the strategy claims infrastructure/site readiness (`npm run build` for beyondsaas-site; report as targeted build evidence only).

After orchestrator execution:

1. Independently inspect the artifact instead of trusting the orchestrator's PASS JSON.
2. Run a deterministic check for required sections, revenue CTA, assumption signals, and CRM no-send preservation.
3. Be careful with placeholder detection: Markdown checkboxes (`- [ ]`) are not placeholders. Search for `TODO`/`TBD` separately from bracket syntax.
4. If wording misses a rubric phrase such as "Michael-only", patch the artifact directly and rerun the targeted check.
5. Post evidence to the exact Linear child and move only that child to Done; do not close the parent until all children are evidenced.

## Done Gate Used

A send-safe partner kit child can be Done when:

- Artifact exists.
- Required sections are present: audience, one-client CTA, co-branded/white-label option, referral economics, non-solicitation reassurance, security posture link/placeholder, Michael-only manual-send instructions, signal tracker.
- No `TODO` or `TBD` placeholders remain.
- Revenue CTA is concrete (e.g., one-client AI Readiness Audit + referral economics).
- Assumption signals are observable: reply, intro, booked audit, explicit no.
- Local CRM verification still shows zero sent/contacted records unless Michael explicitly confirmed a send.

## OKF Evidence

Promote the durable summary to OKF operations, then run a focused `/tmp/hermes-verify-*.py` script against the artifact itself. If the OKF repo has unrelated dirty/untracked files, do not commit opportunistically; report the path and git state.
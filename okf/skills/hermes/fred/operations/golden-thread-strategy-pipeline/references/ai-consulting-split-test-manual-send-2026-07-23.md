# AI Consulting Split-Test Manual Send Gate — 2026-07-23

## When this applies

Use this pattern for Golden Thread runs on AI Consulting or any outbound/revenue project where the pipeline is built but outbound is blocked on Michael-only manual sending.

## Durable lessons

1. **Do not create more agent-send or follow-up work when CRM says zero sent/contacted.** Reconcile first with the CRM, launcher, and local verifiers. If the counts are still zero, the agent-safe move is send enablement.
2. **Convert the activation blocker into a falsifiable split test.** For AI Consulting, the useful next slice was a Michael-only 5 MSP vs 5 direct legal/healthcare checklist, not another generic outreach asset.
3. **Keep CRM state unchanged unless Michael confirms manual sends.** Verification should prove both `leads.json` and `leads_reconciled.json` still have zero sent/contact markers after agent work.
4. **AGY self-report is useful but not sufficient.** Rerun the deterministic artifact verifier and reconciliation verifier directly before reporting or moving Linear state.
5. **Repeated OKF verification nudges require a fresh `/tmp/hermes-verify-*` run against the exact changed OKF path.** The verifier should check the OKF artifact contract, not final chat formatting: selected project, research paths, assumptions, strategy matrix, Linear IDs, rubric evidence, guardrails, verification commands, and absence of placeholder or secret markers.

## Proven execution shape

- Top task: create a Michael-only split-test checklist.
- Artifact shape:
  - Preflight checks.
  - Batch A: 5 MSP leads.
  - Batch B: 5 direct legal/healthcare leads.
  - Manual send steps using the launcher.
  - Post-send confirmation fields.
  - Explicit no-agent-send and no-CRM-mutation guardrail.
  - 7-day thresholds for replies, intros, booked audits, explicit no, and pivot/continue rules.
- Rubric:
  - Unit: artifact exists, has both batches, preflight, send steps, post-send fields, and no unfinished placeholder markers.
  - Integration: references launcher, CRM files, MSP kit, and security posture; reconciliation verifier still returns zero sent/contacted.
  - Revenue: names the $4,500 AI Readiness Audit, $15,000 pilot, and/or 15% MSP referral economics.
  - Assumption: defines a falsifiable MSP vs direct vertical benchmark.

## Verifier pattern

Use a temporary verifier created with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`; run it; remove it in the same command. Import every module used by both wrapper and inner verifier. Print machine-legible JSON with:

- `status`
- `verification_type`: `ad-hoc targeted verification, not suite green`
- `checked_paths`
- `runtime_command`
- `missing_sections`
- `missing_markers`
- `forbidden_found`
- `evidence_path`
- cleanup fact after removal

Avoid literal secret/provider prefixes and avoid embedding exact forbidden placeholder strings in durable OKF prose unless the verifier intentionally permits them.

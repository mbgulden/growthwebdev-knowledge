# Agent Governance Modular Reconciliation Pattern

Use this reference when a production dashboard/API asset exists outside `main` while the dashboard is being split or regenerated.

## Core lesson

A generated dashboard can be locally fresh and still be unsafe to deploy if production contains a good unmerged asset. Before replacing or deploying a regenerated dashboard, compare the candidate output against production/runtime bytes and inspect meaningful deltas. If production has a useful surface missing from `main`, port it path-by-path into the modular source instead of overwriting production.

## Workflow

1. Build the modular dashboard with the deterministic builder and run the freshness check.
2. Compare generated dashboard bytes against the deployed/runtime dashboard.
3. If production has extra functionality:
   - preserve production as the source of truth for that asset;
   - port only the needed module/API/card/script paths onto current `main`;
   - regenerate from modular source;
   - prove the generated output is byte-identical to the preserved production dashboard where visual behavior is supposed to be unchanged.
4. Keep proof classes separate:
   - builder freshness;
   - targeted API/unit tests;
   - browser/rendered proof;
   - GitHub CI;
   - immutable release proof;
   - production overlay/deploy proof.
5. Do not claim backend security repairs are production-live until the immutable release files have actually been overlaid or deployed and the service has been restarted/verified.

## Secret-safe API/display review checklist

When porting dashboard API data from legacy rows, review the **entire serialized payload**, not just explicit link fields.

Probe for all of these in registry/run/completed-work/packet values:

- `Authorization: Bearer ...`
- `password=...`, `token=...`, `api_key=...`, `client_secret=...`
- provider-like tokens such as Slack/GitHub/AWS-shaped values
- private-key material
- credential-bearing URLs/userinfo
- unsafe URL schemes
- path traversal
- control characters and multiline text
- nested packet dictionaries/lists/scalars

Expected behavior:

- unsafe display fields fail closed to a fixed placeholder that does **not** include the rejected value;
- unsafe proof locators are omitted or replaced with generated safe issue links;
- safe issue links, safe local paths, and safe evidence markers remain visible;
- safe marker names containing words like `SECRET_SAFE_ERRORS_OK` are not falsely redacted.

## Proof packet example

```text
COMMAND=builder check;focused API/security tests;Ruff;public security readiness;public smoke;dashboard byte comparison;desktop/mobile rendered proof
RESULT=PASS
SCOPE=production dashboard asset reconciliation plus secret-safe governance API contract
AD_HOC_OR_CANONICAL=ad-hoc targeted + browser/rendered + GitHub CI + immutable release proof
NOT_CLAIMING=canonical full suite,production backend overlay/restart unless separately completed
MARKER=AGENT_GOVERNANCE_MODULAR_RECONCILIATION_OK
```

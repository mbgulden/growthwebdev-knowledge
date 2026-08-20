# Completed-work skill-pack contract wiring

Use this when the AGY/completed-work lane is green enough that the next improvement is prompt/skill quality rather than more infrastructure.

## Session pattern

After the limited AGY overnight dry-run and max_tasks=2 unattended-window guard were complete, the next slice was **Shared Agent Skill Pack + Packet Contract Wiring**.

The work was intentionally repo-level docs/static verifier rather than live Hermes profile mutation:

```text
skills optimize for best output
infrastructure protects against worst output
```

## Contract to document

A class-level completed-work skill-pack reference should include:

- canonical completed-work packet contract,
- proof packet contract,
- non-claims contract,
- safe file/provenance scope,
- AGY/Fred/George/Kai agent-specific examples,
- minimal dispatch preflight checklist,
- dashboard/Linear writeback language for `skill_pack_state=loaded` and `skill_pack_state=unavailable_or_not_reported`,
- no-secret static scan.

Required references to include in docs/config:

```text
shared/prismatic-completed-work-contract
shared/prismatic-proof-packet
shared/prismatic-non-claims
shared/prismatic-safe-file-scope
agy/agy-structured-result-packet
agy/agy-one-task-scope
agy/agy-dashboard-work
agy/agy-model-preflight
fred/fred-clean-pr-builder
fred/fred-verification-gate-runner
fred/fred-deploy-proof
george/george-dashboard-operator-audit
kai/kai-prismatic-domain-review
```

## Static acceptance booleans

Verifier should prove:

```text
shared_contract_exists=true
agy_packet_example_has_source_path=true
proof_packet_example_has_command_result_log_scope_nonclaims_marker=true
non_claims_example_present=true
agent_specific_skill_matrix_present=true
no_secrets_in_docs=true
```

## Non-claims

Do not claim:

```text
skills_installed_in_all_live_profiles
agents_retrained
overnight_autopilot_active
auto_merge_enabled
production_deploy
canonical_full_suite_green
```

## Verification shape

Use a focused static test such as:

```text
python3 -m py_compile tests/test_agent_skill_packs_static.py
python3 -m pytest -q tests/test_agent_skill_packs_static.py
```

Then, if the workspace stale-verification guard repeats, create a fresh `/tmp/hermes-verify-*.py` that checks exactly the docs/test paths named by the guard and cleans itself up. Label it ad-hoc targeted, not canonical full suite.

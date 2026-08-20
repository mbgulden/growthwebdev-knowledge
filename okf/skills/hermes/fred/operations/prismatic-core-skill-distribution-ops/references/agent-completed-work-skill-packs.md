# Agent Completed-Work Skill Packs — Prompt 3 Pattern

Use this reference when asked to wire shared/agent-specific skill packs for completed-work packets without mutating live Hermes profiles.

## Durable pattern

This is a repo-level contract/docs/config slice, not a live skill installation slice:

```text
shared completed-work contract docs
+ agent-specific packet examples
+ dispatch preflight checklist
+ dashboard/writeback language
+ static verifier/no-secret scan
```

Correct target marker:

```text
AGENT_COMPLETED_WORK_SKILL_PACKS_OK
```

## Recommended repo artifacts

```text
docs/agent-skill-packs/completed-work-skill-packs.md
tests/test_agent_skill_packs_static.py
```

The docs should include:

1. Canonical completed-work packet contract.
2. Proof packet contract with `COMMAND`, `RESULT`, `LOG`, `SCOPE`, `NOT_CLAIMING`, and `MARKER`.
3. Shared skill packs:
   - `shared/prismatic-completed-work-contract`
   - `shared/prismatic-proof-packet`
   - `shared/prismatic-non-claims`
   - `shared/prismatic-safe-file-scope`
4. Agent-specific skill matrix for AGY, Fred, George, and Kai.
5. Agent-specific packet examples, especially an AGY packet with explicit `source_path`.
6. Minimal dispatch preflight checklist.
7. Dashboard/Linear writeback language showing `skill_pack_state`, shared packs, agent packs, packet contract version, and validation state.
8. Explicit non-claims.

## Static verifier acceptance booleans

The verifier should print/prove:

```text
shared_contract_exists=true
agy_packet_example_has_source_path=true
proof_packet_example_has_command_result_log_scope_nonclaims_marker=true
non_claims_example_present=true
agent_specific_skill_matrix_present=true
no_secrets_in_docs=true
```

Also run:

```bash
python3 -m py_compile tests/test_agent_skill_packs_static.py
python3 -m pytest -q tests/test_agent_skill_packs_static.py
```

## Boundaries

Do not claim any of these from this slice:

```text
skills_installed_in_all_live_profiles
agents_retrained
overnight_autopilot_active
auto_merge_enabled
production_deploy
canonical_full_suite_green
```

No AGY launch, no two-task window execution, no live Linear mutations, no production deploy.

## PR discipline pitfall

If a PR initially has checkpoint commits, squash to one clean commit before polling CI. If local checkout cannot switch to `main` because another worktree owns it, verify merge via `origin/main` and `gh pr view` rather than trying to mutate the locked worktree.

## Stale verifier pitfall

When Hermes stale verification names changed docs/test paths, run the fresh `/tmp/hermes-verify-*` against the workspace checkout (`/home/ubuntu/work/prismatic-engine`) and the exact changed files, not merely against deployed runtime. Clean up the stale mobile verifier if it is named in the warning.
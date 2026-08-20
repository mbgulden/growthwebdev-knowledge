# GRO-3739 redispatch verifier assertion calibration

Use this when an already-finalized task is redispatched and the required action is a fresh verification refresh, not new implementation.

## Pattern

1. Confirm completion signals first:
   - Linear state is `In Review` (or otherwise already finalized).
   - PR/attachment exists and points at the task branch.
   - Remote branch exists.
   - Prior evidence comment has concrete command output, not only a generic finalize note.
2. Create a clean detached `/tmp` worktree from the remote task branch.
3. Run the task's focused verifier and focused test from that clean worktree.
4. Create a fresh `/tmp/hermes-verify-*` ad-hoc verifier and clean it up in `finally`.
5. Update only `/tmp/issue-batches/<ISSUE>_RESULT.md` with fresh evidence.
6. Remove the temp worktree and re-query Linear state/attachments before returning `[SILENT]`.

## Verifier assertion calibration pitfall

When writing the fresh `/tmp/hermes-verify-*` script, assert the durable acceptance contract, not imagined exact wording.

Bad example from the GRO-3739 refresh:
- The implementation correctly added `### Verifier artifact checklist` and linked the master plan to `pwp-verifier-artifact-requirements.md`.
- The first ad-hoc verifier failed because it asserted invented phrases (`PR/Linear attachment checklist`, `Before moving a theme task to Done`) that were not part of the implemented contract.
- The second failed because it required exact title-case phrases in the master plan even though the master plan validly referenced the requirements document and artifact categories in sentence form.

Good verifier shape:
- Requirements doc contains the concrete checklist and required evidence fields:
  - `Verifier artifact checklist`
  - `Build/test`, `Accessibility`, `Visual/regression`, `Contract/schema`, `Deployment/provenance`
  - `verification_status`, `verification_scope`, `failure_category`, `cleanup_status`, `done_gate_result`
- Master plan links to the requirements doc and names the required artifact families / done gate.
- The verifier prints the temp path, assertion result, exit code, and cleanup status.

## Reporting nuance

A failed over-strict verifier is not itself a blocker when the focused verifier/test pass and a corrected verifier proves the actual contract. Record the corrected fresh evidence in the local RESULT and suppress external delivery if Linear/PR state is already healthy.

## 2026-07-11 calibration addendum

A redispatch refresh can still fail after the canonical verifier and focused pytest pass if the ad-hoc verifier invents exact master-plan wording. For GRO-3739, requiring literal `Done` or `done gate` text in the master plan was too strict: the durable contract was present as `agents cannot mark done without verification output and done_gate_result=done`, plus the requirements-doc link and artifact families. The right ad-hoc assertion is case-insensitive and semantic:

- requirements doc contains the checklist title, artifact categories, and required evidence fields;
- master plan links `pwp-verifier-artifact-requirements.md`;
- master plan mentions verifier artifacts, artifact families such as build/test/accessibility/visual/contract/deployment, and `done_gate_result` or equivalent done-gate enforcement;
- canonical verifier returns `verdict=PASS` and `failures=[]`.

If the first ad-hoc verifier fails only because of literal-wording drift, rewrite the verifier immediately, rerun from a fresh `/tmp/hermes-verify-*` path, record the successful fresh output in `/tmp/issue-batches/<ISSUE>_RESULT.md`, and keep the final cron response silent when Linear/PR state remains healthy.

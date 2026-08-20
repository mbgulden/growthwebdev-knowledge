# Exact-tree merge and immutable deployment gate

Use this pattern when a Prismatic source candidate has been independently reviewed CLEAN and Michael's standing policy authorizes merge/deploy after exact-head proof.

## Gate sequence

1. **Freeze the candidate identity.** Record `HEAD`, `HEAD^{tree}`, parent/base SHA, changed-path containment, focused proof, canonical proof, and independent review handle.
2. **Verify live GitHub state before mutation.** Fetch the real remote, prove `origin/main` still matches the reviewed parent/base, and prove the branch/ref to be pushed is the exact reviewed SHA. Do not rebase or amend after CLEAN without re-review.
3. **Respect lane/branch hooks.** If a pre-push hook rejects an AGY lane branch for cross-lane infrastructure paths, inspect the policy script and publish through an allowed orchestrator lane while preserving the exact reviewed commit. Do not use `--no-verify` unless repo policy explicitly documents it.
4. **Treat hosted CI correctly.** Failing product checks block merge. Runner/billing/spending-limit failures with zero executed steps are hosted-infrastructure failures; under the preserved provider-neutral policy, they are not product evidence and can be bounded by local canonical + independent exact-head proof.
5. **Merge and prove exact tree.** After merge, verify the merge commit tree equals the reviewed tree. If it differs, stop and re-review the merged artifact.
6. **Build immutable release from the merge commit.** Use a new release checkout and versioned venv. Avoid mutable worktree dependence.
7. **Run isolated predeployment proof.** Run import/API smoke from an empty temp directory with only the release/venv on `PYTHONPATH`; a successful import from the current source checkout is contaminated and not release proof. Install declared extras needed for the runtime, then rerun smoke.
8. **Prepare rollback before touching production.** Write rollback instructions and deployment inputs. Use SQLite online backup for live DBs instead of raw file copies. Capture pre-state hashes/manifests.
9. **Cut over atomically.** Update the systemd drop-in and any active wrapper to the immutable release/venv, restart only the intended service, and auto-rollback on activation or health failure.
10. **Close with a post-write verifier.** Create a temporary `hermes-verify-*` script and prove GitHub PR state, release SHA/tree, clean release checkout, systemd `WorkingDirectory`/`ExecStart`, affected HTTP endpoints, additive DB migration, row-count preservation, wrapper target, rollback file, deployment receipt, handoff markers, and cleanup of temporary verifier/input files.

## Required production proof block

```text
COMMAND=<grouped exact commands or verifier path>
RESULT=PASS
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=GitHub PR state, exact release tree, systemd runtime, API smoke, DB migration, receipt/handoff
AD_HOC_OR_CANONICAL=ad-hoc targeted production closeout
NOT_CLAIMING=<producer success, new admission, cap increase, Linear write, branch deletion, consumer restart unless actually done>
MARKER=<slice-specific production marker>
```

## Pitfalls

- Do not claim a source-candidate proof covers deployment after editing receipts/handoffs; run a fresh post-write verifier that covers the changed files too.
- Do not classify a temp verifier syntax/test-node error as product failure. Fix the verifier and rerun until it exercises the product paths.
- Do not let source-checkout imports contaminate release proof. Start release smoke from a neutral directory.
- Do not mutate unrelated runtime pins. If a consumer intentionally remains on an older immutable release, prove and report that boundary.
- Do not synthesize DB rows for proof; preserve and compare existing row counts before/after additive migrations.

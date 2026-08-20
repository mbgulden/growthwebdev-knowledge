## Merge governance vs completed-work auto-integration

When Michael asks whether Prismatic already has an automated merge workflow, distinguish **existing governance/classification** from **missing end-to-end integration**.

Existing foundations may include worktree janitor classification, proof bundles, merge backlog APIs, and promotion recommendations such as `open-or-update-pr`, `capture-proof-or-promote`, `promote`, and `manual-conflict-review`. Do **not** overclaim these as a complete AGY/Fred/Ned completed-work auto-merger.

The remaining gap is the durable bridge:

```text
agent completed work
→ validate handoff/result packet
→ lane/scope/proof check
→ classify merge-ready / clean-rebuild / blocked / superseded / manual-review
→ create or update clean PR
→ run verification
→ write Linear/dashboard state
→ optionally enable safe merge only after policy gates
```

For dashboard/operator availability questions, probe local and public routes separately and report precisely: `health 200` does not mean `/` or `/dashboard` is up, `/workspace-tree 200` does not mean the root dashboard is up, and local API 200 + public 404 can indicate nginx/proxy exposure gaps. Session detail: `references/merge-governance-vs-auto-integration-2026-07-16.md`.


## PR cleanup / noisy branch triage

When asked to resolve open PRs, inspect whether the PR is actually mergeable and product-useful before merging. If a PR is contaminated with committed virtualenvs, generated/vendor files, wrong base branches, or broad historical changes, do not merge it as-is. Instead:

1. Inspect PR metadata, changed-file counts, target branch, CI, and whether it would regress current core modules.
2. Close PRs that target the wrong base or would delete/undo already-merged core work.
3. If a contaminated PR contains a useful slice, rebuild that slice as a clean main-based branch/PR with only product-relevant files.
4. Verify the clean replacement with focused tests/ruff/CI before merging.
5. Leave an explicit PR comment explaining why the original was closed/superseded.

A useful pattern from the filesystem smoke helper cleanup: port only the class-level helper/API and tests (`Finding`, `verify_files_exist`, `verify_files_nonempty`, `verify_files_substantive`) rather than merging a PR that also committed `.venv_dev` or unrelated historical files.

# GRO-3716 repeated ad-hoc verifier refresh pattern

## Context

A post-finalize detector repeatedly reported `Verification status: unverified` even after a focused pytest run and after one successful ad-hoc verifier. The detector specifically required a fresh temporary verifier under `/tmp` with filename prefix `hermes-verify-`, run against changed behavior, with cleanup and an explicit ad-hoc-verification summary.

## Durable lesson

When the detector repeats the same verifier prompt, treat it as a fresh evidence contract. Do not argue from prior pytest output, prior PR comments, or a previous `/tmp/hermes-verify-*` run. Create a new verifier each time and report the exact fresh path/output.

## Working shape

Use Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`, close the fd, write a focused script, run it with `python3`, print the command/path/exit/assertion summary, then remove it in a cleanup block.

For PWP deploy idempotency, the verifier should assert behavior directly rather than calling the full suite:

1. Import the branch under test by prepending the worktree and `plugins/` to `sys.path`.
2. Use a temp `PRISMATIC_STATE_DIR`.
3. Load `pwp_hook_test_plugin` through `PluginLoader`.
4. Run `PWPPluginRunner` three times:
   - first deploy with commit/theme/content hashes -> `deploy_skipped is False`, provider called, `on_deploy` fired;
   - exact replay -> `deploy_skipped is True`, reason is `matching_commit_theme_content_hashes`, provider not called, `on_deploy` not fired;
   - changed `theme_hash` or `content_hash` -> deploy occurs again and state persists the changed hash.
5. Print concise proof lines, for example:
   - `ASSERTIONS: first deploy recorded hashes; matching replay skipped provider/on_deploy; changed theme hash deployed and persisted`
   - `DEPLOY_PROVIDER_CALLS: 2`
   - `RUN_STATE_KEYS: [...]`
6. Print `CLEANUP: removed /tmp/hermes-verify-....py` after deletion.

## Reporting

Label the result as **ad-hoc targeted verification**, not suite green. If Linear already has a finalization comment, post a short evidence-refresh comment with verifier path, command, exit code, assertion summary, provider-call count, and cleanup status.

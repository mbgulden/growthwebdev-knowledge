# GRO-3695 already-finalized redispatch: missing local RESULT refresh

Use this pattern when a cron-dispatched implementation issue is already complete enough to be in Linear `In Review`, has a remote `origin/ned/<issue>` branch and prior finalization/verification comments, but the local `/tmp/issue-batches/<ISSUE>_RESULT.md` is missing or stale. Treat an existing RESULT from a prior cron tick as refreshable, not authoritative, when the dispatcher re-emits the same issue: gather fresh Linear/remote/PR/check/worktree evidence, overwrite the RESULT with the new timestamp and outputs, then suppress delivery if nothing changed.

**Repeated redispatch nuance:** if `/tmp/issue-batches/<ISSUE>_RESULT.md` is already present and non-empty, do not stop there. A repeated cron dispatch is itself a request for fresh completion evidence. Re-query Linear/labels/comments, check the remote branch and PR/check state, rerun focused verification in a clean detached worktree, rerun a fresh `/tmp/hermes-verify-*` targeted verifier, overwrite the RESULT with the new timestamp/output, remove the verifier/worktree, and then return exactly `[SILENT]` when there is still no blocker. Do not post duplicate Linear comments or rerun `finalize_task.sh` just because the local RESULT existed.

## Decision

Do **not** rebuild in the shared checkout and do **not** post duplicate Linear comments just to satisfy the scanner. Treat the run as a verification-refresh pass.

## Safe sequence

1. Re-read the autonomous task skeleton anyway; the cron contract still applies.
2. Query Linear for state, labels, and recent comments.
3. Check remote branch and PR status:
   - `git ls-remote --heads origin ned/<ISSUE>`
   - `gh pr list --head ned/<ISSUE> --json number,title,state,baseRefName,headRefName,url,statusCheckRollup`
4. If the shared checkout is dirty or on another task, leave it untouched.
5. Create a detached clean worktree from the remote task branch:
   - `git fetch origin ned/<ISSUE>`
   - `git worktree add --detach /tmp/prismatic-<issue>-refresh FETCH_HEAD`
6. Run focused verification in the clean worktree.
7. If the detector needs fresh targeted evidence, create a `/tmp/hermes-verify-*.py` script that prints:
   - verifier path
   - tested command
   - command exit
   - assertion summary
   - verification exit
   - cleanup status
8. Write or refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with Linear state, remote branch SHA, PR status, focused verification output, ad-hoc verifier output, lane diff summary, and why duplicate finalize/comment was skipped.
9. Remove the temporary verifier and worktree.
10. Before suppressing delivery, run a local artifact sanity check: the RESULT file is non-empty, the temporary worktree path no longer exists, the `/tmp/hermes-verify-*` verifier no longer exists, and the shared checkout status is unchanged from the pre-refresh snapshot.
11. Return exactly `[SILENT]` when there is no new blocker and no human action is needed.

## Concrete GRO-3695 evidence shape

GRO-3695 was redispatched after it was already `In Review` with `origin/ned/GRO-3695` present and prior finalization + verification refresh comments. There was no PR. The shared checkout was dirty/on `ned/GRO-3672`, so the safe path was a detached `/tmp/prismatic-gro3695-refresh` worktree.

Verification used both:

```bash
python3 -m pytest plugins/pwp/tests/test_theme_installer.py -v
```

and an ad-hoc verifier for:

```bash
python3 scripts/pwp theme install <valid_theme> --target <tmp>/astro-site --tenant sentinelitad --engine-version 0.2.0 --json
```

The verifier asserted successful tenant-scoped Astro/PWP file copies, SHA-256 token/module/content-schema hashes in the install manifest, and unsafe overwrite refusal on a second install. The local RESULT was refreshed and delivery was suppressed.

**Second-install refusal output shape (2026-07-10 refresh):** the unsafe-overwrite case exits nonzero, but with `--json` the refusal details are structured in stdout, not necessarily stderr or a plain text line. The second command returns JSON with `ok=false` and an `errors[]` array containing strings like `Refusing to overwrite existing file without --force: <path>`. Ad-hoc verifiers should parse `proc2.stdout` as JSON and assert `ok is False` plus at least one matching `errors[]` entry. Do not assert that `(stderr + stdout)` contains a generic `already exists` phrase; that stale assertion caused a false verifier failure even though the implementation was behaving correctly.

## Verifier contract pitfall: installer JSON/manifest shape

Do not assume the `pwp theme install --json` output includes `manifestPath`, and do not assume the manifest nests theme metadata under `theme.id`. On the current branch shape verified during a redispatch refresh, the command returns:

- `installRoot`: path to the tenant-scoped install root
- `tokenHash`, `moduleHash`, `contentSchemaHash`: SHA-256 strings in the command JSON
- `themeId`, `themeVersion`: top-level command JSON fields

The manifest lives at `Path(output["installRoot"]) / "install-manifest.json"` and stores top-level `themeId`, `themeVersion`, `tenant`, `tokenHash`, `moduleHash`, and `contentSchemaHash`. `installRoot` is already the tenant-scoped install root (`<target>/pwp/themes/<tenant>`), while `copiedFiles` are relative to `targetProject`; when asserting representative copied files, check paths under `targetProject`, e.g. `<target>/pwp/themes/<tenant>/theme.json`, `<target>/src/components/pwp/Hero.astro`, and `<target>/src/styles/pwp-theme.css`. The current fixture emits `themeId=pwp.theme.trust-light` and `themeVersion=0.1.0`; do not hard-code stale `pwp-valid-theme`/`1.0.0` expectations. Hash values include a `sha256:` prefix, so assert the prefix plus a 64-hex payload rather than raw length 64.

If an ad-hoc verifier fails because it used the older `manifestPath`/`theme.id`, stale fixture identity, raw-hash-length, or `installRoot` path assumptions, fix the verifier and rerun it. Capture the corrected verifier output in `/tmp/issue-batches/<ISSUE>_RESULT.md`; do not treat the first failed verifier as a task blocker when the implementation output itself proves the shape changed.

## Refresh-pass verification pitfalls

- **Do not hard-code the GitHub owner/repo when checking PR status.** In local-clone remotes, `dev-repo` may point at a filesystem path and the authenticated `gh` default may resolve to a different owner than an assumed org string. First run `gh repo view --json nameWithOwner,url` from the clean checkout (or omit `--repo` when already in the repo) and then run `gh pr list --head ned/<ISSUE> --json number,title,state,baseRefName,headRefName,url,statusCheckRollup`. A failed `gh pr list --repo <guessed-owner>/<repo>` is not proof there is no PR.
- **Do not trust `comments(last:N)` ordering without sorting.** Linear comment nodes can appear chronological or otherwise surprising depending on query shape/API behavior; for completion-signal checks, fetch enough comments and sort by `createdAt` or compute `MAX(createdAt)` client-side before concluding the latest finalization/verification comment is absent or stale.
- **Keep redispatch refresh automation boring and cleanup-safe.** When the refresh needs several dependent shell/Python steps (clean worktree, focused pytest, ad-hoc verifier, RESULT rewrite, cleanup), prefer writing a short `/tmp/<issue>_refresh.py` runner with `write_file` and executing it once over a dense nested heredoc/env-var bash pipeline. If an inline script fails mid-run, immediately remove any detached `/tmp/prismatic-<issue>-refresh-*` worktree before retrying. The final sanity check must prove: focused pytest exit `0`, ad-hoc verifier exit `0`, RESULT file non-empty, temp worktree removed, temp `/tmp/hermes-verify-*` file deleted, and the shared checkout status byte-for-byte matches the pre-refresh status.
- **Concurrent RESULT-file refresh warning:** if `write_file` reports that `/tmp/issue-batches/<ISSUE>_RESULT.md` was modified by a sibling subagent or another process, do not treat that as a blocker when the file is only local cron evidence and the fresh verification just ran successfully. Preserve the important fresh evidence by rewriting the RESULT, then run the normal sanity checks (`test -s`, temp verifier removed, temp worktree removed, shared checkout unchanged). Avoid duplicate Linear comments/finalize calls solely to compensate for a local RESULT overwrite warning; the durable authority remains Linear state/comments plus the remote branch.
- **Cleanup sanity must be scoped to this refresh's artifacts, not every stale `/tmp` artifact.** A shell check like `! compgen -G '/tmp/hermes-verify-*.py'` is too broad on a long-lived VM: unrelated stale verifier scripts from other tasks can make a successful refresh look dirty. The refresh runner should record the exact verifier path it created and assert only that path was deleted. Likewise, record the exact detached worktree path for the current refresh; if an older same-issue worktree is discovered later (for example `/tmp/prismatic-gro3695-refresh-*` from a prior tick), remove it only after confirming it is registered as a detached worktree at the same remote SHA. Do not let unrelated `/tmp` residue trigger duplicate finalize/comment churn.
- **Existing RESULT is not a skip condition on redispatch.** If `/tmp/issue-batches/<ISSUE>_RESULT.md` already exists and was refreshed minutes earlier (even by a sibling subagent), the cron redispatch still warrants fresh completion evidence: re-query Linear, check remote branch and PR list/checks, rerun focused pytest plus a fresh ad-hoc verifier in a clean detached worktree, then overwrite the local RESULT. If Linear remains `In Review`, no `dispatch:ready` label is present, the remote branch matches, and `gh pr list --head <branch>` returns `[]`, suppress delivery after cleanup rather than posting another Linear comment or rerunning finalize.
- **Do not build the clean worktree from ambiguous `FETCH_HEAD` after fetching multiple refs.** A command like `git fetch origin deploy-fresh ned/GRO-3695` can leave `FETCH_HEAD` pointing at `origin/deploy-fresh`, so the detached worktree lacks `plugins/pwp/tests/test_theme_installer.py` and `scripts/pwp`; pytest exits `4` and the ad-hoc verifier fails with “can't open file .../scripts/pwp”. Fetch/update the task ref explicitly (`git fetch origin ned/GRO-3695:refs/remotes/origin/ned/GRO-3695`) and create the worktree from `origin/ned/GRO-3695` (or a verified commit SHA), not bare `FETCH_HEAD`.
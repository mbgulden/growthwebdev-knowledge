# GRO-3739 redispatch worktree cleanup refresh

## Pattern

When a cron redispatch targets an issue that is already finalized (Linear `In Review`, remote `origin/ned/<issue>` exists, prior finalization/evidence comments exist, and an open PR/branch already carries the work), treat the pass as a **fresh verification refresh**, not a rebuild and not a duplicate finalize.

This applies even when `/tmp/issue-batches/<ISSUE>_RESULT.md` already exists from a recent earlier refresh. The cron contract is asking for current execution evidence; a stale local RESULT is not enough.

## Required sequence

1. Re-read the autonomous task skeleton anyway. Do not skip the contract just because the issue looks finished.
2. Query fresh completion signals:
   - Linear issue state and labels.
   - Remote branch head (`git fetch origin <branch>` + `git rev-parse origin/<branch>`).
   - PR metadata/checks (`gh pr view ... --json statusCheckRollup,mergeable,mergeStateStatus,...`).
3. Leave the shared checkout untouched if it is dirty or on another task branch.
4. Create a detached `/tmp` worktree from the remote task branch:
   - `git worktree add --detach <tmpdir> origin/ned/<issue>`
5. Run focused evidence from the detached worktree:
   - the canonical verifier, if the branch has one;
   - the focused pytest path;
   - a fresh `/tmp/hermes-verify-*` ad-hoc verifier that prints path, command, exit codes, assertion summary, and cleanup status.
6. Remove the detached worktree with the installed Git-compatible form:
   - `git worktree remove --force <tmpdir>`
   - Do **not** use `--quiet`; this Git build rejects it, and masking cleanup failure is worse than noisy output.
7. Overwrite only `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh evidence, PR state, Linear state, cleanup status, and shared-checkout branch.
8. Read the RESULT back and run an explicit cleanup check (`git worktree list | grep -i <issue> || true`, plus `test -e` for the `/tmp/hermes-verify-*` and worktree paths). The detector expects proof that the refresh artifact exists and temporary verifier/worktree paths were removed, not just a claim in prose.
9. Re-query Linear state/labels and PR checks after the refresh. If shell quoting mangles an inline GraphQL payload (common with `$id:String!` + nested selections under tool wrappers), write the JSON body to `/tmp/<issue>_linear_query.json` and call `curl --data-binary @file`; do not waste budget debugging quote layers.
10. Do not rerun `finalize_task.sh` or post another Linear comment when all completion signals are already good and no check is failing.
11. Final cron response is exactly `[SILENT]` when the redispatch produced no new blocker.

## Verification contract example

For GRO-3739 the successful refresh shape was:

```text
WORKTREE=/tmp/ned-gro-3739-refresh-<timestamp>-XXXXXX
HEAD=c00db449d493957ffaca6f539217729644dde11a
STATUS=## HEAD (no branch)|
---CANONICAL---
python3 scripts/verify_pwp_verifier_requirements.py --json
... "verdict": "PASS" ...
CANONICAL_EXIT=0
---PYTEST---
python3 -m pytest plugins/pwp/tests/test_pwp_verifier_requirements.py -q
1 passed
PYTEST_EXIT=0
---ADHOC---
ADHOC_PATH=/tmp/hermes-verify-gro-3739-XXXXXX.py
COMMAND=/usr/bin/python3 scripts/verify_pwp_verifier_requirements.py --json
STDOUT.verdict=PASS
STDOUT.failures=[]
MISSING_FILES=[]
MISSING_TERMS=[]
ASSERTION=PASS required files, checklist/artifact/attachment/evidence terms, and canonical verifier PASS
ADHOC_EXIT=0
ADHOC_CLEANUP=removed ... exists=false
WORKTREE_CLEANUP=removed ... exists=false
GRO3739_WORKTREE_HIT_COUNT=0
```

## Pitfall

A pre-run alert like “tasks piling up” or a fresh `TASK:<ISSUE>` line does not prove the implementation is incomplete. It proves the scanner redispatched the issue. Verify current state, refresh evidence, and suppress external delivery if nothing changed. Conversely, do not let a recent local RESULT file short-circuit the fresh-verification step; the detector keys on fresh evidence and cleanup, not on the existence of an old RESULT.

When scripting the cleanup check under `set -euo pipefail`, never run `git worktree list | grep -i <issue> | wc -l` bare. Zero matching worktrees makes `grep` exit 1 and can abort the script before the RESULT file is rewritten, even though cleanup succeeded. Use `git worktree list | { grep -i <issue> || true; } | wc -l` or temporarily disable `pipefail`, then read the RESULT back. If the cleanup probe is embedded in a Python refresh wrapper, do not pass that whole pipeline string to `subprocess.run()` in list/argv mode — use `shell=True` deliberately for the pipeline or avoid the shell entirely by reading `git worktree list` output and filtering in Python. Otherwise a successful verification can crash at the post-cleanup check before the RESULT is rewritten.

A second cleanup check should distinguish Git worktree registrations from stray filesystem directories. `git worktree list` can be clean while `compgen -G '/tmp/ned-gro-3739-refresh-*'` still sees an empty stale directory from an earlier failed/partial refresh. If `POST_REFRESH_WT_EXISTS=true` but `WORKTREE_HITS=0`, inspect/remove the stale empty directory, then append a post-refresh block to the RESULT with `POST_WORKTREE_HITS=0`, `POST_ADHOC_EXISTS=false`, `POST_REFRESH_WT_EXISTS=false`, current Linear state, and PR state. The detector cares that the final RESULT proves both registered worktree cleanup and temp-path cleanup.

If a refresh wrapper fails after writing `/tmp/issue-batches/<ISSUE>_RESULT.md.tmp`, do not leave the stale `.tmp` beside the real RESULT. Either overwrite the canonical RESULT with a fresh successful run or append a clear failure record, then remove the stale tmp file and any temporary GraphQL payloads. Add explicit post-refresh lines such as `STALE_TMP_RESULT_EXISTS=false` and `LINEAR_QUERY_PAYLOAD_EXISTS=false` so the next redispatch does not confuse an old failed attempt with current evidence.

When generating ad-hoc verifier Python from a shell heredoc or nested script, avoid accidental newline escaping inside Python string literals (for example `replace("\n", " | ")` can become an unterminated literal if the wrapper expands it wrongly). Safer options: write the verifier from Python using a raw triple-quoted string, or keep the verifier simple enough that the canonical/pytest evidence plus a correctly generated ad-hoc script can be rerun quickly. If the first ad-hoc verifier fails due only to wrapper quoting, rerun fresh and record the successful verifier plus cleanup; do not escalate a quoting artifact as a task blocker.

When re-querying Linear from Python/urllib during a refresh, pass Linear API keys as the raw `Authorization: <lin_api_...>` header, not `Authorization: Bearer <key>`. Linear returns HTTP 400 with `It looks like you're trying to use an API key as a Bearer token` for the Bearer form. Also, when reading `comments(last: N)`, do not assume `nodes[-1]` is the latest comment; compute `max(createdAt)` when the timestamp matters. The GraphQL response shape can make a stale-looking node appear last in a smaller window even when a newer dispatcher comment exists in the issue history.

If the first Linear re-query in a refresh artifact fails because the inline GraphQL string is malformed, append a corrected `LINEAR_RETRY_FIXED` block instead of throwing away the otherwise-good verification evidence. Prefer a multi-line variables query with visibly balanced braces over a compressed one-liner; a one-character extra `}` can produce Linear's opaque `HTTPError 500` + `GRAPHQL_VALIDATION_FAILED` response. After the fixed retry succeeds, append a final cleanup block showing `POST_WORKTREE_HITS=0`, `POST_ADHOC_EXISTS=false`, `POST_REFRESH_WT_EXISTS=false`, `STALE_TMP_RESULT_EXISTS=false`, and `LINEAR_QUERY_PAYLOAD_EXISTS=false`. Remove stale `/tmp/*<ISSUE>*linear*json` payloads from earlier attempts before writing the final cleanup check so the detector does not mistake old payloads for current leakage.

# HDE GRO-3994 shell env + PR body pitfalls

Session: HDE checkout funnel instrumentation finalization (GRO-3994), 2026-07-18.

## `source .env` can rewrite `HOME` and break `~/.hermes/...` paths

Observed failure after sourcing profile env files before finalize:

```text
bash: /home/ubuntu/.hermes/profiles/ned/home/.hermes/profiles/ned/scripts/finalize_task.sh: No such file or directory
```

Root cause: a sourced env changed `HOME`, so `~/.hermes/...` expanded relative to the wrong home directory.

Safe pattern:

```bash
ORIG_HOME=/home/ubuntu
set -a
[ -f /home/ubuntu/.hermes/profiles/orchestrator/.env ] && source /home/ubuntu/.hermes/profiles/orchestrator/.env
[ -z "$LINEAR_API_KEY" ] && [ -f /home/ubuntu/.hermes/profiles/ned/.env.bak ] && source /home/ubuntu/.hermes/profiles/ned/.env.bak
set +a
export HOME="$ORIG_HOME"

PRISMATIC_REPO_ROOT=/path/to/worktree \
FINALIZE_LOCK_FILES='actual edited paths here' \
bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

Use the absolute finalize script path after sourcing env files. Do not rely on `~` unless `HOME` was just re-asserted.

## Do not pass Markdown with backticks through `gh pr create --body "..."`

Observed failure while creating a PR body containing Markdown code spans:

```text
/usr/bin/bash: line 10: session_id: command not found
```

Root cause: backticks inside a double-quoted shell argument trigger shell command substitution before `gh` receives the body.

Safe pattern:

```bash
# Create the Markdown body as a file with write_file, not shell heredoc/echo.
gh pr create \
  --base main \
  --head ned/GRO-XXXX \
  --title "[Ned] ... (#GRO-XXXX)" \
  --body-file /tmp/gro-XXXX-pr-body.md
```

If the PR already exists or `gh pr edit --body-file` hits GitHub Projects Classic GraphQL deprecation errors, patch the PR via REST:

```bash
gh api repos/OWNER/REPO/pulls/PR_NUMBER -X PATCH -F body=@/tmp/gro-XXXX-pr-body.md
```

## Post-finalize verification note

After manual Linear evidence comments, query more than `comments(last:1)` if ordering appears stale. In the GRO-3994 run, `commentCreate` returned success and a comment id, while a first follow-up query showed the older finalize comment because the selection/order did not surface the new comment in the expected position. Re-query `comments(last:5)` before assuming comment creation failed.

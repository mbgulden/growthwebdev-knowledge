# Doc/blocker task verifier loop

Use this when a cron/verifier prompt repeats `Verification status: unverified` after a doc-only task, blocker-evidence task, or OAuth/credential-blocker documentation pass.

## Lesson

Do not answer from the finalize transcript, prior build output, or memory. The detector wants fresh tool output tied to the changed paths.

Even if the repo change is Markdown-only and the local RESULT file lives under `/tmp/issue-batches`, rerun the relevant repo verification in the exact task worktree, then assert the doc and RESULT contents directly.

## Minimal pattern

```bash
cd /tmp/<task-worktree>
npm run build
git diff --check
python3 - <<'PY'
from pathlib import Path
repo_doc = Path('docs/operations/<task-doc>.md')
result = Path('/tmp/issue-batches/<ISSUE>_RESULT.md')
assert repo_doc.exists() and repo_doc.stat().st_size > 500
assert result.exists() and result.stat().st_size > 500
repo_text = repo_doc.read_text(errors='ignore')
result_text = result.read_text(errors='ignore')
for needle in [
    'acceptance-relevant live proof',
    'credential or external blocker text',
    'explicit non-green/blocker status',
]:
    assert needle in repo_text + result_text, needle
print('targeted doc/result assertions passed')
PY
printf 'verification complete at '; date -u '+%Y-%m-%dT%H:%M:%SZ'
```

## Reporting

Report only fresh evidence:

- workspace path
- commands that passed
- build exit/result counts
- targeted doc/result assertion pass
- UTC verification timestamp

If the same verifier prompt repeats, rerun the fresh check again. Do not say “already verified” unless this turn includes new command output.

## GRO-3991 example

Changed paths:

- `/tmp/hd-platform-gro3991/docs/operations/hde-search-console-registration-3991.md`
- `/tmp/issue-batches/GRO-3991_RESULT.md`

Fresh verification that satisfied the prompt:

- `npm run build`
- `git diff --check`
- Python assertions that both files existed, were non-empty, and contained acceptance-relevant blocker/proof facts: HTTP 200 sitemap proof, `171` sitemap URLs, `invalid_grant`, `API keys are not supported by this API`, `GRO-3988`, `webmasters`, and `siteverification`.

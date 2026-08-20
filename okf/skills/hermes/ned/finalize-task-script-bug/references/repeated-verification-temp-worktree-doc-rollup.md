# Repeated verification prompts for temp-worktree documentation/control-plane changes

Use this when a system/user follow-up says `Verification status: unverified` or `stale` and lists changed paths even though the prior response already reported passing verification.

## Rule

Treat every repeated verifier prompt as a fresh evidence contract. Do not argue from the previous run or reuse the previous timestamp. Rerun the relevant command in the exact workspace referenced by the changed paths, read the output, and summarize only the new run.

## Known-good pattern

For doc/control-plane changes in a temp worktree:

```bash
set -euo pipefail
cd /tmp/<repo-task-worktree>
npm run build
git diff --check
python3 - <<'PY'
from pathlib import Path
repo_doc = Path('docs/operations/<doc>.md')
result = Path('/tmp/issue-batches/<ISSUE>_RESULT.md')
assert repo_doc.exists() and repo_doc.stat().st_size > 1000
assert result.exists() and result.stat().st_size > 1000
text = repo_doc.read_text(errors='ignore')
res = result.read_text(errors='ignore')
# assert issue IDs, status, blocker/proof wording, and expected evidence strings
for path in [repo_doc, result]:
    body = path.read_text(errors='ignore')
    forbidden = ['lin_api_', 'cfk_', 'cfut_', 'sk-', 'ghp_', 'gho_', 'ya29.']
    hit = [p for p in forbidden if p in body]
    assert not hit, f'secret-like prefixes in {path}: {hit}'
print('targeted doc/result assertions passed')
PY
printf 'fresh verification complete at '; date -u '+%Y-%m-%dT%H:%M:%SZ'
```

## Temp-worktree dependency bootstrap

If `npm run build` fails with `astro: not found` or equivalent missing local frontend binary in a freshly-created temp worktree, run `npm ci` in that worktree and rerun the build. Capture the successful rerun, not the transient missing-dependency failure. This is a bootstrap step for clean worktrees, not proof that the build is broken.

## Reporting shape

Keep the reply short and evidence-first:

- workspace path
- commands passed
- build summary (`10 page(s) built`, route-complete counts, etc.)
- targeted assertion/secret-scan result
- fresh UTC timestamp
- whether repair was needed

If the verifier prompt repeats again, rerun again. The detector keys on fresh execution, not on a true but stale human-visible summary.

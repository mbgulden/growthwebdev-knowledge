# Repeated `npm run build` verification nudge — HD Platform worktrees

## Trigger

Hermes may repeat an unverified-code warning even after a prior verification turn, especially when the changed paths include both repo files and a `/tmp/issue-batches/*_RESULT.md` artifact. Treat the repeat as a fresh verification request, not as something to debate from prior logs.

## Pattern that worked

1. Re-run the exact named command from the edited worktree:

```bash
cd /home/ubuntu/work/hd-platform-GRO-3988
npm run build
```

2. If the fresh worktree lacks dependencies and `astro` is missing, install using the repo's canonical lockfile path and rerun:

```bash
npm ci
npm run build
```

3. Add a tiny artifact verifier immediately after the build to assert the changed files and result markers exist. Keep it inline or under `/tmp/hermes-verify-*`; do not turn it into product code.

Example assertions:

```python
from pathlib import Path
required = [
    Path('scripts/google-oauth-scope-flow.py'),
    Path('docs/operations/hde-google-oauth-scope-flow-2026-07-19.md'),
    Path('/tmp/issue-batches/GRO-3988_RESULT.md'),
]
for path in required:
    assert path.exists(), path
text = Path('/tmp/issue-batches/GRO-3988_RESULT.md').read_text()
for marker in ['npm run build', 'Astro built 10 pages', 'human Google OAuth consent']:
    assert marker in text, marker
```

4. Report the final fresh output, not the previous turn's output. Include:
   - canonical command passed (`npm run build`),
   - build summary (page count/postbuild summary),
   - artifact verifier result,
   - git clean state when relevant,
   - remaining blocker if the implementation is verified but operational completion still needs human input.

## Pitfall

Do not answer a repeated verification nudge by saying verification already happened. The platform is telling you it did not detect fresh evidence. Run the command again and summarize only the new result.

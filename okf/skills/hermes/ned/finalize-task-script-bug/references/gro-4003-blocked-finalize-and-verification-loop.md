# GRO-4003 blocked finalize + verification-loop lesson

Context: Ned picked up a Search Console sitemap submission task in `hd-platform` while the main worktree already had unrelated dirty HDE GREEN edits. The safe path was an isolated worktree at `/tmp/hd-platform-gro4003`, a `ned/GRO-4003` branch, and a doc-only evidence commit before verification.

Durable lessons:

1. **Finalize can be necessary even when the task is blocked.** The autonomous skeleton says to run `finalize_task.sh` so work is not lost. But the script transitions the issue to `In Review`; if the acceptance criteria are still not green, immediately post a specific blocker comment and move the issue back to `Todo`.
2. **Use the real Ned/Orchestrator Linear key, not placeholder swarm `.env` entries.** `agentic-swarm-ops/.env` may contain placeholder-style values such as `__SET_IN_HOST_ENV...`; source `/home/ubuntu/.hermes/profiles/ned/.env` or the orchestrator profile for real Linear API operations after finalize.
3. **Doc-only changes still need the repo’s verification command when the harness requests it.** If `npm run build` fails with `astro: not found` in a fresh worktree, run `npm install` in that worktree, then rerun `npm run build`. Do not treat the first failure as evidence that verification is impossible.
4. **Do not claim Search Console green from live sitemap checks alone.** Live sitemap/robots proof is useful evidence, but Search Console submission/coverage remains blocked until a valid Google OAuth token/refresh token with Webmasters/Search Console scope works.
5. **If GitHub push auth fails, preserve the local branch and say exactly where it lives.** Do not bypass safe-push or protected-branch guards. Include worktree path, branch, commit SHA, and push error in the Linear blocker.

Recommended blocked-finalize sequence:

```bash
# after committing evidence in an isolated worktree
PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro4003 \
FINALIZE_LOCK_FILES='scripts/docs/gro-4003-search-console-sitemap-proof.md' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4003 ned/GRO-4003 ned

# if acceptance criteria are still blocked, use real Linear creds
set -a
source /home/ubuntu/.hermes/profiles/ned/.env
set +a
# post blocker comment and move issue back to Todo via GraphQL
```

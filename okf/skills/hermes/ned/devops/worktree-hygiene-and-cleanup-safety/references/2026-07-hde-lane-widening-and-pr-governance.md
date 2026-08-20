# HDE lane widening and PR governance — 2026-07

## When this applies

Use this when a repo-local checkpoint is blocked by Prismatic lane governance, the work has already been verified and bundled, and Michael explicitly authorizes widening Ned's lane for the checkpoint branch.

This is not a general bypass. Treat it as a scoped governance change that must be committed, verified, pushed, and reviewed like code.

## Pattern

1. Inspect the active pre-push mechanism:
   - `.git/hooks/pre-push`
   - `scripts/prismatic-pre-push-hook.py`
   - `PRISMATIC_ENGINE.yaml`
2. Patch `PRISMATIC_ENGINE.yaml` under `agents.ned.lanes.owner` to include only the needed checkpoint paths.
   - Include a comment naming the authorization, date, branch, and that it is temporary/scoped.
   - Include `PRISMATIC_ENGINE.yaml` itself in the widened owner list if the hook will evaluate the governance file as part of the push.
3. Verify the governance change before committing:
   - Parse YAML with Python.
   - Assert every previously blocked path is now covered by `agents.ned.lanes.owner`.
   - Dry-run the hook by piping a synthetic push ref line into `python3 scripts/prismatic-pre-push-hook.py origin <remote>`.
4. Run the relevant build/verification command again after the governance edit.
5. Commit the governance change with the required agent prefix.
6. Push normally. Do not bypass the hook; the point is to make the hook pass legitimately.
7. Open a PR to the correct staging/base branch. Prefer a `--body-file` to avoid shell expansion of Markdown.
8. Check PR checks and merge only after they pass.
9. Fetch and verify the merge landed on the base branch.
10. If the Pages/alias route still serves stale content after merge automation, redeploy the built `dist/` using the known Pages token mapping and smoke-test live URLs.

## Verification commands used in the session

```bash
python3 - <<'PY'
import yaml
with open('PRISMATIC_ENGINE.yaml') as f:
    cfg=yaml.safe_load(f)
owners=cfg['agents']['ned']['lanes']['owner']
required=['docs/','payment/','public/','shared/','tests/','.pwp/','package.json','package-lock.json','playwright.config.ts','lighthouserc.json','PRISMATIC_ENGINE.yaml']
missing=[x for x in required if x not in owners]
print('yaml_ok owners', len(owners), 'missing', missing)
raise SystemExit(1 if missing else 0)
PY

base=$(git rev-parse origin/$(git branch --show-current))
head=$(git rev-parse HEAD)
printf '%s %s refs/heads/%s %s\n' refs/heads/$(git branch --show-current) "$head" $(git branch --show-current) "$base" \
  | python3 scripts/prismatic-pre-push-hook.py origin https://github.com/mbgulden/hd-platform.git

npm run build
git push origin HEAD
```

## GitHub PR body pitfall

Do not pass a Markdown PR body with backticks inside a double-quoted shell argument. The shell can execute snippets like `` `PRISMATIC_ENGINE.yaml` `` and corrupt the body.

Safe pattern:

```bash
# write the body with write_file or a single-quoted heredoc first
gh pr create --body-file /tmp/body.md ...
# if edit fails due gh GraphQL/projectCards noise, patch via REST:
gh api -X PATCH repos/OWNER/REPO/pulls/NUMBER -F body=@/tmp/body.md
```

## Deployment follow-up

After the PR merged, GitHub checks passed, but the deploy-fresh alias briefly served stale legacy gates content. Redeploying the current `dist/` with the Pages token fixed it. Use the established mapping: Wrangler expects `CLOUDFLARE_API_TOKEN`; Ned's profile carries the Pages token as `CLOUDFLARE_PAGES_API_TOKEN`. Never print the token.

## Completion evidence to report

- PR URL and merge commit.
- Hook dry-run result: changed files, in-lane count, violations count.
- `npm run build` result.
- `git push` result with pre-push OK.
- PR checks result.
- Live smoke result for staging/alias routes.

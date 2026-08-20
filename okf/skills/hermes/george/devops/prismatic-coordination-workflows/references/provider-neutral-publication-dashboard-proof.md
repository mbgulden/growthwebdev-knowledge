# Provider-neutral PR publication and public dashboard proof boundary

Session-derived reference for Prismatic provider-neutral receipt slices when code is locally accepted but still needs PR publication, review, merge, and production proof.

## Trigger

Use when a Prismatic slice has exact-head native proof and needs to be published/reviewed without letting hosted provider state become the acceptance authority.

## Publication transport recovery

If HTTPS/SSH push is blocked by missing local GitHub transport configuration, recover by authenticating the GitHub CLI without exposing secrets:

```bash
gh auth login --hostname github.com --git-protocol https --web
# Michael completes https://github.com/login/device with the one-time code shown by gh.
gh auth setup-git
git push --set-upstream origin <branch>
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin refs/heads/<branch> | cut -f1)
test "$LOCAL" = "$REMOTE"
```

Report only the authenticated account name, branch, local/remote SHA equality, and PR URL. Never print token values or credential files.

## PR body creation

For proof-rich PRs, write the body to a temporary Markdown file and create the PR with `--body-file`. This preserves backticks, shell examples, hashes, and compact proof packets.

```bash
gh pr create \
  --repo mbgulden/prismatic-engine \
  --base main \
  --head <branch> \
  --title "<title>" \
  --body-file /tmp/<slice>-pr-body.md
```

Immediately re-read supported PR fields and verify:

```text
headRefOid == exact candidate commit
mergeable == MERGEABLE or explicitly explain blocker
baseRefName == main
statusCheckRollup classified as optional hosted signal unless local policy says otherwise
```

## Hosted check classification

If GitHub check runs fail before producing logs or clearly fail due to provider billing/infrastructure, classify them as optional hosted-signal failures. Do not call them product failures without logs. Record the check run URL/metadata and continue with native receipt evidence when the policy permits.

## Public dashboard proof boundary

When Michael supplies or confirms the canonical public dashboard URL, use it as the production/public proof target:

```text
https://prismatic.growthwebdev.com
```

Before merge/deploy, capture it as a **pre-deploy baseline** so public shell health is not conflated with the candidate being live:

```text
DASHBOARD_HTTP=<200|...>
HEALTH_HTTP=<200|...>
NATIVE_RECEIPT_API=<expected predeploy value, often 404>
STATE=healthy existing dashboard; candidate not deployed
```

After merge and immutable deploy/restart, repeat the same public checks and only then claim production proof for the native receipt API/dashboard integration. Preserve the existing dashboard shell; do not replace it with a fallback surface.

Public reverse proxies may expose gateway APIs only under `/api/gateway/...` even when localhost also serves `/api/...`. Verify the route actually used by dashboard JavaScript; do not call a public 404 a deployment failure until the gateway-prefixed alias is tested.

For durable systemd rollout, create a commit-addressed release checkout and matching non-editable venv, smoke it on an isolated port/temp state, then add one highest-precedence drop-in. Verify merge-commit tree equals the independently reviewed candidate tree before switching. Keep the prior release/venv/drop-in intact; rollback is removal of only the new drop-in plus daemon-reload/restart.

For end-to-end authority proof, persist a real signed receipt only after isolated-store acceptance. Retain real logs/artifacts under restricted durable state, prove public list/detail readback, and use element-scoped rendered DOM assertions (page scripts may still contain fallback text that makes whole-document negative-string assertions misleading).

## Large-dashboard rendered proof fallback

For a heavy dashboard where ordinary browser automation is noisy or times out, use an installed headless Chromium/Chrome command as a bounded rendered proof path and save a screenshot artifact. Treat this as a fallback technique, not as a durable claim that browser tooling is broken.

Useful pattern:

```bash
chromium --headless --disable-gpu --no-sandbox \
  --user-agent='Mozilla/5.0 PrismaticProof' \
  --virtual-time-budget=8000 \
  --screenshot=/home/ubuntu/<proof>.png \
  https://prismatic.growthwebdev.com/
```

Then inspect the screenshot/DOM for the specific markers under review and report the image path as proof of layout preservation only. It is not API proof unless paired with API/read-model checks.

## Non-claims to keep explicit

- PR open is not merged.
- Clean-room/local proof is not production proof.
- Public dashboard `200` before deploy proves the existing shell, not the candidate integration.
- Hosted CI red/queued is not native rejection unless policy explicitly makes it authoritative.

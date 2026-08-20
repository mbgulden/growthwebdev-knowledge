# HDE staging-governor push governance repair — July 2026

## Trigger

Use this reference when HDE launch work is already verified on local `staging`, but `git push origin staging` fails with a branch-prefix guard like:

```text
❌ [Prismatic Engine] Branch 'staging' doesn't match any agent prefix.
Valid prefixes: feature/ → fred, content/ → kai, research/ → agy, jules/ → jules, ned/ → ned
```

If Fred is the configured staging governor, this is not a Stripe/build issue. It is a repo-governance contract bug.

## Durable root causes found

1. `PRISMATIC_ENGINE.yaml` had stale staging config:

```yaml
staging:
  governor: "fred"
  branch: "deploy-fresh"
```

but the real runtime/promotion branch was `staging`.

2. The pre-push hook checked branch prefixes before checking the staging-governor exception, so `staging` was rejected before Fred could be recognized as governor.

3. Git was not using the repo-local fixed hook because global config overrode hooks:

```bash
git config --show-origin --get core.hooksPath
# file:/home/ubuntu/.gitconfig /home/ubuntu/.hermes/profiles/ned/git-hooks
```

The repo-local `.git/hooks/pre-push` can be correct and still ignored if `core.hooksPath` points elsewhere.

## Repair sequence

1. Lock governed files before editing:

```bash
node /home/ubuntu/.antigravity/swarm.js lock PRISMATIC_ENGINE.yaml fred
node /home/ubuntu/.antigravity/swarm.js lock scripts/prismatic-pre-push-hook.py fred
```

2. Patch `PRISMATIC_ENGINE.yaml`:

```yaml
staging:
  governor: "fred"
  branch: "staging"
```

3. Patch the hook so the staging branch exception is evaluated before normal branch-prefix validation:

```python
governor = str(config.get("staging", {}).get("governor", GOVERNOR_AGENT))
staging_branch_name = str(config.get("staging", {}).get("branch", STAGING_BRANCH))
is_staging_push = any(ref == f"refs/heads/{staging_branch_name}" for ref in remote_refs)
if is_staging_push:
    agent_id = governor if branch == staging_branch_name else _determine_agent(branch, config)
    if agent_id != governor:
        print(f"❌ [Prismatic Engine] Push to {staging_branch_name} is BLOCKED.")
        print(f"   Only {governor} (staging governor) can push to {staging_branch_name}.")
        print(f"   You are: {agent_id or 'unknown'}")
        return 1
else:
    agent_id = _determine_agent(branch, config)
    if agent_id is None:
        ...
        return 1

assert agent_id is not None
```

Also update the default constant and docs/comments from `deploy-fresh` to `staging` where this repo’s real staging branch is `staging`.

4. Install the tracked hook and make Git actually use it:

```bash
cp scripts/prismatic-pre-push-hook.py .git/hooks/pre-push
chmod +x .git/hooks/pre-push
python3 -m py_compile scripts/prismatic-pre-push-hook.py .git/hooks/pre-push
sha256sum scripts/prismatic-pre-push-hook.py .git/hooks/pre-push

git config --local core.hooksPath .git/hooks
git config --show-origin --get core.hooksPath
```

Expected active hook source:

```text
file:.git/config .git/hooks
```

5. Verify before pushing using a temp `/tmp/hermes-verify-*` script. Assertions should include:

- tracked and installed hook hashes match;
- config says `branch: "staging"` and `governor: "fred"`;
- hook has `STAGING_BRANCH = "staging"`;
- non-empty Fred staging push returns 0 and prints `Pre-push OK: fred → staging`;
- no-op/equal staging push returns 0, possibly with empty stdout;
- `ned/...` branch attempting to push remote `refs/heads/staging` returns 1 with `Only fred` / `You are: ned`;
- remote `refs/heads/main` push returns 1.

6. Push and read back:

```bash
git push origin staging
git ls-remote origin refs/heads/staging
git rev-parse HEAD
```

The remote staging SHA must match local `HEAD`.

7. Unlock after commit/push boundary:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock PRISMATIC_ENGINE.yaml fred
node /home/ubuntu/.antigravity/swarm.js unlock scripts/prismatic-pre-push-hook.py fred
```

## Pitfalls

- Do not stop after fixing `.git/hooks/pre-push`; verify `core.hooksPath`. A global hook path can keep running stale code.
- Do not bypass hooks or force-push around governance. Fix the governance contract and prove both allow and block cases.
- Do not classify a no-op hook run with empty stdout as failure if return code is 0 and local/remote refs are identical. Use a simulated previous remote SHA (`HEAD^`) to exercise the non-empty positive message path.
- Keep unrelated workspace dirt (env backups, runtime data, unrelated docs) unstaged.
- Use ad hoc targeted verification language unless the full canonical suite actually ran.

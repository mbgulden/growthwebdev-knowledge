---
name: agy-github-pr-workflow
description: Branch creation, Git staging/commits, pushing, and Pull Request lifecycle management via CLI.
version: 1.0.0
---

# AGY GitHub Pull Request Workflow

Manage code changes in Git, commit changes following standard formats, push, and submit PRs for review.

## Trigger Conditions

Use this skill when developing a feature, applying bug fixes, or publishing code changes to a Git remote.

## Numbered Steps with Exact Commands

1. **Create target branch**:
   Sync origin main and branch:
   ```bash
   git checkout main && git pull origin main
   git checkout -b feature/agy-implementation
   ```

2. **Commit changes**:
   Stage changes and commit with meaningful message:
   ```bash
   git add .
   git commit -m "feat(agy): implement dynamic skill loading backend"
   ```

3. **Push to remote**:
   ```bash
   git push -u origin feature/agy-implementation
   ```

4. **Create PR via GitHub CLI**:
   ```bash
   gh pr create --title "feat(agy): implement dynamic skill loading backend" \
     --body "Resolves issue related to executor autonomy. Integrates with $HOME/.antigravity/skills/." \
     --reviewer fred
   ```

## Pitfalls

- **Authentication failures**: Ensure `GH_TOKEN` or SSH credentials are set. If `gh` CLI prompts interactively, it will freeze in automated runs.
- **Untracked files**: Ensure new code files are explicitly added with `git add` to prevent losing work.

## Verification Steps

- Check Git status and branch name:
  ```bash
  git status
  git branch --show-current
  ```
- List open PRs to confirm creation:
  ```bash
  gh pr list --limit 1
  ```

---
name: agy-credential-security
description: Prevent API token and key leakage during file updates and commits.
version: 1.0.0
---

# AGY Credential Security & Git Hygiene

Safeguard environment variables, prevent key exposure, and maintain clean commits.

## Trigger Conditions

Use this skill when creating files containing tokens, modifying `.env` parameters, or staging changes to Git.

## Numbered Steps with Exact Commands

1. **Verify gitignore blocks keys**:
   Ensure `.env`, tokens, and logs are excluded:
   ```bash
   cat .gitignore | grep -E '\.env|\.token|logs'
   ```

2. **Pre-commit Scan for secrets**:
   Check staged diffs for private keys or passwords before committing:
   ```bash
   git diff --cached | grep -iE 'api_key|password|secret|token|lin_api_'
   ```
   Ensure no actual keys are shown in the diff.

3. **Secure workspace files**:
   Set file permissions on sensitive config paths:
   ```bash
   chmod 600 $HOME/.gemini/antigravity-cli/*token*
   ```

## Pitfalls

- **Accidental commit of .env**: Adding `.env` to git tracking is a major security risk. Remove tracked environment files immediately with `git rm --cached .env`.
- **Environment variables in code**: Never hardcode credentials in code files. Always read from environment or `.env`.

## Verification Steps

- Run the secret scan command. If no keys are printed, staging is safe.

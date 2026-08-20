# AGY Golden Thread remediation: Linear auth/routing and local secret hygiene (2026-07-18)

Use this when Michael replies to an `AGY Golden Thread Project Review` digest and asks Fred to execute fixes or route them to owners.

## What changed in this session

The cron delivery only showed headings, but the durable output contained concrete rows under:

```text
~/.hermes/profiles/orchestrator/cron/output/0db3cc8a9c40/YYYY-MM-DD_HH-MM-SS.md
```

The actionable rows were:

- missing/stale `RESULT.md` diagnostics on existing Linear issues;
- paused AGY/Ned orchestrations that needed `/approve` plus stricter exit criteria;
- one local credential/config hygiene finding;
- one dirty owner-lane workspace that needed Ned routing rather than Fred committing it.

## Linear API lessons

1. **Do not add `Bearer ` to a Linear API key.**
   - Linear returned: `It looks like you're trying to use an API key as a Bearer token. Remove the Bearer prefix from the Authorization header.`
   - Use the raw `LINEAR_API_KEY` value in the `Authorization` header.
   - Only OAuth tokens should use `Bearer <token>`.

2. **Prefer validated multiline GraphQL for nested fields.**
   - Compact one-line queries with nested `labels { nodes { ... } }` are easy to brace incorrectly and can return GraphQL syntax errors.
   - Use clear multiline queries and test a one-issue lookup before batch mutation.

3. **Issue labels may be workspace-global, not team-local.**
   - `teams { labels { ... } }` did not surface labels like `agent:agy` even though issues already had them.
   - Use `issueLabels(first: 250)` to find global label IDs before mutation.

4. **`issueSearch(term:)` may not exist in the active schema.**
   - If search upsert fails with `Unknown argument "term" on field "Query.issueSearch"`, do not keep retrying.
   - Use exact issue-number lookups when known, or create a bounded new owner-routed issue if duplicate risk is acceptable and documented.

## Remediation pattern

1. Recover full cron rows; never mutate from Telegram headings alone.
2. Live-check every cited Linear issue.
3. For stale missing-`RESULT.md` rows where the issue is already AGY-routed, post an audit comment with:
   - what to verify first;
   - requirement to write `RESULT.md` or an equivalent evidence packet;
   - explicit “no Done without evidence.”
4. For paused orchestrations, posting `/approve` is acceptable when Michael asks Fred to execute solutions, but include the evidence/exit-criterion comment in the same action.
5. If a backlog issue is not routed, move it to `Todo` and apply `agent:agy`, `dispatch:ready`, and the appropriate consumability/model label.
6. If a completed issue still has `dispatch:ready`, remove the stale dispatch label and keep `agent:done`.
7. If a dirty worktree is in another owner’s branch/lane, do not commit over it. Create a new owner-routed Linear closeout issue with the diff summary and exit criterion.

## Local secret/config hygiene pattern

When a local AGY/Hermes scratch config contains a plaintext provider key field:

1. Do not print the key value.
2. Replace the provider-specific plaintext field with an env-var reference, e.g. `api_key_env: GEMINI_API_KEY`.
3. Verify common secret prefixes are absent from the resulting file.
4. If you create a plaintext backup during editing, remove it before final verification. A backup containing the old secret is not an acceptable final state.
5. State the boundary clearly: local plaintext exposure was fixed; external key rotation/revocation was **not** completed unless you actually performed it in the provider dashboard/API.

## Verification checklist

Use a focused `/tmp/hermes-verify-*` script and report it as ad hoc targeted verification:

```text
gemini_plaintext_api_key_removed=true
gemini_api_key_env=GEMINI_API_KEY
plaintext_backup_removed=true
linear_source_issues_commented=<count>
owner_routing_issue=<identifier>
stale_dispatch_ready_removed=true
credentialized_github_remotes_under_work=0
NOT_CLAIMING=external key rotation completed
AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite green
```

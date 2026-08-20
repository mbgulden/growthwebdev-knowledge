# Verification nudges: changed-path artifact checks and secret-marker hygiene (2026-07-18)

## Context
A Golden Thread run changed two Markdown artifacts:

- `/home/ubuntu/work/hd-platform/docs/becca-transit-feedback-packet.md`
- `/home/ubuntu/work/okf/operations/2026-07-18-hd-engine-core-golden-thread.md`

The post-turn verifier nudged twice even after `npm run build` passed. The durable fix was a focused `/tmp/hermes-verify-*` verifier against the exact changed paths, reported explicitly as **ad-hoc targeted verification, not suite green**.

## Durable workflow lesson
When a verification nudge names changed Markdown/report paths:

1. Run the requested canonical command if one is named, e.g. `npm run build`.
2. Also create a temporary verifier with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`.
3. Verify the exact changed paths named by the nudge, not a generic final-response shape.
4. Check the artifact contract:
   - required sections exist,
   - Linear IDs are present,
   - rubric terms exist (`Unit`, `Integration`, `Revenue`, `Assumption`),
   - guardrails are present,
   - no placeholders such as `TODO`, `TBD`, `{{`, `}}`,
   - no secret/token prefixes.
5. Remove the temp verifier in the same command and include the removed path in the report.
6. Report the result as **ad-hoc targeted verification, not suite green**.

## Secret-marker pitfall
Do not include credential prefixes in Markdown artifacts even as placeholders or examples. A string like `sk_live_REPLACE` or `sk_test_REDACTED` can be detected as a secret prefix and keep verification failing.

Use neutral wording instead:

- Good: `Stripe credentials are unset or redacted`.
- Good: `placeholder credentials`.
- Avoid: any literal provider-key prefix followed by placeholder text.

## Example verifier checks
For Markdown/report artifacts, a focused verifier can check:

```python
secret_markers = ['sk_live_', 'sk_test_', 'ghp_', 'xoxb-', 'AIza', 'LINEAR_API_KEY=']
placeholder_markers = ['TODO', 'TBD', '{{', '}}']
required_terms = ['Selected Project', 'Assumption Challenges', 'Strategy Comparison', 'Linear Tasks Created', 'AGY Execution Result']
```

Keep the verifier scoped to the named changed paths and avoid claiming broader repository health unless a canonical suite was actually run.

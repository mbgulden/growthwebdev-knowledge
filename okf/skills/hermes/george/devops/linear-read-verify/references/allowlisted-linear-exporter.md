# Allowlisted Linear exporter pattern

Use when Prismatic coordination needs more than the default `linear_read_verify.py` metadata broker exposes (for example: parent descriptions, bounded children, labels, relations, or dependency dedupe review) while preserving a read-only/no-arbitrary-GraphQL boundary.

## Pattern

- Build a separate exporter script under George's profile, not by expanding the default metadata broker into arbitrary GraphQL.
- Hardcode an allowlist of approved parent identifiers for the current bounded review slice.
- Use a named GraphQL `query`, never a `mutation`; verify the query text contains no mutation before live use.
- Request bounded connection sizes explicitly (`children(first: N)`, `labels(first: N)`, `relations(first: N)`, inverse relations where needed).
- Fail closed on `pageInfo.hasNextPage=true` or returned node counts above the expected bound; do not silently truncate over-limit arrays.
- Redact before truncation, not after truncation. Cover named secrets (`api_key`, `token`, `secret`, `password`), bearer values, JWT-like values, common API prefixes (`sk-`, `lin_api_`, GitHub tokens, Slack tokens), AWS access IDs, URLs/titles/descriptions/labels/state names, and private-key blocks.
- Strip the exact loaded credential from the **raw bounded response object before normalization/field truncation**, then repeat exact-credential stripping after normalization as defense in depth. A post-normalization-only pass can leak a meaningful credential prefix when a raw credential crosses `MAX_DESCRIPTION_CHARS` or another truncation boundary.
- Secret-key redaction must handle quoted keys as well as quoted values, including JSON/Python/backtick forms such as `{"token":"..."}`, `{'password': '...'}`, `` `api_key`=`...` ``, and `"AWS_SECRET_ACCESS_KEY"="..."`. Regexes that only allow quotes before the value can still leak JSON-formatted credentials in descriptions.
- Build the HTTP client with redirects disabled. Python `urllib.request` follows HTTP redirects by default and can carry `Authorization` into the redirected request, including cross-origin redirects. Use a rejecting `HTTPRedirectHandler`/opener path and fail before constructing any follow-up request; do not rely on checking the final URL after the request completes.
- CLI/public errors should be generic. Never print exception text that may include headers, credential material, transport details, redirect targets, or user-supplied secret-like data.
- Keep `read_only: true` and an `allowlist` in output for proof review.

## Local adversarial test cases

Before live use, add mocked unit tests for:

- allowlist rejection;
- query contains no mutation;
- normal child/relation normalization;
- child pagination fail-closed;
- relation pagination fail-closed;
- label pagination or >limit fail-closed;
- malformed over-limit child/relation arrays fail-closed;
- oversized HTTP response fail-closed;
- redaction before truncation near the output boundary;
- exact loaded credential removal from the raw bounded response before truncation, including an unpatterned credential crossing `MAX_DESCRIPTION_CHARS` where both the full value and a meaningful prefix must be absent;
- common token formats, private-key block redaction, and quoted-key credential forms (`{"token":"..."}`, `{'password': '...'}`, backtick keys, quoted AWS secret keys);
- exact loaded credential removal from normalized output even when the credential appears standalone without a key label;
- redirect rejection using a mocked opener/handler path; assert the rejected redirect does not produce a follow-up request and public CLI output remains generic;
- main/CLI failure path does not emit exception text or credential-like strings.

## Proof packet fields

```text
PY_COMPILE=<PASS|FAIL>
UNIT_TESTS=<N passed|FAIL>
SCRIPT_SHA256=<sha256>
TEST_SHA256=<sha256>
LOG=<path under /tmp or profile reports>
LOG_SHA256=<sha256>
LIVE_LINEAR_USE=<true|false>
LINEAR_MUTATED=false
INDEPENDENT_REVIEW=<CLEAN|BLOCKED|pending>
```

## Boundary

This pattern supports bounded read/export review only. It is not approval for Linear writes, state changes, comments, or deployment. If a live credential query is needed, first get local tests green and independent CLEAN review of the exact script/test hashes.
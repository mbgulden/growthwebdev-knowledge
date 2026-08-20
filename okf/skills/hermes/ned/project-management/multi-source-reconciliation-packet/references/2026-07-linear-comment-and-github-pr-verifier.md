---
type: Reference
title: Linear comment-listing and per-PR verifier patterns
description: Pitfalls hit while verifying Linear `commentCreate` results, body-prefix matching across an issue's full comment history, and the public GitHub REST read pattern for PR state when `gh` auth is missing.
tags: [linear, github, verification, commentCreate, commentUpdate, urllib]
timestamp: 2026-07-28T02:15:00Z
source_session: HDE reconciliation packet items 5/6 (2026-07-28)
related_skills: [linear-api-operations, multi-source-reconciliation-packet, ad-hoc-verification-contracts]
---

# Linear comment-listing and per-PR verifier patterns

## Symptom

A `/tmp/hermes-verify-*` verifier reports `FAIL: PR-batch comment missing PRs: 19,23,24,...` or `GRO-4004: reopen comment missing`, even though the comment was successfully created and is visible in Linear. Concurrently, a `commentUpdate` mutation that worked when written with `input` only now returns `Field commentUpdate argument "id" of type String! is required`.

## Cause

Two independent pitfalls:

1. **Comment-listing depth.** Linear's `comments(last: N)` returns only the N most recent comments. If the issue already had >N comments from prior work, a newly created comment may not appear in the result. The single most common false-negative in Linear-state verifiers.

2. **The `commentUpdate` vs `commentCreate` asymmetry.** `commentCreate` takes only `input: CommentCreateInput!`. `commentUpdate` takes BOTH `id: String!` AND `input: CommentUpdateInput!`. They look like the same pattern; they are not.

## Resilient patterns

### Comment listing

```python
q = """query($id:String!){
  issue(id:$id){
    comments(last: 50){
      nodes { id body createdAt user { name } }
    }
  }
}"""

# Pick the comment you actually care about by exact body prefix
target = None
for c in comments:
    if (c['body'] or '').startswith('PR-batch close:'):
        target = c
        break

assert target is not None, "expected PR-batch close comment by exact body prefix"
```

Use `last: 50` for any verification that asserts "did this comment land?", plus `startswith` filtering. Substring match (`'PR-batch close' in body`) is unreliable when older comments mention the same phrase.

### commentUpdate with id + input

```python
mutation = """mutation($id:String!, $input: CommentUpdateInput!) {
  commentUpdate(id: $id, input: $input) { success }
}"""

requests.post(
    'https://api.linear.app/graphql',
    headers=headers,
    json={
        'query': mutation,
        'variables': {
            'id': 'bf3b5e06-d6a3-4fa1-b07e-420b9b6faf3a',
            'input': {'body': new_body},
        },
    },
    timeout=30,
)
```

`input` does NOT contain `id`. The mutation signature is `commentUpdate(id: String!, input: CommentUpdateInput!)` and Linear returns `Field commentUpdate argument "id" of type String! is required, but it was not provided.` if you put `id` inside `input`.

## Public GitHub REST read for PR verification

When `gh` auth is missing but the verifier must confirm PR state (for example, "are these 11 candidate PRs still open?"):

```python
import urllib.request, json
url = 'https://api.github.com/repos/mbgulden/hd-platform/pulls?state=open&per_page=100'
req = urllib.request.Request(url, headers={
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'Ned-Verify',  # GitHub API requires a User-Agent header
})
prs = json.loads(urllib.request.urlopen(req, timeout=30).read())
open_nums = {p['number'] for p in prs}
candidates = [19, 23, 24, 28, 29, 34, 35, 36, 37, 38, 39, 41]
assert all(n in open_nums for n in candidates), "candidate PRs no longer open"
```

Stdlib-only, works inside `execute_code` and `terminal`, requires no auth for public read. The `User-Agent` header is mandatory; GitHub's API rejects requests without it.

## Verification

For each verifier that asserts Linear or GitHub state:

1. After `commentCreate`, fetch the issue's `comments(last: 50)` and assert the new comment appears by `id` or exact `startswith(body)` — not by substring match.
2. After `commentUpdate`, fetch the comment by `id` and assert the new body length or content substring matches.
3. After enumerating GitHub PRs, compare the returned `set(p['number'] for p in prs)` against your candidate set; assert subset/superset as appropriate.
# Linear Markdown Canonicalization Notes

Use this when Prismatic Linear packet writers/recovery scripts compare submitted Markdown with Linear's stored description/body text.

## Observed durable behavior

Linear may rewrite harmless Markdown list syntax during storage. Known forms observed during executable packet/recovery work:

- Line-leading unordered list markers submitted as `- item` may be stored as `* item`.
- If a contiguous list starts immediately after a non-list paragraph/header line, Linear may insert one blank line before the first stored `* item`.
- Child/parent projection fields can expose the canonicalized stored form, so both direct issue verification and read-only parent/child projection guards must use the same expected stored form.

## Safe modeling pattern

Do not weaken description verification to a loose contains/normalized-whitespace check. Instead:

1. Keep the frozen raw payload unchanged and hash-bound.
2. Build a deterministic `expected_stored_description` from the frozen raw payload for known Linear canonicalizations only.
3. Prefer submitting the deterministic fixed-point canonical form as the mutation input when Linear has already proven it rewrites the raw form; this prevents repeated post-mutation drift failures while preserving raw-payload immutability.
4. Compare live Linear snapshots to the exact canonical expected stored form, ignoring only fields explicitly allowed by the operation such as `updatedAt`.
5. Use the same canonicalized expected description anywhere the edited issue is embedded as a projection in parent/child snapshots.
6. Record raw-vs-submitted/canonical hashes in dry-run and final receipts so reviewers can distinguish frozen source content from Linear-safe mutation input.
7. Prove the canonicalizer is idempotent over every packet payload before seeking execution authorization.
8. After a failed authorized execution and bounded recovery, freeze a fresh retry baseline from the recovered live state and hash-bind it to the recovery receipt before preparing the next retry.

## Minimal canonicalizer shape

```python
import re

def linear_expected_markdown(value: str) -> str:
    out = []
    for line in value.splitlines(keepends=True):
        match = re.match(r'^(\s*)- (.*)$', line.rstrip('\n'))
        if match:
            previous = out[-1].rstrip('\n') if out else ''
            if previous and not re.match(r'^\s*[\-*] ', previous):
                out.append('\n')
            line = f'{match.group(1)}* {match.group(2)}' + ('\n' if line.endswith('\n') else '')
        out.append(line)
    return ''.join(out)
```

When retrying a packet after Linear has proven it stores the canonical form, use this helper as both:

- the exact expected stored description; and
- the submitted mutation description, while still hashing and preserving the frozen raw bundle separately.

Add an idempotence check over every packet description:

```python
assert linear_expected_markdown(linear_expected_markdown(description)) == linear_expected_markdown(description)
```

This is an exact postcondition helper and Linear-safe submission helper for known rewrites, not a license to accept arbitrary Markdown drift.

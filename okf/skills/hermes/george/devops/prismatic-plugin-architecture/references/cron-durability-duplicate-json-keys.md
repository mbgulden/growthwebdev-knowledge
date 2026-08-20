# Cron durability duplicate-key hardening

Use this reference for Prismatic plugins that inspect Hermes `cron/jobs.json` or private cron snapshot envelopes.

## Durable lesson

Python's normal `json.loads()` silently keeps the last value for duplicate object keys. For a scheduler authority file, that can make the object a plugin validates differ from the bytes an operator or auditor sees. A cron durability plugin must reject duplicate keys before normal schema validation.

## Required coverage

Reject duplicate keys at all JSON object depths:

- authority root, e.g. duplicate `jobs`;
- each job object, e.g. duplicate `id`/`enabled`;
- nested schedule/config objects;
- private snapshot/envelope metadata;
- escaped or Unicode-equivalent key collisions, e.g. `"id"` and `"\u0069d"`.

Do not reflect the duplicate key value in public findings or exceptions that may reach chat/Linear; report a stable generic error or hashed identifier only.

## Implementation pattern

Use `object_pairs_hook` rather than post-parse checks:

```python
def reject_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON object key")
        out[key] = value
    return out

obj = json.loads(raw_text, object_pairs_hook=reject_duplicate_keys)
```

Because `object_pairs_hook` runs for nested objects too, it catches nested schedule/config and envelope duplicates before they collapse. Still keep explicit raw-text fixture tests for every level so future refactors cannot accidentally revert to ordinary `json.loads()`.

## Verification

Add raw JSON fixture tests instead of constructing Python dictionaries, because Python literals cannot preserve duplicate keys. Include an escaped-key fixture such as `{"id":"one","\\u0069d":"two"}` to prove decoded key collisions fail closed.

# Machine-readable packet boundary proof

Use this pattern when a Prismatic evidence/review packet is itself the artifact under verification: admission envelopes, classification matrices, precontracts, handoffs, or state-reconciliation packets.

## Session-derived trigger

A packet verifier failed even though the packet was directionally correct because the verifier expected machine-readable fields that were only present as prose or human formatting:

- active sequence was written with Unicode arrows instead of a stable `KEY=value` field;
- close/event authority was expressed as prose (`not authorized`) rather than a parseable boolean;
- a verifier tried to bind exact authorization-marker display text, which can be masked in logs/UI.

## Correct pattern

1. Add a final packet boundary block before hashing:

```text
ACTIVE_SEQUENCE=GRO-4275->GRO-4271->GRO-4273->GRO-4336->GRO-4337
PARENT_CLOSE_AUTHORIZED=false
LINEAR_WRITE_COUNT=0
NOT_CLAIMING=<comma_or_semicolon_safe_nonclaims>
MARKER=<stable_marker>
```

2. Have the verifier parse `KEY=value` lines into a dictionary, then assert values semantically:

```python
kv = {}
for line in text.splitlines():
    if "=" in line and not line.startswith("-"):
        key, value = line.split("=", 1)
        kv[key] = value
assert kv["LINEAR_WRITE_COUNT"] == "0"
assert kv["PARENT_CLOSE_AUTHORIZED"] == "false"
assert kv["ACTIVE_SEQUENCE"].split("->") == expected_sequence
```

3. Print neutral proof labels instead of exact sensitive/authority marker strings:

```text
LINEAR_WRITE_COUNT=0
PARENT_CLOSE_AUTHORITY=ABSENT
EVENT_BOUNDARY=PASS
```

4. Hash both the packet and the proof log after the final packet edit. If the verifier reveals a missing boundary field and you patch the packet, rerun the verifier and report the new packet hash.

## Boundary

This is not a substitute for canonical test-suite proof. Label it `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the repository’s canonical suite actually ran and passed.

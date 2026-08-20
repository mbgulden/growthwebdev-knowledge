# Authority contract trust roots

Use this reference when a Prismatic failed-producer recovery contract repairs registry, identity, idempotency, or authority-boundary defects.

## Lesson captured

A repair contract that says "trusted authority" or "trusted registry" is still under-specified unless it names the exact authority object and proves how a runner obtains immutable bytes from it. Future reviewers should block abstract trust-root language before any task-file or recovery event is prepared.

## Minimum concrete authority fields

A sufficient authority contract should define, in the artifact itself:

```text
SOURCE_ID=<stable normative identifier>
STORAGE_OBJECT=<exact table/file/service object>
SCHEMA_ID=<stable schema identifier>
SCHEMA_VERSION=<non-boolean integer/version>
RETRIEVAL_INTERFACE=<exact read API and accepted parameters>
INSTALL_INTERFACE=<trusted loader API, if writes/install are allowed>
DIGEST_ALGORITHM=<algorithm>
DIGEST_DOMAIN=<domain separation bytes/string>
MAX_CANONICAL_BYTES=<hard cap>
```

## Storage-object pinning

For local SQLite/file authorities, require:

- canonical configured absolute path;
- no symlinked component;
- device/inode/object-type pinning;
- owner and mode evidence (`0600` or stricter for private authority DBs);
- parent-chain no-group/world-write evidence;
- same pinned object/connection across claim, immediate decision, and finalization;
- explicit rejection of copied DBs, attached DBs, TEMP objects, alternate schemas, caller-selected paths, and reopened replacements.

## Canonical bytes and digest rules

The contract should spell out canonical serialization and rejection rules rather than saying "canonical JSON" generically. Include:

- exact encoder options (`sort_keys`, separators, UTF-8, NaN policy, Unicode policy);
- exact top-level keys and nested object schemas;
- duplicate-key, unknown-field, missing-field, float, invalid integer/boolean, invalid Unicode, control-character, and size rejection;
- byte-for-byte re-encoding equality;
- lowercase digest form plus digest recomputation before insert/retrieval/finalization;
- collision handling for same key/different bytes and same digest/different bytes.

## Provenance boundary

State who may install authority rows and who may only retrieve them. Runner/claim/renew/finalize paths should generally accept only lookup identity, for example:

```text
source_id + registry_generation + snapshot_digest
```

They should reject caller-supplied bytes, reconstructed mappings, alternate source IDs, and path-derived authority. The trusted install path must run transactionally and share the same canonical-byte/digest validators as retrieval.

## Equality checks

Persist the exact authority tuple atomically with the claim and compare it byte-for-byte at every boundary that can affect external behavior:

1. claim;
2. immediate pre-spawn decision;
3. receipt/finalization.

For pre-invocation mismatches, require durable fail-closed/quarantine with zero adapter calls. For post-invocation mismatches, forbid successful finalization.

## Artifact-version discipline

If independent review blocks a frozen authority contract:

1. preserve the blocked version byte-for-byte;
2. record the blocker and review id;
3. create a new `Vn+1` artifact with a new marker/hash;
4. dispatch fresh exact-artifact review;
5. keep event counts and task-file existence checks at zero until explicit authorization.

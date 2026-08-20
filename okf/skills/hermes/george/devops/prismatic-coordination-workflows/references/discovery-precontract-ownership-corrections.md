# Discovery/precontract ownership corrections

Use this when a Prismatic discovery or precontract artifact is reviewed and found incomplete, especially for ownership/finalization/integrity-boundary claims.

## Pattern

1. Preserve the blocked artifact exactly.
   - Keep original path, SHA, review handle, and blocker.
   - Do not silently edit in place or erase the failed review trail.
2. Produce a new versioned artifact (`V2`, `V3`, etc.) with the minimum correction.
   - Keep the prior decision if still valid, but correct the implementation inventory.
   - State which claims changed and which did not.
3. Verify from implementation evidence, not prose.
   - Prefer AST/source probes that count constructors/calls/paths.
   - Bind exact commit/tree/worktree cleanliness and artifact SHA.
   - For SQL ownership, check actual table names and transaction boundaries from source before writing verifier assertions.
4. Keep authority flags false unless Michael explicitly authorizes a launch/mutation.
   - `KEY_CREATION_AUTHORIZED=false`
   - `SOURCE_MUTATION_AUTHORIZED=false`
   - `EVENT_POST_AUTHORIZED=false`
   - `PRODUCER_AUTHORIZED=false`
5. Dispatch a fresh independent review against the corrected exact bytes.
6. Record both states in handoff/hot state.
   - Blocked original remains blocked.
   - Corrected version is pending until review returns clean.

## Proof packet shape

```text
V1=<path>
V1_SHA256=<sha>
V1_REVIEW=<delegation>:BLOCKED
V1_DEFECT=<short exact blocker>
V2=<path>
V2_SHA256=<sha>
IMPLEMENTATION_EVIDENCE=<commit/tree/source paths>
STATIC_PROOF=<log path>
STATIC_PROOF_SHA256=<sha>
REVIEW=<delegation>:pending|CLEAN|BLOCKED
AUTHORITY_FLAGS=false
NOT_CLAIMING=<acceptance, dispatch readiness, mutation, event, producer, merge, deployment>
MARKER=<stable marker>
```

## Pitfalls

- Do not let a corrected verifier become another source of false confidence. If the verifier fails because it guessed table names or string spellings, inspect the actual source and rerun with exact implementation terms.
- Do not convert a discovery/precontract decision into dispatch readiness. Discovery clean and producer authorization are separate gates.
- Do not over-broaden the fix: correct the specific reviewed defect while preserving zero-authority boundaries.

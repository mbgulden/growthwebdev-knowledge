# Pure time contract authority

Use this reference when reviewing Prismatic task contracts that introduce schedule, cron, lease, expiration, catch-up, or projection APIs.

## Durable lesson

A function or decision path cannot be both:

- pure / deterministic / no wall-clock reads; and
- required to reject values as `future`, `stale`, `expired`, or relative to `now`

unless the contract supplies a concrete time authority such as:

1. an explicit `reference_utc` / `as_of_utc` argument;
2. a persisted database authority row bound by schema/digest; or
3. a clearly named runtime authority source with tests proving how it is read and frozen.

Without that authority, words like `future` have no deterministic meaning. A reviewer should block the contract rather than let implementers invent a hidden wall-clock read or inconsistent local definition.

## Minimum artifact-only correction patterns

Choose one:

### A. Add explicit authority

- Add `reference_utc` / `as_of_utc` to the API or identify the persisted authority row.
- Define strict RFC3339 UTC parsing and timezone behavior.
- Require tests proving values before/equal/after the reference boundary.
- Require tests proving no undeclared wall-clock source is read.

### B. Remove wall-clock-relative rejection

- Replace `reject malformed/future/reversed inputs` with `reject malformed/reversed inputs`.
- State that valid timestamps are not rejected merely because they are before or after the actual current date.
- Require tests using timestamps on both sides of the real current date and proving identical deterministic behavior without a clock read.

## Review recipe

When reviewing an exact-head contract:

```text
1. Search the artifact for: future, stale, expired, current, now, wall-clock, clock, reference, as_of, after, through.
2. For each relative-time word, identify the exact authority source.
3. If the API claims purity/no wall-clock, verify every relative-time rule is parameterized or persisted.
4. If not, return BLOCKED with the first ambiguous temporal requirement and the minimum artifact-only correction.
```

## Proof boundary

This is a contract-review rule. It does not prove the eventual implementation is correct; after implementation, still require exact-head reproduction and tests that exercise the real decision path.

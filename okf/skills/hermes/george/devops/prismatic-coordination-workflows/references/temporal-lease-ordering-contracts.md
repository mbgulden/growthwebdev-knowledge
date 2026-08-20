# Temporal lease ordering in Prismatic contracts

## Trigger

Use this reference when freezing or reviewing Prismatic contracts that make authority decisions from timestamps, especially leases, stale-runner finalization, reconciliation sweeps, receipt terminalization, or `LIMIT`-bounded selection of expired rows.

## Durable lesson

If the system accepts UTC `Z` timestamps with zero through six fractional digits, raw timestamp text is not a safe ordering or equality substrate.

Examples that can break lexical assumptions:

```text
2026-07-31T00:00:00.1Z
2026-07-31T00:00:00.100000Z
```

Those represent the same instant, but byte/text comparison may treat them differently. Similar hazards exist for no-fraction versus fractional forms and for different fractional widths.

## Contract requirements

A Prismatic authority contract should require:

1. Validate timestamp strings with the existing strict UTC grammar.
2. Parse both lease and reference values into aware UTC instants.
3. Convert to deterministic integer epoch microseconds for comparisons.
4. Treat equality as expired for lease-authority checks unless the product contract explicitly says otherwise.
5. For SQLite selection/order before `LIMIT`, use a deterministic connection-local scalar backed by the strict parser, e.g. `prismatic_utc_micros(value)`.
6. Fail closed on invalid stored timestamps; do not silently skip or coerce them.
7. Forbid raw Python/SQLite timestamp-text comparison for authority decisions.
8. Forbid SQLite `julianday`/`strftime` authority comparisons when microsecond precision and accepted textual forms matter.
9. In CAS updates, bind the exact original timestamp text as identity while separately rechecking the parsed instant predicate.
10. Add tests for no-fraction, mixed fractional width, equivalent instants such as `.1Z` vs `.100000Z`, stale/equal leases, and SQLite ordering before `LIMIT`.

## Review checklist

When reviewing a candidate or precontract, ask:

- Does any `WHERE`, `ORDER BY`, Python branch, or finalization guard compare timestamp strings directly?
- Is the ordering performed before `LIMIT`, or is the code limiting first and sorting/parsing later?
- Does CAS prove the row is the same row selected, including exact old lease text, while also proving the parsed lease remains expired?
- Are invalid timestamps handled as fail-closed transaction aborts rather than best-effort omissions?
- Do tests exercise textually different but instant-equivalent UTC strings?

## Non-claims

This reference does not require a schema migration by itself. It is a contract/review rule for authority-bearing temporal decisions. If a future implementation chooses to store normalized microseconds, that choice needs its own migration contract and durability proof.

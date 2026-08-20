# Production authority initialization amendment pattern

Use this when a reviewed Prismatic release/activation contract reaches production prestate and discovers that the live DB is missing an additive schema prerequisite, while the current contract forbids production DB writes.

## Trigger

- PR/merge/release staging already passed exact-head and immutable-release gates.
- Production access is still read-only.
- A read-only/query-only DB prestate proves the target database exists but lacks the accepted additive schema.
- The current contract does not authorize migration or initialization.

## Required response

1. **Stop activation immediately.** Do not reinterpret a read-only contract as implicit migration permission.
2. **Freeze a narrow amendment contract** before any DB mutation. Bind the already-completed merge/release/staging facts and the read-only discovery.
3. **Authorize exactly the missing additive initialization**, not a general DB-write window:
   - bound installed source/module hash from the immutable venv;
   - exact DB pathname;
   - one initialization call plus one idempotence call;
   - no arbitrary SQL, no payload/secret output, no producer/consumer enablement.
4. **Online backup gate before mutation:**
   - prove live DB path is regular and non-symlink;
   - create backup through SQLite online backup API from a read-only source connection;
   - publish backup no-clobber with mode `0600`;
   - fsync backup and receipt directory;
   - verify backup read-only/query-only with `integrity_check == ok`;
   - record backup SHA/size/inode;
   - never automatically restore the backup.
5. **Freeze pre-migration logical projection** with a read-only/query-only transaction:
   - all pre-existing `sqlite_master` rows;
   - all pre-existing table names and row counts;
   - absence of the additive schema objects;
   - FK/integrity checks;
   - no row values/payloads.
6. **After initialization:**
   - require exact schema version and complete expected additive object set;
   - require all pre-existing `sqlite_master` rows unchanged;
   - require all pre-existing table row counts unchanged;
   - require new additive tables empty unless the contract explicitly says otherwise;
   - require FK/integrity checks;
   - run the migration/init a second time and require byte-for-byte projection equality;
   - run the accepted live projection API twice and require equal empty/default projections;
   - prove separate `mode=ro` + `PRAGMA query_only=ON` write rejection.
7. **Rollback boundary:** additive schema remains durable production state unless a separate reviewed restore contract authorizes reversal. Gateway rollback must not delete or reverse it automatically; older gateway builds should ignore the new tables.
8. **Same-UID writer exclusion must be mandatory, not observational:**
   - stopping known units plus `lsof`/process checks is useful discovery but cannot exclude detached, delayed, or newly spawned same-UID writers;
   - pin a root-trusted ancestor (for example `/home`) and descriptor-open every mutable namespace component down to the DB with `openat2(RESOLVE_BENEATH|RESOLVE_NO_MAGICLINKS|RESOLVE_NO_SYMLINKS)`;
   - retain every FD for the complete backup/migration/proof lifetime and reprove canonical path device/inode identity plus DB regular/link-count-one after acquisition and before restoration;
   - for each initially user-owned component, journal original metadata **before first mutation**, then apply `fchmod(000) -> fchown(0,0) -> fchmod(final restrictive mode)` and immediately validate exact UID/GID/type/mode/device/inode; applying final mode only before `fchown` leaves an old-owner `fchmod(0777)` race;
   - fence the complete parent chain that can rename the DB directory, not only the DB directory itself; otherwise lazy SQLite WAL/SHM opens can be redirected even when the main connection is inode-bound;
   - restore child-to-parent, with the highest mutable ancestor restored last; partial failures restore the pre-mutation journal in reverse order.
9. **Bind SQLite and executable artifacts:**
   - open SQLite only after the complete namespace fence is acquired;
   - use one retained connection object for `Connection.backup`, both migration calls, schema/count/idempotence checks, and query-only write rejection;
   - copy pure-stdlib migration source and any publication helper into an exact root-protected deployment directory, hash-check before/after import or invocation, and stage the supervisor itself as a root-owned no-clobber exact-hash copy before execution;
   - keep detailed receipts and the backup in the root-owned mode-`0700` deployment directory with mode-`0600` files.
10. **Adversarial proof before production:** run a same-UID process holding preexisting FDs that continuously attempts both `fchmod(0777)` and namespace rename/replacement from acquisition through an explicit SQLite-close/fence-still-active boundary. Accept only: (a) migration on the original inode with final restrictive modes, or (b) pre-migration fail-closed with no schema/WAL write to original or replacement.
11. **Fresh-schema expected rows:** distinguish metadata from data. For cron authority v3, `cron_authority_schema_version` must contain exactly one `(authority_id=1, schema_version=3)` row while the eight authority data tables and six public projection families are empty.
12. **Independent review before mutation:** dispatch at least one full contract review and one focused DB/adversarial review. Do not mutate production while reviews are pending.

## Reporting marker

```text
PRODUCTION_READ_ONLY_PRESTATE=true
PRODUCTION_DB_MUTATION=false
SCHEMA_PREREQ_MISSING=true
AMENDMENT_REVIEW_PENDING=true
SYSTEMD_DROPIN_PUBLISHED=false
GATEWAY_RESTARTED=false
```

## Pitfall

A successful merge and immutable staging proof does not grant new production DB-write authority. If prestate reveals an initialization gap, the right move is a reviewed, bounded amendment — not an improvised migration and not a false activation claim.

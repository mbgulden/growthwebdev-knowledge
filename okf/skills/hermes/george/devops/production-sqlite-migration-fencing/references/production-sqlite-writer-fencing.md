# Session-derived checklist: production SQLite writer fencing

This reference captures reusable lessons from Prismatic production authority-init contract reviews. It is intentionally class-level: use it for any production SQLite migration where same-user or short-lived writers may reach the DB/WAL/SHM path.

## What failed review

A contract that stopped a fixed list of systemd units and then checked `lsof`/`fuser` still failed concurrency review because the exclusion was observational. An unlisted/manual/cron/detached process could open the SQLite DB after the point-in-time check.

A second issue was unconditional gateway restoration: if the old gateway was not preconditioned as active/running, “restore/start old gateway” contradicted “never restore a unit that was not active before quiescence.”

A third issue was a pathname-based fence contract. A sequence such as `stat/lstat -> chmod/chown path -> re-stat path` cannot prove the same object remained targeted across every step. Even if the shell contract names exact paths, a privileged deployment contract should not rely on caller-side pathname operations for the security boundary.

A fourth issue was pinning the directory and DB FDs but letting SQLite operations reopen the canonical pathname after the parent directory could be renamed. FD pinning proves what the supervisor holds; it does not automatically bind `sqlite3.connect(path)`, `Connection.backup` source selection, migration helpers, or public projection readers if they take a path.

A fifth issue was fencing only the leaf bus directory while leaving a writable ancestor (for Prismatic, `/home/ubuntu/.prismatic`) unfenced. Same-UID code could rename/replace `bus` during the fence window; SQLite WAL/SHM creation or any path-taking helper could then write into the replacement tree even though the original bus/DB FDs stayed pinned.

A sixth issue was executing or importing mutable profile/venv/worktree paths under root. The supervisor itself and any pure-stdlib project module/drop-in helper it uses must be copied into a root-protected deployment area or `/root`, hash-bound, and verified before privileged execution/import/invocation.

## Durable correction

Use a mandatory OS fence owned by one reviewed privileged supervisor:

1. Require old gateway active/running if rollback always restarts it.
2. Stop known writers, but treat this only as risk reduction.
3. Snapshot directory/DB metadata and require DB regular, non-symlink, and link-count-one.
4. Pin a trusted root ancestor first. For Prismatic `/home` is acceptable only if root-owned and not group/other-writable.
5. Descriptor-open every path component from the trusted ancestor to the DB and deployment directory. Prefer constrained `openat2(RESOLVE_BENEATH|RESOLVE_NO_MAGICLINKS|RESOLVE_NO_SYMLINKS)` for untrusted components; use `O_DIRECTORY|O_NOFOLLOW` for directories and a fixed basename for the DB.
6. Revoke write/traversal from parent to child before SQLite opens. For each initially user-owned component, journal owner/group/mode/device/inode/link count before mutation, then perform `fchmod(000)`, `fchown(0,0)`, and only then `fchmod(final_restrictive_mode)`. Example final modes: `/home/ubuntu` `0555`, `.prismatic` `0555`, deployments `0555`, exact deployment dir root `0700`, bus `0500`, DB `0600`.
7. After each transfer, validate the complete canonical path/device/inode/link-count chain against the pinned descriptors. This order matters: setting a restrictive mode before `fchown` leaves a same-UID FD holder able to race `fchmod(0777)` before ownership changes.
8. After acquiring the fence, prove no DB/WAL/SHM handles remain. `lsof`/`fuser` is now only a surviving-handle check, not the fence.
8. Stage the supervisor into `/root` with no-clobber creation, mode `0600`, fsync, exact SHA verification, `python -B`, and no ambient `PYTHONPATH`. Do not execute mutable profile paths as root.
9. If importing project code, copy exact pure-stdlib modules into the now-root-protected deployment directory and hash-check before and after `importlib` loading. Copy and hash-check any drop-in helper before invocation.
10. Open exactly one SQLite connection only after the complete ancestor fence is acquired. Prove a SQLite-owned `/proc/self/fd` regular-file handle matches the pinned DB device/inode.
11. Pass the same retained connection into online backup, migration calls, direct schema/count/projection proof, idempotence proof, and `PRAGMA query_only` write-rejection checks. Do not call path-taking helpers during the fenced interval unless they are proven to reuse the bound connection.
12. Hold the trusted ancestor FDs, child FDs, deployment-dir FD, and retained connection through online backup, duplicate prestate, migration call 1, schema/projection/write-rejection proof, migration call 2/idempotence, no-clobber receipt publication, release drop-in publication, daemon reload, and loaded-unit provenance proof.
13. Immediately before restoration, close the retained SQLite connection, then repeat canonical-path/device/inode/link-count checks.
14. Restore DB and any safe regular link-count-one WAL/SHM metadata by FD; restore child directories before parents; restore the user/home traversal component last. Keep root-created receipt directories root-owned mode `0700` if they are deployment evidence.
15. The supervisor must never start services. The caller starts the new gateway only after supervisor PASS, or executes the reviewed rollback path on BLOCKED.
16. After writers resume, compare only the authority/migrated state, not whole-DB immutability.

## Disposable verification pattern

Before production mutation, exercise the supervisor on disposable SQLite DBs with root-path semantics, not only unprivileged test mode. Minimum cases:

```text
BOUND_SQLITE_CONNECTION=PASS
PINNED_INODE_MIGRATION=PASS
WAL_BACKUP=PASS
METADATA_RESTORATION=PASS
PREEXISTING_TABLE_PRESERVATION=PASS
BACKUP_AND_IDEMPOTENCE_RECEIPTS=PASS
HARDLINK_REJECTION=PASS
```

Add an adversarial parent-chain test before trusting WAL behavior:

```text
TRUSTED_ANCESTOR_CHAIN=PASS
BUS_RENAME_REJECTED=PASS
NO_REPLACEMENT_WAL_OR_DB_WRITE=PASS
CHILD_TO_PARENT_RESTORATION=PASS
ROOT_PROTECTED_DEPLOYMENT_RECEIPTS=PASS
```

The test should attempt same-UID rename/replace of the SQLite directory while the root supervisor holds the fence. It should verify the rename is rejected, no replacement DB/WAL/SHM appears, original data/schema updates land on the pinned DB inode, child-to-parent restoration matches original metadata, and root-created receipts remain unreadable/root-protected until deliberately inspected as root.

Also run same-UID adversaries through the explicit SQLite-close/fence-still-active boundary:

```text
CONTINUOUS_FCHMOD=PASS
FINAL_RESTRICTIVE_MODES=PASS
CONTINUOUS_RENAME=PASS
NO_REDIRECTED_DB_OR_WAL=PASS
```

The `fchmod` adversary should retain preexisting FDs on user-owned components and continuously attempt `fchmod(0777)` from the first ownership transfer until the supervisor signals SQLite has closed while the fence is still active. The rename adversary should continuously attempt bus rename/replacement; accepted outcomes are fenced migration on the original inode or pre-migration fail-closed with no schema/WAL write to either original or replacement DB.

Also verify syntax/lint/format of the supervisor, exact SHA binding in the contract, root bootstrap hash proof, module/helper copy hashes, and failure-path metadata restoration. Preserve logs under `/tmp/hermes-verify-*` or the task’s receipt directory and quote hashes in the proof packet.

## Wording to prefer

```text
lsof/fuser/repeated projections are evidence only; the mandatory writer exclusion is the pinned-FD root-only trusted-ancestor directory/DB fence.
```

```text
The security boundary lives inside one reviewed privileged supervisor staged into `/root`; caller-side pathname chmod/chown/stat sequences are not accepted as the fence.
```

```text
A leaf directory FD fence is not enough if a writable parent can rename/replace that leaf; pin and fence the complete ancestor chain from a trusted root.
```

```text
Post-activation proof compares authority schema/version/object/projection invariants only; unrelated event/log tables may advance after fence release.
```

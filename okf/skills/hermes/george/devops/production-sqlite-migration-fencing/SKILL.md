---
name: production-sqlite-migration-fencing
description: Plan, review, and verify production SQLite migrations that must exclude concurrent writers without overclaiming.
---

# Production SQLite Migration Fencing

## When to use

Use this for production SQLite mutations where services, timers, daemons, or manual processes may write to the same DB/WAL/SHM files. Especially relevant for Prismatic bus/event-log migrations and additive schema initialization.

## Core rule

Stopping known units and checking `lsof`/`fuser` is not writer exclusion. It is only observational evidence. A safe migration contract needs a mandatory fence that prevents unapproved writer access for the whole mutation interval.

## Required contract shape

1. **Name the rollback precondition.** If rollback says “restore/start the old gateway,” require that gateway to be initially `active/running`; otherwise make restart conditional on prior-active state.
2. **Stop known writers as risk reduction.** Stop timers first, then one-shot services, then long-lived services. Do not call this exclusive fencing.
3. **Snapshot reversible metadata.** Record owner, group, mode, device, inode, and link count for the bus directory and DB; require the DB is regular, non-symlink, and link-count-one.
4. **Acquire the fence inside one reviewed privileged supervisor.** Do not write a contract that relies on caller-side pathname `chmod/chown/stat` steps; pathname acquisition is TOCTOU-prone. The supervisor should pin the bus directory and DB with retained file descriptors, then perform descriptor-bound metadata changes (`fchmod`/`fchown`) and descriptor-relative DB access.
5. **Use constrained descriptor-relative opens.** Open the bus directory with `O_DIRECTORY|O_NOFOLLOW`; open the fixed DB basename with constrained `openat2` flags such as `RESOLVE_BENEATH|RESOLVE_NO_MAGICLINKS|RESOLVE_NO_SYMLINKS` when available. Require regular file, non-symlink, and link-count-one before migration.
6. **Fence semantics.** Revoke non-root traversal/write through the pinned descriptors: bus directory root-only traversal (e.g. `0500`) and DB root-only write access (e.g. `0600`). The exact mode/owner may vary, but the proof must be descriptor-bound and reversible.
6a. **Transfer ownership without a same-UID chmod race.** For every initially user-owned fenced component, record original metadata before the first mutation, then use the safe sequence `fchmod(000) -> fchown(0,0) -> fchmod(final_restrictive_mode)` and immediately validate exact uid/gid/type/mode/device/inode. If ownership is transferred after setting the final restrictive mode, a same-UID process holding an old FD may race `fchmod(0777)` before `fchown` lands.
7. **Prove no surviving handles after the fence.** `lsof`/`fuser` now verifies no pre-existing writer survived; it is not the fence itself.
8. **Run only the authorized migration executor.** Use reviewed root execution, bound release venv/interpreter, `python -B`, and no ambient `PYTHONPATH`. Prefer one supervisor invocation that owns backup, migration, validation, receipt publication, drop-in publication, daemon reload, and loaded-unit provenance proof.
9. **Fence the complete ancestor chain, not only the leaf directory.** If any parent of the SQLite directory remains user-writable, same-UID code can rename the parent/child and cause lazy WAL/SHM or path-taking helper writes to land in a replacement tree. Pin a trusted root ancestor (for Prismatic: `/home` must be root-owned and not group/other-writable), descriptor-open every component down to the DB and deployment directory, then revoke write/traversal from parent to child before SQLite opens. Revalidate the full device/inode/link-count chain before and after the fenced work.
10. **Bind SQLite itself, not only the pathname.** If the migration API accepts an existing `sqlite3.Connection`, open exactly one connection only after the complete ancestor fence is acquired, then prove a SQLite-owned `/proc/self/fd` regular-file handle matches the pinned DB device/inode. Repeat the proof after the fence. This prevents parent/directory substitution from redirecting SQLite backup/migration writes through a reopened canonical pathname.
11. **Hold pinned descriptors and the bound connection continuously.** Keep the trusted ancestor chain FDs, bus/DB FDs, deployment-dir FD, and retained SQLite connection through backup, migration call(s), idempotence checks, final preactivation logical proof, drop-in/helper proof, daemon reload, and loaded-unit provenance proof. Do not call `sqlite3.connect(db_path)`, path-based migration helpers, or public path-based projection APIs while the fence is held unless those APIs are independently proven to reuse the retained connection.
12. **Root-stage execution artifacts before privileged execution.** Do not execute a mutable profile/worktree script path as root. Copy the reviewed supervisor into `/root` using no-clobber creation, mode `0600`, fsync, exact SHA verification, and `python -B` with no ambient `PYTHONPATH`. If importing pure-stdlib project code, copy the exact module into the root-protected deployment directory and hash-check it before and after `importlib` loading. Hash-check any copied drop-in helper before invoking it.
13. **Restore from the same pinned descriptors.** After DB proof and drop-in proof, close the retained root SQLite connection, then immediately before restoration revalidate canonical path/device/inode/link-count against the pinned descriptors. Restore WAL/SHM metadata if present and safe, restore DB metadata by FD, restore child directories before parents, and restore the user/home traversal component last. Keep durable receipt directories root-owned if they contain root-created deployment evidence.
14. **Release only at activation boundary.** Verify no handles, restore metadata, then immediately start the gateway and run live proof.
15. **Compare only stable state after writers resume.** Once the fence is released, unrelated event/log tables may advance. Post-activation proof should compare the migrated schema/object/projection state, not claim whole-DB immutability.

## SQLite WAL/SHM pitfalls

- WAL mode can create transient `-wal` and `-shm` files even during read-only inspection.
- Snapshot/fence WAL/SHM after quiescence, not from stale earlier observations.
- If WAL/SHM exist at release, require regular non-symlink/link-count-one files and restore owner/mode deliberately.
- A read-only or diagnostic health check against an unfenced live SQLite DB must not claim a complete snapshot. Capture DB and WAL identities before and after inspection; if either appears, disappears, or changes identity/size/mtime during inspection, suppress page/freelist metrics and return a conservative warning with `snapshot_complete=false` rather than overclaiming.

## Rollback pitfalls

- `lstat -> hash -> unlink` is not atomic rollback proof. Prefer no-clobber override publication and avoid deletion-based rollback.
- Advisory locks are insufficient unless every writer path is proven to use the same lock.
- Never restore/start a unit that was inactive before quiescence unless the contract explicitly preconditioned that unit as active/running.

## Proof packet fields

```text
WRITER_EXCLUSION=pinned-FD root-only trusted-ancestor/directory/DB fence
SQLITE_BINDING=single retained sqlite3.Connection opened after complete ancestor fence and proven via /proc/self/fd to match pinned DB inode
OBSERVATION_ONLY=lsof/fuser/repeated projections
AUTHORIZED_WRITER=reviewed privileged supervisor staged into /root with exact hash verification
FD_PINNING=trusted_root_fd,parent_chain_fds,bus_dir_fd,db_fd,deployment_dir_fd retained through preactivation proof
OPEN_POLICY=O_DIRECTORY|O_NOFOLLOW plus constrained openat2(RESOLVE_BENEATH|RESOLVE_NO_MAGICLINKS|RESOLVE_NO_SYMLINKS) for every untrusted path component and fixed DB basename
FENCE_MUTATION=fchmod/fchown only; no caller-side pathname chmod/chown/stat acquisition
FENCE_TRANSFER_SEQUENCE=journal_metadata_before_first_mutation; fchmod(000); fchown(0,0); fchmod(final_restrictive_mode); validate uid/gid/type/mode/device/inode and DB nlink1
DB_ACCESS_POLICY=no fenced sqlite3.connect(db_path) or path-taking migration/projection helpers unless proven to reuse retained connection
ARTIFACT_TRUST=hash-bound root-staged supervisor, root-protected copied module, hash-checked drop-in helper
FENCE_HELD_THROUGH=ancestor_chain,bound_connection,backup,call1,proof,call2,final_preactivation_proof,dropin,daemon_reload,loaded_unit_proof
FENCE_RELEASE=activation_boundary; close retained connection, restore DB/WAL/SHM and child directories by FD, restore user/home traversal last
POST_ACTIVATION_COMPARISON=authority-state only
NOT_CLAIMING=whole-DB immutability after writer resume


## Related reference

- `references/production-sqlite-writer-fencing.md` — concise session-derived checklist and pitfalls from the GRO-4318 authority-init deployment contract review, including pathname-fence TOCTOU, same-UID parent-directory replacement/WAL redirection, trusted-ancestor descriptor fencing, root-staged supervisor bootstrap, and root-protected module/helper copies.

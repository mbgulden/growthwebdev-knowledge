# Release contract path semantics and systemd drop-in ownership

Use this reference when freezing or reviewing a Prismatic release contract that moves an accepted exact head through GitHub PR/merge and immutable systemd deployment.

## Durable lessons

1. **Separate repair delta from PR delta.**
   - A failed-producer repair may have a small checkpoint-to-head delta, e.g. two paths.
   - The GitHub PR allowlist is not necessarily that repair delta; compute it with merge-base/triple-dot semantics: `git diff --name-only BASE_SHA...HEAD`.
   - Also compute the base-tree to deterministic merge-tree delta: `git diff --name-only BASE_SHA EXPECTED_MERGE_TREE`.
   - Require both PR and base-to-merge sets to equal the frozen allowlist.

2. **Do not use raw two-dot output as PR truth after base drift.**
   - `git diff --name-only BASE_SHA..HEAD` can include current-main-only commits in reverse when the branch is behind/diverged from `origin/main`.
   - If those paths are dashboard or unrelated mainline preservation work, the contract must say the expected merge tree preserves them rather than treating them as candidate changes.

3. **Bind all PR-path blobs, not only the newly repaired files.**
   - For every PR allowlist path, record both `git rev-parse HEAD:path` and `git show HEAD:path | sha256sum`.
   - Before push/merge, verify all blobs at HEAD.
   - After merge, verify the same blob identities in the merge commit and verify the base-to-merge changed-path set is still the frozen allowlist.

4. **Receipt-owned systemd drop-ins need no-clobber publication and deletion-free rollback.**
   - Do **not** model rollback as `lstat → hash → rm`. That validation/removal sequence is TOCTOU-racy: another actor can swap the pathname after validation and before unlink.
   - Derive two concrete receipt-owned paths: a release drop-in such as `/etc/systemd/system/prismatic-gateway.service.d/99-<task>-<merge-short>-release.conf`, and a lexically later rollback override such as `zz-<task>-<merge-short>-rollback.conf`.
   - Immediately before activation, prove both final names are absent; stop if either exists or is a symlink.
   - Freeze exact bytes and SHA-256 for both drop-ins. The rollback override should clear/restate prior effective `ExecStart` and restore prior effective `WorkingDirectory`, so rollback is an override publication rather than deletion.
   - Publish with a reviewed helper or script that operates relative to an opened trusted parent-directory FD, validates owner/mode, uses `O_NOFOLLOW`, holds an exclusive deployment lock, writes to a staging name without `.conf`, hashes through the same opened FD, binds device/inode/size/hash, publishes with `renameat2(RENAME_NOREPLACE)`, and `fsync`s the directory.
   - Incomplete staging residue must be systemd-ignored and preserved for inspection. After successful publication, prove regular/non-symlink identity and frozen hash before `daemon-reload`.
   - Rollback must never unlink, truncate, overwrite, rename-away, or delete the release drop-in or any pre-existing pathname. It publishes the higher-order rollback override with the same no-replace helper, then daemon-reloads/restarts and proves prior provenance/health.
   - Any failure after staging or publication authorizes no daemon-reload/restart unless rollback override publication succeeds; otherwise report `BLOCKED/manual recovery` and leave artifacts intact for inspection.

## Review checks

A release-contract reviewer should independently reproduce:

```bash
git fetch origin
git rev-parse origin/main
git diff --name-only BASE_SHA...HEAD
git merge-tree --write-tree BASE_SHA HEAD
git diff --name-only BASE_SHA EXPECTED_MERGE_TREE
for p in <allowlist paths>; do
  git rev-parse HEAD:$p
  git show HEAD:$p | sha256sum
done
```

Then inspect the deployment/rollback section for path absence, frozen bytes/hash, atomic `O_EXCL` creation, post-install hash proof, and hash-owned rollback deletion limits.

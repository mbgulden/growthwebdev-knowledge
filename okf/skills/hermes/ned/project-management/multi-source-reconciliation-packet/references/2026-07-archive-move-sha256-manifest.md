---
type: Reference
title: SHA-256 manifest + byte-count cross-check for archive moves
description: When the reconciliation packet calls for moving "runtime-only" or "archive" directories out of a tracked repo (for example `dist.backup-*` or `node_modules/`), produce a JSON manifest that records per-file SHA-256 + declared total bytes, then verify on-disk totals match declared totals byte-for-byte after the move. This is the canonical proof that an archive move actually preserved the bytes.
tags: [archive, sha256, manifest, integrity, move-not-copy, reconciliation]
timestamp: 2026-07-28T01:20:00Z
source_session: HDE reconciliation packet items 2a/2b (2026-07-28)
related_skills: [multi-source-reconciliation-packet, worktree-hygiene-and-cleanup-safety, response-contract-and-result-reporting]
---

# SHA-256 manifest + byte-count cross-check for archive moves

## Symptom

The reconciliation packet classifies some paths as `archive` (move to `_hde_cleanup_archive/...`) or `runtime-only` (add to `.gitignore`). The agent executes the move with `os.rename` or `mv`, deletes the source, and reports "done." But there is no proof that the moved bytes are intact and complete.

## Why a manifest is needed

A move without a manifest is silent about:

- whether every file was actually copied,
- whether the byte counts survived the move,
- whether a partial move left one side truncated.

The agent will not detect a partial move until Michael (or another agent) tries to use the archive and finds it broken weeks later. That is exactly the failure mode reconciliation packets are designed to prevent.

## Pattern

For each directory being moved:

1. **Write the manifest first**, before touching the source. The manifest records:
   - archive name
   - source path (full)
   - destination path (full, after move)
   - file count
   - declared total bytes
   - per-file records: relative path, byte count, SHA-256

   ```json
   {
     "archived_at_utc": "2026-07-28T01:16:00+00:00",
     "operator": "ned",
     "reason": "HDE reconciliation item 2b: archive timestamped build backups; current dist/ supersedes them.",
     "sources": [
       {
         "archive_name": "dist.backup-bad-old-shell-20260718T093141Z",
         "src_path": "/home/ubuntu/work/hd-platform-staging/dist.backup-bad-old-shell-20260718T093141Z",
         "dest_path": "/home/ubuntu/work/_hde_cleanup_archive/2026-07-27-dist-backups/dist.backup-bad-old-shell-20260718T093141Z",
         "file_count": 565,
         "total_bytes": 17788578,
         "files": [
           {"path": "API.md", "bytes": 1234, "sha256": "..."},
           ...
         ]
       }
     ]
   }
   ```

2. **Use `os.rename`** rather than `shutil.copytree + rmtree`. `os.rename` is atomic on the same filesystem and either succeeds or fails — no half-state. Cross-filesystem moves fall back to `shutil.move`, which can fail mid-way, but `os.path.isdir(src) == False` after the call is the post-condition that proves the source is gone.

3. **After the move, re-walk the destination** and verify:
   - `os.path.isdir(dest)` is True
   - `os.path.isdir(src)` is False
   - The sum of `os.path.getsize(...)` over every file on disk equals the declared `total_bytes` byte-for-byte (allow at most 1% drift for xattr/perm metadata, or 1024 bytes whichever is greater).
   - SHA-256 of a spot-check sample (10 files per archive minimum) matches the manifest.

4. **Save the manifest** as `<archive_root>/archive-manifest.json`. The manifest is itself an evidence artefact and should be referenced from the reconciliation packet and the Linear parent comment.

## Worked example (HDE, 2026-07-28)

| Field | Value |
|---|---|
| Archives | `dist.backup-bad-old-shell-20260718T093141Z/` (17,788,578 bytes, 565 files)<br>`dist.backup-pre-price-copy-20260718T165249Z/` (17,709,716 bytes, 565 files) |
| Destination root | `/home/ubuntu/work/_hde_cleanup_archive/2026-07-27-dist-backups/` |
| Manifest | `archive-manifest.json` (209 KB; SHA-256 of every file) |
| Move | `os.rename` per directory (atomic on same FS) |
| Post-condition | source dirs absent, dest dirs present, declared totals match disk totals exactly |
| Spot-check | 10 files per archive SHA-256 validated against manifest |
| Verifier | `/tmp/hermes-verify-hde-recon-2a-2b-final-2026-07-28.py` (deleted after PASS) |

The packet and the Linear parent issue [GRO-4343](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4343) both reference the manifest path. Future agents needing to restore one of the backups can verify the manifest's SHA-256 against on-disk bytes before using it.

## Pitfalls

- **Do not use `cp -r` followed by `rm -rf`.** A partial copy leaves the source deleted and the destination incomplete. `os.rename` (same filesystem) is atomic.
- **Do not skip the post-move byte-count check.** `os.rename` succeeded does not mean every file made it. The byte-count cross-check is the cheapest reliable proof.
- **Do not embed the file list in the reconciliation packet itself.** The packet is read by humans; the manifest is read by agents. Keep them separate. The packet references the manifest path; the manifest lives next to the archives.
- **Do not run the SHA-256 step inside the verifier script only.** Compute the manifest before the move, then re-verify inside the verifier. The manifest is durable evidence; the verifier is throwaway proof.
- **Do not exceed the 1% / 1024-byte drift tolerance without investigating.** A real drift means the move lost or duplicated something. The drift budget is for filesystem metadata, not for file bytes.
- **Do not put credentials or full paths to secrets in the manifest.** The manifest should record relative paths inside the archive and SHA-256. If the archive contains customer data, classify the archive itself as `sensitive-review` and skip the manifest until Michael approves.

## Related

- `multi-source-reconciliation-packet/SKILL.md` "Required output" section, item 1 (path classification) and "Production-readiness gate" — the manifest path belongs in the packet's "Artifacts produced" list.
- `worktree-hygiene-and-cleanup-safety` — for the broader pattern of "preserve good/ambiguous work, archive the rest."
- `references/2026-07-stat-only-sensitive-file-resolution.md` — when the archive contains a sensitive file, defer to that pattern first.
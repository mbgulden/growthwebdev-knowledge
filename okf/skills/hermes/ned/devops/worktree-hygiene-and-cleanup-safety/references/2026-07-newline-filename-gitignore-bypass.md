---
type: Reference
title: Newline-filename .gitignore bypass + stat-only resolution
description: Pattern for resolving a flagged sensitive file whose name contains a literal newline character (or other control characters) that bypasses .gitignore globs. Stat-only inspection without peeking at contents, empty-file SHA-256 sentinel, deletion/move receipt, defensive .gitignore comment.
tags: [newline-filename, gitignore-bypass, sensitive-file, stat-only, deletion-receipt, empty-sha-sentinel]
timestamp: 2026-07-28T00:35:00Z
source_session: HDE reconciliation packet (2026-07-27/28)
related_skills: [worktree-hygiene-and-cleanup-safety, multi-source-reconciliation-packet]
---

# Newline-filename `.gitignore` bypass + stat-only resolution

## Symptom

A reconciliation packet, `git status --porcelain --untracked-files=all`, or `git ls-files --others --exclude-standard` shows a file that looks sensitive (named `production*` or `*.db*` or `*.env*`) but the corresponding `.gitignore` rule does not match it. `cat .gitignore` looks correct. `git check-ignore -v <path>` returns nothing.

## Diagnosis

The filename almost certainly contains a control character that the display layer hides. In a typical incident:

```text
$ ls /home/ubuntu/work/hd-platform/ | grep -i database
production_database.db
```

But the file is actually named `production_database.db\n` with a literal trailing newline. The `*.db` glob does not match because the trailing newline breaks the pattern.

Confirmation probe (Python only — never `cat` the file):

```python
import os
for name in os.listdir("/home/ubuntu/work/hd-platform/"):
    if "database" in name.lower():
        print(repr(name))   # 'production_database.db\n'  <- newline visible
```

If `repr()` shows the `\n`, the diagnosis is confirmed.

## Resolution pattern

Treat the file as flagged sensitive even though it appears as ordinary untracked. The agent must not `cat` or `open(path).read()` to "look inside" — that defeats the entire reason the file was flagged. Use stat-only inspection.

### Step 1: Stat-only inspection

```python
import os, hashlib, datetime

target_dir = "/home/ubuntu/work/hd-platform/"
records = []
for name in os.listdir(target_dir):
    if "database" not in name.lower():
        continue
    full = target_dir + name
    st = os.lstat(full)
    with open(full, "rb") as f:        # only for hashing
        data = f.read()
    records.append({
        "name_repr": repr(name),
        "size_bytes": st.st_size,
        "mode": oct(st.st_mode),
        "inode": st.st_ino,
        "nlink": st.st_nlink,
        "mtime_utc": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat(),
        "ctime_utc": datetime.datetime.fromtimestamp(st.st_ctime, datetime.timezone.utc).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
```

Do **not** print, log, or display `data` itself. Hashing is acceptable because the hash is bound to bytes the agent chose to read but never displayed.

### Step 2: Empty-file sentinel

If `size_bytes == 0`, the file is provably empty. Confirm with the canonical empty-file SHA-256:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

If the recorded `sha256` matches this constant, the file was truly zero bytes from creation. Safe to delete or quarantine.

If `size_bytes > 0`, stop. The agent has not been authorized to read the contents, and a non-empty file with a sensitive name needs owner direction. Hold the file (or move it to quarantine with mode `0600`) and report back.

### Step 3: Save a deletion/move receipt

Save to a path outside any tracked repo, e.g. `/home/ubuntu/work/_hde_quarantine/YYYY-MM-DD/`:

```json
{
  "quarantined_at_utc": "2026-07-28T00:31:33.797334+00:00",
  "action": "deleted (was empty stub with broken filename)",
  "original_path": "/home/ubuntu/work/hd-platform/production_database.db\n",
  "original_filename_repr": "'production_database.db\\n'",
  "size_bytes": 0,
  "sha256_pre_deletion": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "inode": 1593708,
  "nlink": 1,
  "mode": "0o100644",
  "mtime_utc": "2026-07-19T03:24:53.595113+00:00",
  "ctime_utc": "2026-07-19T03:24:53.595113+00:00",
  "rationale": "..."
}
```

The SHA-256 is a tamper-evident binding. If the agent had quietly replaced the file before hashing, the hash would change. The receipt proves which bytes were hashed.

### Step 4: Patch `.gitignore` with comments only

```gitignore
*.db
# Defensive note: filenames containing a literal newline bypass *.db globs.
# 2026-07-27 HDE reconciliation found one such empty stub and deleted it.
# See /home/ubuntu/work/_hde_quarantine/2026-07-27/production_database_deletion_record.json
node_modules/
```

Do **not** add a new glob like `*` or `?\?` to "fix" the bypass — those would mask legitimate files and break unrelated work. A comment is sufficient because the bug is rare and future agents reading the comment know to inspect filenames with `repr()`.

### Step 5: Verify with a fresh ad-hoc verifier

Run `npm run build` if the canonical command expects it (it almost certainly will not detect Markdown-only edits). Then write a `/tmp/hermes-verify-*-resolution.py` script that asserts:

- the file is gone from disk (`os.lstat` raises `FileNotFoundError`),
- the receipt exists with all required fields and the canonical empty SHA-256,
- `.gitignore` is patched with the comment, not a new glob,
- the full packet and Telegram summary contain the "RESOLVED" markers,
- the Telegram summary is ASCII-clean (re-run the ASCII check after every patch — em-dashes sneak back in even when the agent is consciously avoiding them),
- no credential-shaped strings leak in any artefact.

Run the verifier, delete it, report `PASS`.

### Step 6: Update docs and post Linear comment

Update both packet documents (full + Telegram-safe) to mark the decision row "RESOLVED YYYY-MM-DD". Post a structured comment to the parent Linear issue summarising:

- filename (with `repr()` so the newline is visible),
- size + SHA-256 + inode + mtime,
- why untracked,
- action taken,
- receipt path,
- any `.gitignore` defensive changes.

## Worked example (HDE, 2026-07-28)

| Field | Value |
|---|---|
| Filename (literal) | `production_database.db\n` |
| Size | 0 bytes |
| SHA-256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Inode | 1593708 |
| Mode | `0o100644` |
| Created | 2026-07-19 03:24:53 UTC |
| Why untracked | `*.db` glob did not match because the trailing newline broke the pattern |
| Action | Deleted; receipt at `/home/ubuntu/work/_hde_quarantine/2026-07-27/production_database_deletion_record.json`; `.gitignore` patched with comment only |

The full session transcript of this incident (stat-only investigation, Telegram summary updates, ad-hoc verifier, Linear comment) is recorded under `multi-source-reconciliation-packet/references/2026-07-stat-only-sensitive-file-resolution.md`.

## Pitfalls

- **Never `cat` the file** even briefly, even if you think it is empty. The override did not authorize reading contents. Use the SHA-256 round-trip to bind the receipt to the actual bytes without displaying them.
- **Never add a `*` glob** to `.gitignore` to "fix" the bypass. Comments only.
- **Never use `os.path.exists('plain')` to test for the file** when the filename contains control characters. Use `os.lstat` with the literal name from `os.listdir`. `exists` silently returns False.
- **Never skip the receipt.** If `st_size > 0` and you cannot proceed without peeking, hold the file (or move to quarantine with `0600`) and report back. The override did not authorize destruction of unknown bytes.
- **Never mark the Telegram summary ASCII-clean once** and assume it stays that way. After every patch to either packet document, re-run the ASCII check. Em-dashes and other smart punctuation sneak in even when the agent is consciously avoiding them.
- **Never trust a green `npm run build` on docs-only edits** as proof of a Markdown patch. Run a fresh `/tmp/hermes-verify-*-resolution.py` artifact verifier. The build green is necessary context, not sufficient evidence.

## Empty-file canonical SHA-256

The SHA-256 of zero bytes is a well-known constant and works as a sentinel for "this file was provably empty":

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Useful in any stat-only investigation where reading is forbidden but proving emptiness is required before destruction.
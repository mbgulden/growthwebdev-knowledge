# Lane discipline: symlink taxonomy in `prismatic-pwp-ubersuggest-auth`

## What the repo looks like

`prismatic-pwp-ubersuggest-auth` is organized around two parallel plugin
trees:

- `plugins/<name>/...` — the canonical checkin location.
- `prismatic/shipped_plugins/<name>/...` — a symlink target that the
  engine actually loads at runtime.

`ls -la plugins` shows `plugins → prismatic/shipped_plugins` (the
canonical checkin location is the symlink, not the directory).

## Why this matters for the lane guard

The lane guard reads the agent's `Owned directories` list and checks
each modified file against it. In Ned's case the list is
`['scripts/', 'prismatic/', 'plugins/']`. The symlink means **the same
file lives under two paths simultaneously**:

```
plugins/pwp/capabilities/publish_kpi_tracker/__init__.py
└── prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/__init__.py
```

When the agent reports "I edited `prismatic/shipped_plugins/pwp/...`",
the lane guard sees that path. When the agent reports "I edited
`plugins/pwp/...`", it sees that path. Both are allowed (both prefixes
are in the lane), but the same file is recorded twice in `git status`
under both paths during the change.

## Implications for patch operations

- **`write_file` / `patch` from this profile writes to whichever path
  the agent saw first.** Use the canonical `plugins/<name>/...` path
  unless the runtime loader is being diagnosed.
- **`git status` shows the file under both paths during edits.** Use
  `git status --porcelain | sort -u` before committing to avoid
  double-counting.
- **State checks at runtime read from `prismatic/shipped_plugins/...`
  paths** because that's where the engine loader resolves. A test
  environment that imports `plugins.pwp.capabilities.publish_kpi_tracker`
  will succeed; one that imports `prismatic.shipped_plugins.pwp.capabilities.publish_kpi_tracker`
  will also succeed. They both point to the same module instance
  (because of the symlink).
- **`git restore` on one path restores the other path too** — the symlink
  is the source of truth. If you need to revert just a partial edit
  without losing unrelated work, use `git checkout -- <path>` on the
  path the agent originally wrote to.

### `git add plugins/...` errors "beyond a symbolic link"

When you stage via the canonical symlink path, git refuses:

```
fatal: pathspec 'plugins/pwp/capabilities/.../foo.json' is beyond a symbolic link
```

**Recovery.** Stage via the resolved path. `plugins/` is a symlink
pointing at `prismatic/shipped_plugins/`, so:

```bash
# BAD — fails with "beyond a symbolic link"
git add plugins/pwp/capabilities/publish_kpi_tracker/sites/hd-engine.runtime.json

# GOOD — git follows the symlink when given the resolved path
git add prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/sites/hd-engine.runtime.json
```

Same rule for `git rm`, `git mv`, and any other porcelain command
that takes a path. The pre-push gate accepts either path (both are
in Ned's lane), but staging only works through the symlink target.

### `cat > plugins/.../file` writes to the resolved inode, not the symlink path

A terminal `cat > file` heredoc (or any non-patch file write) on the
symlink path writes through the symlink to the target inode. The
write **succeeds**, but `git status` then shows the file under
**both** paths — or under only the resolved path if the symlink
target doesn't already exist on disk. The latter is the silent
trap: the file exists, you can `cat` it, but `git add` via the
symlink path fails because the file isn't visible at that path yet.

**Recovery for the silent-write trap:**

1. Write to the resolved path explicitly so the file lands where
   git expects it:
   ```bash
   cat > /home/ubuntu/work/prismatic-pwp-ubersuggest-auth/prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/sites/hd-engine.runtime.json <<EOF
   { "...": "..." }
   EOF
   ```
2. Or stage via the resolved path immediately after the write:
   ```bash
   git add prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/sites/hd-engine.runtime.json
   ```
3. Verify with `ls -la` that the file exists at both paths via the
   symlink — `readlink -f plugins/.../file` shows the resolved inode,
   and the file at the resolved path should be non-empty.

When in doubt, always use `write_file` / `patch` tools (which
resolve symlinks explicitly) over `cat > file` shell heredocs for
any file inside `plugins/...`.

## The lane guard's behavior on cleanup work

When a session adds non-`prismatic/`, non-`plugins/` files at the repo
root (e.g. `conftest.py`, `pytest.ini`, `pyproject.toml`) — these are
outside the lane. The lane guard will list them and abort the commit.
Recovery:
- Move the necessary pieces into `plugins/<name>/...` and re-export.
- For test-helper files only, place them under `plugins/<name>/tests/conftest.py`
  or `plugins/<name>/tests/__init__.py` so the lane guard sees them
  inside the agent's prefix.
- For repo-wide config (`pyproject.toml`, `pytest.ini`), the agent
  cannot add these solo. The lane guard is designed to require a human
  to merge them. Accept the gate and post the "ready, push requires
  human" comment to Linear.

## Verifying the symlink has not drifted

If a future `git checkout` reverses the symlink (e.g. an old PR replaced
the symlink with a real directory), the new file lives under only one
path. Symptom: `git status` shows the file under `plugins/` but Python
imports under `prismatic/shipped_plugins/` fail because no file exists
there. Recovery: `git restore prismatic/shipped_plugins/...` to
reconstitute the symlink, or `ln -s ../plugins prismatic/shipped_plugins`
at the repo root. The historical command was `ln -s ../plugins prismatic/shipped_plugins`.

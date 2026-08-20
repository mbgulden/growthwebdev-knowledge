# Prismatic Journal Core + Dashboard Browser Pattern

Session learning: daily journal continuity should be core Prismatic plumbing, not a fragile Hermes-profile-only wrapper. If a journal cron fails, repair the core journal contract and expose the artifacts in the operator dashboard when useful.

## Failure contract observed

`Hermes daily journal snapshot` failed because `project-registry.json` stored `_last_sync` as a string, while `extract_golden_thread_summary()` assumed it was a dict:

```text
AttributeError: 'str' object has no attribute 'get'
```

## Durable fix pattern

In `prismatic/journal.py`:

```python
def coerce_sync_summary(sync: Any) -> dict[str, Any]:
    if isinstance(sync, dict):
        return sync
    if isinstance(sync, str):
        return {"synced_at": sync}
    return {}
```

Then use the coerced shape in Golden Thread summary rendering:

```python
raw_sync = reg.get("_last_sync", {})
sync = coerce_sync_summary(raw_sync)
if "synced_at" in sync and len(sync) == 1:
    lines.append(f"- Last sync: {sync['synced_at']}")
else:
    ... counter rendering ...
```

Also harden workspace resolution because runtime/systemd `PRISMATIC_HOME` can mean `~/.prismatic` rather than the source/data workspace. Prefer `PRISMATIC_WORKSPACE`/`PRISMATIC_WORKDIR`; otherwise only treat `PRISMATIC_HOME` as workspace if it contains workspace-owned state like `Hermes-Research` or `project-registry.json`.

## Additive Prismatic experience

When the user asks for journal access, add a read-only browser instead of just fixing the cron:

Core API functions:

```python
list_journal_files(config, limit=500) -> {root, exists, total, by_kind, files, recent}
read_journal_file(relpath, config, max_chars=120000) -> {path, kind, size, mtime, content, truncated}
```

Important safety rule:

- Resolve the requested path against `journal_root` and reject traversal outside the root.
- Only allow text-like journal extensions (`.md`, `.json`, `.txt`).

Gateway routes:

```text
GET /api/gateway/journals/tree
GET /api/gateway/journals/file?path=...
```

Dashboard:

- Add a **JOURNALS** tab to the canonical operator dashboard.
- Show counts by kind: daily, inbox, weekly, latest, index.
- Render a file tree/list similar to workspace tree.
- Load selected file content in a preview pane.
- Include an “Open via workspace tree” link when applicable.

## Runtime/worktree verification

Prismatic often has multiple local worktrees or similarly named repos. Before claiming a core journal fix, verify the module used by the cron/runtime is the module you patched:

```python
import inspect
import prismatic.journal
print(inspect.getfile(prismatic.journal))
```

If this points at a different worktree than the file you edited, either patch the runtime tree too or clearly label the first patch as not live. Include this assertion in the `/tmp/hermes-verify-*` script so the evidence proves the active runtime path, not just a nearby source checkout.

When the Tier-1 watchdog includes unrelated credential failures, the journal remediation can still be complete. Report the requested job as `RECOVERED` and list unrelated continuing failures separately instead of forcing `silent_failures=0` for the whole fleet.

## Verification expectations

Use a `/tmp/hermes-verify-*` tempfile verifier and prove:

```text
py_compile=passed
core_sync_shape_hardening=passed
core_workspace_resolution=passed
core_journal_tree_read=passed
path_traversal_guard=passed
gateway_journal_routes=present
dashboard_journals_tab=present
local_journal_tree_api=200
local_journal_file_api=200
daily_journal_snapshot=exit0
tier1_watchdog_silent_failures=0
public_dashboard_journal_tab=present
cleanup_exists=false
```

Report as ad hoc targeted verification only unless a full canonical suite actually ran.

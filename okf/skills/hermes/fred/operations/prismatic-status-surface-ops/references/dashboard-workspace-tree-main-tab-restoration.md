# Dashboard Workspace Tree Main-Tab Restoration

Use this reference when the public `/workspace-tree` route works but Michael says it feels weird, separate, or not useful. The durable lesson: workspace browsing belongs inside the canonical `Prismatic Hub Dashboard` Workspaces tab, with standalone `/workspace-tree` kept only as a backup/deep-link compatibility surface.

## User-corrected product shape

- Do **not** treat a separate `/workspace-tree` page as the primary product experience once `/dashboard` is canonical again.
- The main dashboard should contain a navigable Workspace Tree tab:
  - folder tree / roots on the left;
  - file preview/viewer on the right;
  - URL/deep-link support such as `/dashboard?file=prismatic/gateway/server.py` so Telegram links land in the dashboard context;
  - a fallback/legacy link to `/workspace-tree?file=...`, not the other way around.
- Avoid mock workspace tables (`mockWorkspaces`) as a substitute for real workspace navigation.

## Backend pattern

Reuse the existing workspace-tree safety contract rather than introducing a new file resolver:

```text
/api/workspaces                    -> roots + shallow tree
/api/workspace-tree/preview?file=  -> file preview under allowed roots
/api/workspace-tree/node?file=&depth= -> safe directory expansion under allowed roots
```

The `/api/workspace-tree/node` route should:

- call the same `_workspace_tree_resolve(file)` used by preview;
- reject traversal with the existing `403 workspace-tree path blocked` behavior;
- require the resolved path to be a directory;
- return `_workspace_tree_node(target, root, max_depth=depth)` under the matched allowed root;
- cap `depth` with FastAPI `Query(..., ge=0, le=3)` or similarly bounded limits.

## Frontend pattern

In `prismatic/gateway/templates/dashboard.html`:

- replace the old Workspaces mock/status table with an embedded explorer;
- include stable DOM anchors such as:

```text
#workspace-tree-roots
#workspace-file-preview
#workspace-preview-name
#workspace-legacy-link
```

- implement directory expansion against `/api/workspace-tree/node`;
- implement file preview against `/api/workspace-tree/preview`;
- make `/dashboard?file=<path>` open the Workspaces tab and preview the target file automatically;
- make `#workspaces` open the Workspaces tab without requiring a click;
- keep `/workspace-tree` and `/workspace-tree?file=...` working for old Telegram links and emergency standalone viewing.

## Verification pattern

Use a focused log, e.g. `/tmp/fred-dashboard-workspace-tree-main-production-verify.log`, and keep chat output compact.

Minimum proof:

```text
python3 -m py_compile prismatic/gateway/server.py
extract inline dashboard <script> to /tmp/...js
node --check /tmp/...js
route table includes /dashboard, /workspace-tree, /api/workspaces, /api/workspace-tree/preview, /api/workspace-tree/node
curl local/public /dashboard?file=prismatic/gateway/server.py -> 200 text/html
curl local/public /api/workspace-tree/node?... -> 200 application/json
curl local/public /api/workspace-tree/preview?file=prismatic/gateway/server.py -> 200 application/json
curl traversal attempt against /api/workspace-tree/node?file=../../etc -> 403 application/json
browser DOM proof: Workspaces tab visible, tree present, preview present, previewName points at requested file
```

Suggested compact marker:

```text
MARKER=DASHBOARD_WORKSPACE_TREE_MAIN_OK
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical_full_suite_green,agy_completed_work_integration_gate
```

## Pitfalls

- Do not regress canonical `/` and `/dashboard` serving of `templates/dashboard.html` while improving Workspaces.
- Do not replace the canonical dashboard with the standalone workspace-tree surface.
- Do not weaken path traversal protections or bypass the existing allowed-root resolver.
- Do not claim success from HTTP 200 alone; prove DOM behavior and file preview content.
- If a PR shows only the template but the UI calls a new API route, check for auto-checkpoint commits and squash/verify the branch diff includes both `server.py` and `dashboard.html` before CI/merge.

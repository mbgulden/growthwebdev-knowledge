# Public workspace-tree/dashboard route repair

## When this applies

Use this when `prismatic.growthwebdev.com` has a live `/health` route but operator/dashboard routes such as these return `404`:

```text
/dashboard
/workspace-tree
/api/workspaces
/api/workspace-tree/preview
/api/gateway/dashboard/contracts
```

This usually means the public hostname is reaching the gateway process, but the active gateway source or nginx proxy map is missing the dashboard/workspace-tree compatibility routes.

## Diagnosis sequence

1. Reproduce public and local routes separately:

```bash
curl -sS -D /tmp/h -o /tmp/b https://prismatic.growthwebdev.com/workspace-tree?file=okf/operations/INDEX.md
curl -sS -D /tmp/h -o /tmp/b http://127.0.0.1:9000/workspace-tree?file=okf/operations/INDEX.md
```

2. Confirm which module systemd is running:

```bash
systemctl cat prismatic-gateway
PYTHONPATH=/home/ubuntu/.prismatic/venv_stable/lib/python3.12/site-packages python3 - <<'PY'
import inspect
import prismatic.gateway.server as s
print(inspect.getfile(s))
for r in s.app.routes:
    print(getattr(r, 'path', None), sorted(getattr(r, 'methods', []) or []))
PY
```

3. If `/health` works but dashboard routes are missing from the route table, patch the live gateway source, not nginx alone.

## Repair pattern

Add read-only compatibility routes to `prismatic/gateway/server.py`:

```text
GET /
GET /dashboard
GET /workspace-tree
GET /api/workspaces
GET /api/workspace-tree/preview
GET /api/gateway/dashboard/contracts
```

Recommended behavior:

- Prefer `/dashboard` serving `prismatic/gateway/templates/dashboard.html` when that canonical operator dashboard is available and in-scope.
- If the active production gateway has `/health` and `/workspace-tree` but both `/` and `/dashboard` return FastAPI `404 {"detail":"Not Found"}`, a small no-JS operator entry shell is an acceptable production durability repair. It must visibly render before JavaScript, use the title/header `Prismatic Engine Operator Dashboard`, and link to working surfaces: `/workspace-tree`, `/health`, `/api/plugins/catalog`, `/api/plugins/governance`, and `/api/governance/merge-backlog`.
- The fallback shell must be safe if API calls fail and must not perform filesystem preview reads itself; leave path/file preview to `/workspace-tree` and its API.
- `/workspace-tree?file=...` serves a small read-only shell that previews a safe workspace-relative file.
- `/api/workspaces` lists configured/discovered workspace roots.
- `/api/workspace-tree/preview?file=...` resolves only under `/home/ubuntu/work` or the configured workspace root and blocks traversal.
- `/api/gateway/dashboard/contracts` returns a read-only manifest and does **not** run verification side effects.
- If the existing workspace-tree plugin API exists, mount it under `/api/plugins/hermes-plugin-workspace-tree-navigator` instead of duplicating all plugin internals.


Production durability sequence for route repairs:

1. Reproduce public and local status codes, and inspect the runtime route table from `/home/ubuntu/.prismatic/runtime/prismatic-engine`.
2. Patch a clean feature branch in the repo, not the mutable runtime checkout.
3. Prove the branch on an isolated local port. Use Hermes `terminal(background=true)` for the temporary server; do **not** shell-background with `&` in a foreground command.
4. Open/merge a reviewed PR to `main` when policy allows Fred to merge clean production-surface PRs.
5. Fast-forward the durable runtime checkout on `main`, restart `prismatic-gateway.service`, then prove public routes.
6. Confirm runtime remains clean on `main...origin/main` and `/workspace-tree` traversal protection still returns 400/403.

Patch nginx when public API paths are still 404 after local gateway works:

```nginx
location = /api/workspaces {
    proxy_pass http://127.0.0.1:9000/api/workspaces;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /api/workspace-tree/ {
    proxy_pass http://127.0.0.1:9000/api/workspace-tree/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Then:

```bash
python3 -m py_compile prismatic/gateway/server.py
sudo systemctl restart prismatic-gateway
sudo nginx -t
sudo systemctl reload nginx
```

## Production durability deployment ladder

Treat `/`, `/dashboard`, and `/workspace-tree` public route repairs as production durability work, not as a mutable live hotfix:

1. Reproduce public and local routes separately and save detailed output under `/tmp/fred-dashboard-operator-surface-verify.log` or another explicit `/tmp` proof log.
2. Inspect the route table from the active runtime source with the same `PYTHONPATH`/venv that systemd uses.
3. Patch a clean feature branch from `origin/main`; do not edit a dirty production checkout directly.
4. Prove the branch locally first. If starting a temporary gateway, use a tracked background process and kill it after proof; do not use shell `&` in foreground commands.
5. Open a small PR, include before/after curl proof, route-table proof, files changed, focused verification, explicit non-claims, and marker `DASHBOARD_OPERATOR_SURFACE_REPAIR_READY_FOR_DEPLOY_OK`.
6. If Fred is acting as staging governor and policy permits merging production repairs, wait for CI, merge, fast-forward `/home/ubuntu/.prismatic/runtime/prismatic-engine` on `main`, restart `prismatic-gateway.service`, then prove public routes.
7. Final production proof should include local and public `/`, `/dashboard`, `/health`, `/workspace-tree`, content assertions for `Prismatic Engine Operator Dashboard`, and traversal safety (`/api/workspace-tree/preview?file=../../etc/passwd` should remain 400/403). Final marker: `DASHBOARD_OPERATOR_SURFACE_PRODUCTION_OK`.

## Verification checklist

Use a `/tmp/hermes-verify-*` script that checks:

- changed files exist
- `py_compile` passes for `prismatic/gateway/server.py`
- route table contains every repaired route (`/`, `/dashboard`, `/workspace-tree`, and relevant APIs)
- local and public routes return `200`:
  - `/`
  - `/dashboard`
  - `/health`
  - `/workspace-tree`
  - `/workspace-tree?file=okf/operations/INDEX.md` when file-preview proof is in scope
  - `/api/workspaces`
  - `/api/workspace-tree/preview?file=okf/operations/INDEX.md`
  - `/api/gateway/dashboard/contracts` when that route is in scope
- `/` and `/dashboard` contain visible fallback text, including `Prismatic Engine Operator Dashboard`, `Workspace Tree`, `Health`, `Plugins`, and `Governance`
- `/workspace-tree` contains `Prismatic Workspace Tree` and the requested file path when previewing a file
- preview API returns actual `INDEX.md` content when file-preview proof is in scope
- contract manifest includes `workspace_tree` and `/workspace-tree` when contract route proof is in scope
- path traversal such as `../../etc/passwd` is blocked with 400/403
- browser/DOM proof shows non-blank content, expected `h1`, required links, and `bodyHas404=false`
- runtime checkout is durable and clean: `git -C /home/ubuntu/.prismatic/runtime/prismatic-engine status --short --branch` should show clean `main...origin/main`

When a stale verifier guard names exactly `prismatic/gateway/server.py`, make the compact proof machine-obvious:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m py_compile prismatic/gateway/server.py
AD_HOC_VERIFICATION=PASS
changed_paths_checked=/home/ubuntu/work/prismatic-engine/prismatic/gateway/server.py
MARKER=DASHBOARD_OPERATOR_SURFACE_PRODUCTION_OK
```

Report as **ad hoc targeted verification**, not full suite-green.


Report as **ad hoc targeted verification**, not full suite-green.

## Pitfalls

- Do not assume nginx is the only failure just because the public URL 404s. If local `:9000` also 404s, the gateway route table is missing the route.
- Do not treat `/health` as proof the dashboard runtime is complete; it may be a stripped/minimal gateway.
- Do not expose arbitrary filesystem reads. Resolve workspace-tree preview paths under the allowed workspace root and explicitly block traversal.
- Do not rely on huge visual screenshots for proof when the page contains large preview content; a DOM check can prove title/headers/content without producing multi-megabyte captures.

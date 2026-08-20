# Production runtime checkout + `/workspace-tree` repair

## When this applies

Use this when the Prismatic production durability standard is installed but live proof still shows either of these blockers:

```text
PRODUCTION_WORKTREE_DURABILITY_OK is not proven
WORKSPACE_TREE_PRODUCTION_OK is not proven
```

Especially when the verifier reports:

```text
route table missing /workspace-tree
local route /workspace-tree?... returns 404
workspace-tree safe preview failed
```

or systemd readback shows the live gateway running from the mutable dev checkout:

```text
WorkingDirectory=/home/ubuntu/work/prismatic-engine
```

## Critical boundary

Do not claim `WORKSPACE_TREE_PRODUCTION_OK` until **public/authenticated browser proof** is captured. A local production-gateway fix is meaningful but is still partial if Cloudflare Access blocks public proof.

Use precise markers:

```text
PRODUCTION_WORKTREE_DURABILITY_OK = runtime checkout proven
WORKSPACE_TREE_PRODUCTION_OK = local + public/auth + browser/screenshot proven
PRODUCTION_RUNTIME_WORKSPACE_TREE_REPAIR_BLOCKED = public/auth/browser proof unavailable
```

## Runtime checkout migration pattern

1. Capture rollback and current service state first:

```bash
systemctl cat prismatic-gateway | sed -E 's/(SECRET|TOKEN|KEY|PASSWORD)=.*/\1=[REDACTED]/g'
systemctl show -p WorkingDirectory,FragmentPath,ExecStart,ActiveState,SubState prismatic-gateway
curl -sS http://127.0.0.1:9000/health
```

2. Create or refresh the dedicated runtime checkout:

```bash
RUNTIME=/home/ubuntu/.prismatic/runtime/prismatic-engine
mkdir -p /home/ubuntu/.prismatic/runtime
[ -d "$RUNTIME/.git" ] || git clone https://github.com/mbgulden/prismatic-engine.git "$RUNTIME"
git -C "$RUNTIME" fetch origin main
git -C "$RUNTIME" checkout -B main origin/main
git -C "$RUNTIME" reset --hard origin/main
git -C "$RUNTIME" clean -fdx
python3 -m py_compile "$RUNTIME/prismatic/gateway/server.py" "$RUNTIME/scripts/verify_production_durability_standard.py"
```

3. Back up systemd and change only the runtime source path:

```bash
BACKUP=/etc/systemd/system/prismatic-gateway.service.pre-production-worktree-migration-$(date -u +%Y%m%dT%H%M%SZ).bak
sudo cp /etc/systemd/system/prismatic-gateway.service "$BACKUP"
sudo python3 - <<'PY'
from pathlib import Path
svc=Path('/etc/systemd/system/prismatic-gateway.service')
s=svc.read_text()
s=s.replace('WorkingDirectory=/home/ubuntu/work/prismatic-engine','WorkingDirectory=/home/ubuntu/.prismatic/runtime/prismatic-engine')
s=s.replace('/home/ubuntu/work/prismatic-engine/.venv_dev/bin:', '/home/ubuntu/.prismatic/runtime/prismatic-engine/.venv_dev/bin:')
svc.write_text(s)
PY
sudo systemctl daemon-reload
sudo systemctl restart prismatic-gateway
```

4. Prove the invariant:

```bash
systemctl show -p WorkingDirectory,FragmentPath,ExecStart,ActiveState,SubState prismatic-gateway
git -C /home/ubuntu/.prismatic/runtime/prismatic-engine status --short --branch
git -C /home/ubuntu/.prismatic/runtime/prismatic-engine rev-parse --short HEAD
curl -sS http://127.0.0.1:9000/health
```

Expected invariant:

```text
WorkingDirectory=/home/ubuntu/.prismatic/runtime/prismatic-engine
runtime git status: ## main...origin/main
```

Rollback:

```bash
sudo cp "$BACKUP" /etc/systemd/system/prismatic-gateway.service
sudo systemctl daemon-reload
sudo systemctl restart prismatic-gateway
curl -sS http://127.0.0.1:9000/health
```

## `/workspace-tree` compatibility route pattern

Patch `prismatic/gateway/server.py` with small read-only gateway-native routes rather than relying on plugin UI assets alone:

```text
GET /workspace-tree
GET /workspace-tree/index.js
GET /api/workspaces
GET /api/workspace-tree/preview?file=...
```

Required behavior:

- `/workspace-tree` returns visible HTML with `Prismatic Workspace Tree`.
- The page contains inline CSS and meaningful fallback content so it stays visible without CDN JavaScript.
- `/workspace-tree/index.js` returns 200 if the page references it.
- `/api/workspaces` returns configured/discovered roots.
- `/api/workspace-tree/preview?file=<safe repo file>` returns 200 and file content.
- traversal, encoded traversal, and absolute private paths return 400/403 and never leak `/etc/passwd`.

A working fallback phrase used in the incident:

```text
Visible fallback content loaded without CDN JavaScript.
```

## Verification ladder

Before merge, prove the branch on a temporary local port:

```bash
PYTHONPATH=. /home/ubuntu/.prismatic/venv_stable/bin/python3 -m prismatic.gateway.server --host 127.0.0.1 --port 9010 --log-level warning
python3 scripts/verify_production_durability_standard.py \
  --route /workspace-tree \
  --local-base http://127.0.0.1:9010 \
  --require-local \
  --enforce-route
```

After merge and runtime deployment, prove live local production gateway:

```bash
cd /home/ubuntu/.prismatic/runtime/prismatic-engine
python3 scripts/verify_production_durability_standard.py \
  --route /workspace-tree \
  --local-base http://127.0.0.1:9000 \
  --require-local \
  --enforce-route
```

Probe exact routes:

```bash
curl -sS -o /tmp/body -w 'status=%{http_code}\n' 'http://127.0.0.1:9000/workspace-tree?file=README.md'
curl -sS -o /tmp/body -w 'status=%{http_code}\n' 'http://127.0.0.1:9000/workspace-tree/index.js'
curl -sS -o /tmp/body -w 'status=%{http_code}\n' 'http://127.0.0.1:9000/api/workspaces'
curl -sS -o /tmp/body -w 'status=%{http_code}\n' 'http://127.0.0.1:9000/api/workspace-tree/preview?file=docs/prismatic-production-durability-standard.md'
curl -sS -o /tmp/body -w 'status=%{http_code}\n' 'http://127.0.0.1:9000/api/workspace-tree/preview?file=../../etc/passwd'
```

## Browser and screenshot proof

Use browser/DOM proof for the live local route after systemd restart:

```text
title = Prismatic Workspace Tree
h1 = Prismatic Workspace Tree
hasBlackPage = false
workspaceJsLoaded = loaded
console errors = 0
```

If Chromium snap cannot write screenshots because of AppArmor/snap permissions (`Failed to write file ... Permission denied`), do not record “browser tools are broken.” Use `wkhtmltoimage` as an alternate screenshot renderer and still keep the DOM/browser proof:

```bash
wkhtmltoimage --width 1440 --height 1200 \
  'http://127.0.0.1:9000/workspace-tree?file=README.md' \
  /home/ubuntu/.prismatic/runtime/proofs/workspace-tree-live-local-$(date -u +%Y%m%dT%H%M%SZ).png
```

## Public/auth proof boundary

If public curl/browser hits Cloudflare Access and returns 302 to `growthwebdev.cloudflareaccess.com`, do **not** stop there when Michael has authorized Cloudflare API use. Use the Cloudflare Access incident skill to add a narrow verifier-IP bypass for the exact Access app/hostname, then verify the public HTTPS route through Cloudflare.

Required verifier-IP bypass shape:

```text
name: Bypass Fred Hermes verifier IP - workspace-tree proof YYYY-MM-DD
decision: bypass
precedence: 1
include: ip <verifier-egress-ip>/32
```

Keep it least-privilege: do not broaden to `everyone`, do not remove Michael email/PIN policies, and do not disturb webhook bypasses.

If API credentials are truly unavailable or policy mutation fails, mark:

```text
public/auth route works = BLOCKED
reason = Cloudflare Access verifier-IP policy could not be created
```

Do not claim `WORKSPACE_TREE_PRODUCTION_OK` until a public HTTPS browser session proves the page is visible, not blank/black, and has no fatal first-party JS errors.

## Public nginx/CDN asset pitfall

If the public HTML route is `200` but `/workspace-tree/index.js` is `404`, inspect nginx before changing app logic. An exact nginx location like `location = /workspace-tree` does not proxy `/workspace-tree/index.js`; add an exact asset location, run `nginx -t`, then reload nginx.

If Cloudflare keeps serving a stale `404` with `cf-cache-status: HIT`, purge the exact URL. If a browser still has the stale asset, cache-bust the script tag, e.g. `/workspace-tree/index.js?v=YYYYMMDD`, merge/deploy, purge both old and cache-busted URLs, and verify from the browser context that `workspaceJsLoaded == "loaded"`.

## Compact stale-guard proof

When the stale verifier asks for exact changed paths, use a `/tmp/hermes-verify-*` script that emits compact JSON and suppresses nested route output. Include:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=runtime systemd readback + git clean + health + production durability enforce verifier + route/public/browser proof
AD_HOC_VERIFICATION=PASS
changed_paths_checked=[...]
cleanup=PASS removed /tmp/hermes-verify-*.py
```

Avoid huge nested verifier bodies; they can be truncated and fail the freshness detector even when the proof is good.

# Workspace-tree review-link 400 + deployed-gateway source of truth (2026-08-20)

Session detail from the HFG guest-fleet review-packet handoff. Class lesson: **the
`/workspace-tree?file=…` deep-link pattern is not a reliable handoff surface on this
deployment**, and the deployed gateway's source of truth is not the worktree you'd guess.

## What happened

1. Packet written to `hd-platform-staging/review-packets/hfg-guest-fleet-2026-08-20/`.
2. First probe: `/api/workspace-tree/preview?file=<path>` → 400 (old API shape).
3. Read a `prismatic-pwp-ubersuggest-auth` worktree copy of the gateway → wrong build
   (that copy still had the `file=` param + `PRISMATIC_WORKSPACE_ROOTS` roots).
4. Deployed gateway (pid on `:9000`) uses `workspace_id`+`path` query params; found via
   the served dashboard bundle's `fetch(`/api/workspace-tree/preview?${query}`)` +
   `URLSearchParams({ workspace_id, path })`.
5. Probe with `workspace_id=ws-0000000000000000000000000002` (Work Repositories =
   `/home/ubuntu/work`) + relative path → **200, exact 10,269 bytes, content == disk**.
   Then, minutes later, the same request began 400ing `invalid workspace identifier`
   consistently — public AND local origin, both routes, for a VALID id.
6. Diagnosis: deployed gateway = `/home/ubuntu/work/prismatic-engine`
   (`ls -l /proc/<pid>/cwd`), env `PRISMATIC_WORKSPACE_REGISTRY_FILE` →
   `~/.prismatic/config/workspace-registry.json` (strict validation in
   `prismatic/gateway/workspace_tree.py`: uid in {0,euid}, mode & 0o022, size cap,
   schema_version==1, exact key sets, request-scoped pinned fd). List endpoint
   (`/api/workspaces`) kept reporting the 4 workspaces while `resolve()` flaked.
7. Decision: NOT a packet bug. Did not fix the production registry inside a handoff
   task (flagged to Michael, separate infra fix). Delivered via tarball + SHA256 +
   FINAL-STATE comment on the parent epic (GRO-4797).

## Rules

- **Source of truth for the deployed gateway is the runtime checkout, not the
  worktree:** `pid=$(ss -tlnp | grep ':9000 ' | grep -oP 'pid=\K[0-9]+' | head -1)`
  then `tr '\0' ' ' < /proc/$pid/cmdline` + `ls -l /proc/$pid/cwd` +
  `tr '\0' '\n' < /proc/$pid/environ | grep -iE 'registry|workspace'`.
  Reading any `work/prismatic-<feature>/` copy for deployed behavior is a stale-read trap.
- **Verify the link the reviewer will actually fetch:** public domain, exact API shape
  from the served bundle, sha256(returned content) == sha256(disk file). A 200 on
  localhost or "the route exists" is not handoff-grade proof.
- **When the surface 400s on valid input:** compare list vs resolve endpoints to isolate
  registry flake from path problem; name the regression precisely (`invalid workspace
  identifier` from `WorkspaceRegistry.resolve()` in workspace_tree.py); fall back to
  tarball+SHA+Linear comment; offer the infra fix as a separate decision.
- **`/workspace-tree` page route is now a 302-ish redirect stub to `/dashboard`** in the
  deployed build — the deep-link param `?file=` is not honored by the new SPA; the new
  contract is `/dashboard?workspace_id=…&path=…#workspaces` (client-side
  `history.replaceState`). Even that depends on the flaky registry, so the web surface
  is best-effort, never the only path.
- **Handoff link + tarball are complements, not alternatives:** post BOTH. The tarball
  comment carries SHA256 + contents + "verify SHA first, then run §3".

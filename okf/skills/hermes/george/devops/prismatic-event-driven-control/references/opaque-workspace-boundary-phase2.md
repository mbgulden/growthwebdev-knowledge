# Opaque workspace boundary Phase 2 gate

Use when public/dashboard workspace APIs are being moved from filesystem-path browsing to an explicit opaque workspace-id boundary.

## Durable lesson

Workspace containment, implementation, Linear dispatch, deployment, and public unblocking are separate gates. An opaque `workspace_id` is a routing identifier, not authentication. Keep edge/Nginx containment active until a separate access-control contract proves that reverse-proxied clients cannot inherit loopback/operator trust.

## Dispatch pattern

1. Treat the current Linear/project registry as the dispatch truth, not handoff prose alone.
2. Before creating a Linear issue, do bounded title/UUID lookup to avoid duplicates.
3. For deterministic single-create writers, freeze:
   - deterministic UUID/idempotency identity;
   - issue packet SHA-256;
   - writer SHA-256;
   - writer test SHA-256;
   - dry-run log proving zero mutation.
4. Prefer Linear filter lookups for absent deterministic IDs. In this session, singular `issue(id:)` raised a GraphQL error when absent; the durable lesson is: prove absent-id behavior against the live schema in read-only mode and bind the working query/type (for example `ID!`) before live create.
5. Execute one live create/mirror only after exact writer review returns `CLEAN/PASS`; no retry unless the live result proves zero durable side effects and Michael authorizes/contract permits a retry.

## Implementation contract pattern

- Remove implicit root discovery (`PRISMATIC_WORKSPACE_ROOTS`, repo insertion, `PRISMATIC_WORKSPACE_ROOT`, `/home/ubuntu/work` child scanning) from public workspace routes.
- Use an explicit JSON registry with duplicate-key rejection, unknown-key rejection, bounded enabled entries, stable opaque IDs, bounded labels, and absolute operator-approved roots.
- Missing registry means empty public registry, not fallback discovery.
- API responses and dashboard DOM/query params may contain only `workspace_id`, labels, and relative paths. Never emit roots, host paths, path fragments, exception strings, or eager tree data.
- Preserve the canonical Hub Dashboard Workspaces tab. Do not replace it with a temporary mini-dashboard. Keep `/dashboard?workspace_id=<id>&file=<relative>` canonical and `/workspace-tree?workspace_id=<id>&file=<relative>` as contained legacy fallback.

## Filesystem boundary pattern

1. Reject malformed relative paths before filesystem access: NUL/control chars, Unicode normalization changes, `%`, backslash, absolute paths, POSIX `//`, Windows drive/UNC forms, `.`, `..`, hidden components, empty interior components, excessive component count/length.
2. Open configured roots component-by-component from `/` with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`; reject `/` itself.
3. On supported Linux, prefer `openat2` relative to the approved root FD with `RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS|RESOLVE_NO_MAGICLINKS`.
4. Decide fallback eligibility through a one-time harmless capability probe only. Do not fall back after any request-time `openat2` path/access error (`EXDEV`, `ELOOP`, `ENOTDIR`, `EACCES`, `EPERM`, etc.).
5. Fallback is component-wise `os.open(..., dir_fd=..., O_NOFOLLOW|O_CLOEXEC)` with `O_DIRECTORY` on intermediate directories.
6. For preview, authorize the already-open FD with `fstat`: regular file only and `st_nlink == 1`; reject symlinks, directories, FIFOs, sockets, devices, hardlinks, growing/oversize, NUL bytes, non-UTF-8, hidden/sensitive names.
7. Read from the already-open FD only; never reopen by string path after validation.
8. Close FDs on every success/failure path.

## Verification packet

```text
COMMAND=<exact focused tests/build/openat2 probe/dry-run>
RESULT=<PASS|BLOCKED>
LOG=<path>
SCOPE=opaque workspace boundary preparation
AD_HOC_OR_CANONICAL=ad-hoc targeted unless full suite run separately
LINEAR_MUTATED=<true|false>
REGISTRY_MUTATED=<true|false>
SOURCE_MUTATED=<true|false>
WORKTREE_CREATED=<true|false>
DEPLOYMENT_AUTHORIZED=false
PUBLIC_UNBLOCK_AUTHORIZED=false
NOT_CLAIMING=deployment,Nginx unblock,access-control acceptance,canonical green unless separately proven
MARKER=PRISMATIC_PHASE2_OPAQUE_WORKSPACE_BOUNDARY_GATE
```

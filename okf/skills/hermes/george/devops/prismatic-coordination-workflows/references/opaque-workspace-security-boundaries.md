# Opaque workspace security boundary contracts

Use this reference when coordinating Prismatic dashboard/workspace-tree security work where public APIs currently expose filesystem paths or accept path-like selectors.

## Contract principles

- Preserve the existing canonical Hub Dashboard Workspaces tab; do not replace it with a mini/fallback dashboard.
- Public API selectors must be opaque workspace IDs plus relative paths, not absolute paths or reversible path-derived tokens.
- Prefer IDs shaped like `ws-<32 lowercase hex>`: server/operator-assigned, stable, non-semantic, and non-reversible.
- Registry input should be a file path from explicit service configuration, not inline JSON in an environment value and not implicit discovery from repo roots or `/home/ubuntu/work`.
- Treat missing registry config as an empty workspace list; treat invalid/unsafe registry config as fail-closed generic 503.
- Registry files should be opened with no symlink following, bounded size, strict UTF-8, duplicate-key detection, exact known keys, safe owner/mode checks, and bounded collection size.
- Open configured roots component-by-component from `/` with directory FDs and no symlink following; hold approved root FDs for the request so path replacement cannot retarget reads.
- On supported Linux, prefer `openat2` with beneath/no-symlink/no-magic-link/no-cross-device style restrictions. Decide fallback eligibility only through a harmless one-time capability probe; never fall back after a request-time access denial.
- Authorize opened objects by `fstat`, not by string resolution. Reject symlinks, devices, sockets, FIFOs, directories for preview, multiple hardlinks, oversized/growing files, non-UTF-8 preview content, NULs, percent/backslash/drive/UNC/absolute/dot traversal variants, and NFKC tricks.
- Response bodies, HTML, links, DOM data attributes, console logs, and errors must not include registry paths, configured roots, parent path components, or JSON keys like `root`/absolute `path`.

## Dashboard-specific checks

- Hydrate workspace cards with only ID/name; lazy-load root trees.
- Keep `selectedWorkspaceId` and `selectedRelativePath` separate in dashboard state.
- Use escaped data attributes and event delegation instead of inline path-bearing `onclick` strings.
- Canonical deep link: `/dashboard?workspace_id=<id>&path=<relative>#workspaces`; legacy fallback may mirror the same opaque ID + relative path.
- Remove path-only links in other tabs, such as Merge-tab audit links; point them to safe Workspaces navigation until a valid opaque ID exists.
- Rebuild generated dashboard templates with the canonical build script and prove deterministic `--check` parity.

## Proof expectations

- Focused adversarial API tests plus dashboard source-split/generation tests.
- Canonical suite comparison against exact base if failures remain.
- Git-free archive reproduction of the candidate.
- Wheel inspection and non-editable install smoke tests so production packaging does not depend on the mutable source checkout.
- Browser-rendered desktop and mobile proof covering Workspaces tab, deep links, malicious label/filename escaping, absence of injected handlers/elements, console errors, and overflow.
- Production containment proof remains separate from implementation proof; keep Nginx blocks active until a deployment phase is explicitly authorized and verified.

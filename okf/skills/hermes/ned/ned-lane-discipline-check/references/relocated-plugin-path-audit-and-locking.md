# Relocated Plugin Paths: Audit and Locking

## Problem

A migration/extraction prompt can name a historical path while `origin/main` has moved the component. In the PWP extraction audit, historical PR paths were `plugins/pwp/...`, but current main carried exact retained blobs under `prismatic/shipped_plugins/pwp/...`.

## Safe procedure

1. Resolve the historical path in the authoritative ref with `git ls-tree -r origin/main -- <path>`.
2. If absent, find the current component location and record both historical and current paths in the audit.
3. Before any write, lock the actual destination path with `swarm.js lock <current-path> ned`; a lock on the historical path does not cover a relocated write.
4. Build a blob-to-current-tree mapping. An exact PR blob found anywhere in current main is **superseded**, even if the pathname changed.
5. Keep repo-root CLI shims and PE-specific adapters outside the standalone plugin import. Classify them as separate PE integration work.

## Audit output rule

Enumerate every unique historical plugin path, with one classification each. Include current-main SHA, PR head, merge base, and relevant relocation commit. Do not merge, close, or wholesale cherry-pick the stale branch.

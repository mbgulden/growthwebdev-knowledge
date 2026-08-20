---
name: prismatic-plugin-architecture
description: "Design, extend, verify, and document Prismatic Engine plugin architecture, including manifests, loader contracts, Gateway/dashboard surfaces, MCP integration, artifacts, policy, and installed-distribution portability."
triggers:
  - Prismatic Engine plugin architecture
  - PE plugin manifest
  - plugin loader
  - plugin catalog
  - MCP plugin integration
  - shipped plugin packaging
  - installed wheel plugin discovery
  - Asset Forge 3D integration
  - Prismatic Video plugin
  - Prismatic Images plugin
  - Prismatic Music/SFX plugin
  - Prismatic Game Assets plugin
  - plugin development path
---

# Prismatic Plugin Architecture

Use this skill when Michael asks to make, review, extend, package, or verify the Prismatic Engine plugin system or a domain plugin that must integrate deeply without becoming PE Core.

## Core principle

PE Core owns orchestration, lifecycle, Gateway/API, dashboard visibility, governance, state, plugin discovery, and agent/tool discovery. Plugins own domain implementation: media generation, 3D asset forging, service APIs, schemas, provider credentials, MCP servers, artifacts, and workflows.

A plugin can be deeply integrated and still removable. Disconnecting or disabling it must not delete artifacts or break unrelated PE services.

## Proven integration path

For a new or repaired plugin class, drive toward this contract:

1. **Manifest** — `plugin-manifest.yaml` with schema/version/name/entry point/core constraint and domain fields.
2. **Plugin class** — subclass `PrismaticPlugin`; implement `on_init()` and `register_tools()`.
3. **Discovery hooks** — implement only what applies:
   - `capability_contract()`
   - `connection_contract()`
   - `register_mcp_servers()`
   - `register_api_routes()`
   - `register_artifact_types()`
4. **MCP/service bridge** — declare transport, resources, tools, and redacted auth environment-variable names.
5. **API/dashboard** — expose status/job/asset/control surfaces through Gateway/dashboard, or declare the planned surfaces before claiming readiness.
6. **Artifact/provenance** — durable IDs, MIME/artifact types, lineage, and export rules are contractual.
7. **Governance** — policy preview, approval gates, secret redaction, unknown-plugin blocking, and destructive-action boundaries must be explicit.
8. **Validation** — exercise catalog, validate, blueprint/scaffold, load gate, policy allow/block, and failure paths.
9. **Documentation** — document exact commands, connect/disconnect semantics, runtime requirements, and non-claims.

## Important PE files

- `prismatic/interface/plugin.py` — plugin base class and optional discovery hooks.
- `prismatic/core/registry.py` — loader and capability validation.
- `prismatic/plugin_architecture.py` — manifest parser, validation, catalog, discovery, blueprints, and scaffolding.
- `prismatic/plugin_policy.py` — policy allow/block/approval behavior.
- `prismatic/plugin_artifacts.py` — artifact/provenance safety and storage.
- `prismatic/quality/plugin_load.py` — ship-time plugin load gate.
- `scripts/plugin_architecture` — catalog/validate/blueprint/scaffold CLI.
- `prismatic/gateway/server.py` — generic plugin API surfaces.
- `docs/prismatic-plugin-architecture.md` — canonical product documentation.
- `docs/plugin-blueprints/` — non-live future plugin blueprints.

## Future media/service classes

- `video` — Prismatic Video
- `images` — Prismatic Images
- `music-sfx` — Prismatic Music/SFX
- `game-assets` — Prismatic Game Assets
- `asset-forge-3d` — external app/service with HTTP MCP integration

Asset Forge 3D should use environment-backed redacted credentials, an HTTP MCP endpoint, durable jobs/assets/exports, and Gateway/dashboard status surfaces.

## Standard execution workflow

1. Confirm whether the change belongs in PE Core, a shipped plugin, or an external operator plugin.
2. Inspect the current manifest, loader, catalog, policy, artifact, API, dashboard, package-data, and CI surfaces before editing.
3. Preserve canonical product assets and existing adapters; use path-level changes rather than rewrites.
4. Define acceptance criteria for manifest validation, discovery boundary, load success, policy allow/block, artifacts, API/dashboard visibility, and packaging.
5. Implement centrally through plugin architecture/registry/policy contracts; avoid endpoint-specific or plugin-name-specific bypasses.
6. Add a successful path and a fail-closed path. Unknown, duplicate, malformed, secret-bearing, or destructive requests must not silently pass.
7. Verify locally, independently review the exact artifact, require exact-head CI, and separate source proof from release/installed-distribution proof.
8. Merge only after exact-head review and CI under the active authorization policy. Deployment remains a separate gate.

## Scripts-repo curator/verifier reconciliation

When a helper/orchestrator scripts branch appears to add PE curator, verifier, janitor, cron, worktree, or cleanup capabilities, treat it as built-first reconciliation rather than ordinary merge cleanup:

1. Freeze exact branch/head/tree/base/ahead count, changed paths, dirty state, untracked paths, and remote/PR authority before reviewing.
2. If the shared checkout is dirty, review immutable Git objects or archives; do not normalize the shared checkout to make review easier.
3. Compare any vendored `prismatic` or curator package against canonical PE modules and the master plan before promoting it.
4. Reject wholesale merge for heterogeneous branches. Preserve the branch and extract clean, coherent slices from `main` with exact-head review.
5. Keep workspace selection and Python package authority separate: AGY `--dir` must not decide which curator bytes are imported.
6. Prefer a pinned, fail-closed supervisor adapter over vendoring PE packages into scripts repos.
7. Put profile-specific health checks in a removable Hermes-operations adapter/plugin that emits deterministic read-only findings; PE Core owns lifecycle/policy/artifacts/dashboard visibility; curator classifies/routes; action broker governs cleanup. Use injected roots, direct JSON/text inspection for scheduler/profile state, and read-only invariance proofs; do not import loaders that can auto-repair/write during health snapshots.
8. For read-only operations plugins, harden the checker as adversarial infrastructure: disable Git optional locks/fsmonitor, treat active SQLite WAL as a warning boundary rather than stale truth, reject symlink/path escapes and dangling-symlink false passes, hash/redact arbitrary IDs/paths/field names, enforce finite scan/time limits, and make registered tools call the same reviewed runner.
9. Cron durability plugins must be non-authoritative unless explicitly promoted: produce deterministic redacted history, atomic private `0700`/`0600` snapshots outside live authority, no-overwrite writes, authority digest/tamper checks, and restore/readback plans only. Never patch Hermes `jobs.json` directly from PE helper code. Treat scheduler authority JSON as hostile raw text: parse with duplicate-key rejection at root/job/nested/envelope levels before schema validation, including escaped Unicode key collisions, so the validated object cannot differ from the source bytes.
10. Deletions, VACUUM/reclaim, service restarts, branch publication, merges, and Linear writes remain separate explicit approval gates.

See `references/scripts-repo-curator-reconciliation-2026-07-31.md` for the session-specific review sequence, curator-adapter contract, and cleanup pitfalls.
See `references/hermes-operations-health-plugin-readonly.md` for the reusable read-only Hermes operations health plugin pattern.
See `references/read-only-ops-and-cron-durability-hardening-2026-07-31.md` for adversarial review lessons covering Git/SQLite/path/redaction limits and non-authoritative cron snapshots.
See `references/read-only-health-race-hardening-2026-07-31.md` for the deeper health-plugin race hardening pattern: killable helper process groups, bounded IPC cleanup, conservative live SQLite/WAL identity fences, and stale-claim suppression.
See `references/descriptor-bound-sqlite-and-pgid-health-hardening.md` for the exact hardened inspection pattern: hold an `O_NOFOLLOW` SQLite descriptor and connect through `/proc/self/fd`, revalidate DB/WAL identity before surfacing metrics, and use `waitid(...WNOWAIT)` before same-PG cleanup so success-path descendants cannot leak.
See `references/cron-durability-duplicate-json-keys.md` for the durable raw-JSON parser hardening pattern: reject duplicate keys before schema validation, including escaped-key collisions.

## Foundation-runway sequencing after recovery

When PE has just exited an emergency repair/recovery phase, switch from isolated repair prompts to a foundation runway before launching more implementation slices:

1. Clean the handoff into a current-state page plus historical evidence index; do not sequence from superseded historical sections.
2. Create one Linear project/backlog for the foundation program, but keep only one issue at a time Ready/In Progress.
3. Start with a no-code current-state architecture/source-of-truth ADR before product or plugin implementation.
4. For dashboard/UI work, require an approved operator UX master plan and visual baseline before visual QA or CSS nits become acceptance criteria.
5. Preserve cap-1, event-driven admission, exact binding, independent review, immutable release proof, and separate merge/deploy authorization.
6. Avoid adding new wrappers, receipt schemas, or manual dispatch ceremony when the right fix is convergence onto the canonical run state machine.
7. Use risk-tiered verification: exact-head/local/release/browser/production proof as needed, but do not require a giant browser evidence packet for every low-risk foundation document change.

See `references/pe-foundation-runway-after-recovery-2026-07-27.md` for a concrete PE Foundation 1.0 issue sequence and acceptance boundaries.

## Installed-distribution portability

Use this workflow whenever shipped plugins must work outside a source checkout:

1. **Package boundary** — put manifests, runtime modules, fixtures required at runtime, and shipped assets beneath an importable package resource boundary. Include them in wheel and sdist package data.
2. **Discovery semantics** — explicit `plugins_dir` and `PRISMATIC_PLUGINS_DIR` remain exclusive boundaries unless an additive model is deliberately specified. A missing override must not silently fall back. Duplicate names must fail closed rather than use first-match ordering.
3. **Compatibility path** — if a source-only compatibility symlink is retained, verify its Git mode, target, and checkout resolution. Do not assume it survives sdist creation.
4. **Clean-room wheel** — build a wheel; install it non-editably in a fresh venv with required runtime extras; remove `PYTHONPATH`; use an empty CWD.
5. **Import isolation** — assert `prismatic.__file__` resolves beneath the fresh venv prefix. Source-side smoke harnesses may be reused only when source-path injection is disabled in installed-prefix mode.
6. **Installed behavior** — run catalog, load gate, policy allow, unknown-plugin block, public-launch smoke, release smoke, and security readiness using the installed interpreter.
7. **Archive inspection** — inspect wheel and sdist members independently for required manifests/modules/assets and unintended symlinks.
8. **CI parity** — install all extras required by repository `conftest.py`, Gateway imports, and smoke scripts. Trigger paths must include the packaged resource directory plus discovery/policy/load files—not only a legacy top-level plugin path.
9. **Proof boundary** — a controlled suite with unrelated live-network tests deselected is not canonical full green. Require exact-head GitHub CI before merge.
10. **Release proof** — after merge, create a standalone no-alternates release checkout and rerun focused, clean-room wheel, readiness, release/security, static/build, and controlled canonical proof before claiming publishable distribution.

## Verification pattern

At minimum, adapt and run:

```bash
python3 -m py_compile \
  prismatic/plugin_architecture.py \
  prismatic/interface/plugin.py \
  prismatic/core/registry.py \
  prismatic/gateway/server.py

python3 -m pytest -q \
  tests/test_plugin_architecture.py \
  tests/test_plugin_policy.py \
  tests/test_plugin_load_gate.py \
  tests/test_plugin_artifacts.py

python3 -m prismatic.quality.plugin_load
python3 scripts/plugin_architecture catalog
python3 scripts/release_check.py
python3 scripts/public_security_readiness_audit.py
git diff --check
```

For packaging changes, also run the repository's clean-room installed-wheel test and fresh-install distribution readiness command. Build/test operations that share `dist/`, egg-info, or source-generated metadata should run serially.

## Verification output discipline

- Put verbose pytest/build/audit output in `/tmp/<agent>-<issue>-verify.log` or a durable artifact.
- Chat/Linear receives a compact packet: `COMMAND`, `RESULT`, `LOG`, `SCOPE`, `AD_HOC_OR_CANONICAL`, `NOT_CLAIMING`, `MARKER`.
- Distinguish ad-hoc targeted checks, controlled suites, exact-head GitHub CI, standalone release proof, browser proof, and production proof.
- If a check fails, report the exact command, one-line cause, log path, and repair gate; never convert a partial run into a canonical claim.
- Load `compact-verification-output` for reusable proof-packet details.

## Pitfalls

- Do not treat blueprint generation as a working integration.
- Do not claim API/dashboard integration from manifest declarations alone.
- Do not expose raw credentials; publish only redacted environment-variable names.
- Do not add provider-specific logic to PE Core when a generic plugin hook suffices.
- Do not make external services or MCP servers mandatory for PE startup.
- Do not confuse a sample plugin with production-ready policy, artifact, and lifecycle behavior.
- Do not present mock/sample/no-op dashboard data as live truth.
- Do not let shipped plugins shadow operator overrides or duplicate external names.
- Do not validate installed-wheel behavior from the source CWD or with source `PYTHONPATH` injection.
- Do not assume wheel success proves sdist, source symlink, CI dependency, or fresh-host behavior.
- Before classifying canonical `pip wheel`/installed-wheel failures as package defects, verify the exact test interpreter has pip (`<python> -m pip --version`). A `uv venv` can be valid yet pip-less, causing tests that invoke `sys.executable -m pip` to fail before wheel construction. Hydrate only the disposable verification venv with `<python> -m ensurepip --upgrade`, rerun the exact failed tests, confirm the Git worktree stayed clean, then rerun canonical.
- Do not run unrelated live-network Lighthouse/browser tests inside an isolated plugin packaging gate.

## Supporting references

Load only the reference relevant to the current task:

- `references/CONSOLIDATION_MAP.md` — audit map from the former oversized main file to the themed supporting references, including source ranges and checksums.
- `references/governance-security-and-public-readiness.md` — governance summaries, durable jobs, artifacts, policy, public security, and launch onboarding.
- `references/planning-audits-and-release-candidates.md` — OKF/North Star audits, rubric planning, cohesive integration, and RC loops.
- `references/agent-dispatch-control-and-production-durability.md` — Telegram/filesystem dispatch, audit control planes, agent context packs, polling recovery, and production durability.
- `references/merge-governance-and-pr-triage.md` — completed-work integration boundaries and noisy PR cleanup.
- `references/pwp-dashboard-and-ingestion-integration.md` — PWP lifecycle, Workspace Tree/dashboard preservation, visual QA, and ingestion follow-ups.
- `references/release-engineering-and-verification.md` — release engineering, compact proof discipline, verification commands, and historical pitfalls.

The skill directory also contains granular historical references for specific audits, dispatch repairs, dashboard preservation, and production-readiness slices. Use `skill_view(name='prismatic-plugin-architecture', file_path='references/<file>.md')` only when that exact topic is needed.

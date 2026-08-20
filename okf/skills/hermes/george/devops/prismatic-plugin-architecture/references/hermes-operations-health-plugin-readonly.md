# Read-only Hermes operations health plugin pattern

Session pattern: implementing a Prismatic shipped plugin that inspects Hermes profile operational health without becoming a second scheduler authority and without mutating profile state.

## Durable design rule

Profile-specific Hermes operational checks belong in a removable adapter/plugin. PE owns lifecycle, policy, artifacts, dashboard visibility, and routing. The plugin emits deterministic read-only findings; it does not remediate, delete, compact, restart services, publish branches, write Linear, or patch Hermes scheduler state.

## Implementation constraints

- Accept injected roots such as `profile_root`, `cron_root`, `state_root`, and optional repository root. Do not hard-code the active agent profile.
- Normalize and reject traversal/relative-root escapes; release/profile roots must be existing directories where appropriate.
- Treat Hermes `cron/jobs.json` as scheduler authority. Snapshot/verify its shape, duplicate job IDs, and migration/path signals, but do not patch it directly.
- Avoid importing Hermes scheduler loader functions during read-only checks when the loader can auto-repair or persist. Inspect JSON/text directly for health snapshots.
- Findings should be deterministic JSON: stable IDs, status, severity, path-safe detail, and summary counts.
- Expose plugin metadata through the standard shipped-plugin surfaces: `plugin-manifest.yaml`, `PrismaticPlugin` subclass, `capability_contract()`, and `register_tools()` if needed.
- Package the plugin under an importable package resource boundary and verify the wheel contains `__init__.py`, runtime modules, manifest, and README.
- Keep the package marker (`__init__.py`) side-effect-light. Do not eagerly import runnable modules if that creates import-order or `runpy` warnings when using `python -m`.

## Verification checklist

- Fixture-driven tests cover healthy path, malformed input, duplicate cron IDs, path migration semantics, traversal rejection, state DB thresholds, manifest/plugin schema, and read-only invariance.
- Live canary against a real profile is allowed only read-only: record before/after DB/WAL/cron/state metadata or file hashes and assert invariance.
- Run plugin architecture/load-gate tests plus focused plugin tests.
- Run `ruff check`, `ruff format --check`, `git diff --check`, and a clean immutable-archive wheel build (`git archive <head> | tar -x ...; uv build --wheel ...`).
- Classify any live-profile warnings as findings, not repairs.

## Non-claims

Passing this pattern does not imply canonical full-suite green, scheduler restore authority, cleanup authorization, deployment, or production dashboard visibility. Those remain separate gates.

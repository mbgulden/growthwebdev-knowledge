## Release engineering layer

Gap 6 public release engineering is implemented. Use these surfaces for release/package work:

- `scripts/release_check.py` — local release-readiness checker; expected marker `RELEASE_READINESS_OK`.
- `scripts/release_smoke.py` — release-level smoke composing CLI metadata, plugin load gate, public launch smoke, and security audit; expected marker `RELEASE_SMOKE_OK`.
- `docs/release-process.md`, `docs/release-checklist.md`, `docs/migrations.md`, `docs/upgrade-guide.md`, and `docs/stable-cli-entrypoints.md` are the public release docs.
- `config/prismatic.sample.yaml` is the public sample config; `scripts/bootstrap_env.sh` bootstraps a local release/dev environment.
- `Dockerfile` and `.devcontainer/devcontainer.json` are local/dev smoke surfaces, not production deployment recipes.
- CI matrix lives in `.github/workflows/test.yml` and covers Python 3.10, 3.11, 3.12, and 3.13 plus release checks/smoke/build. Keep lint scoped to the release/public surface unless the historical lint backlog is deliberately being fixed.
- Publish workflow lives in `.github/workflows/publish.yml`; it verifies tag/version match, runs release checks/smoke/security, builds, twine-checks, uploads artifacts, attests provenance, and publishes on `v*` tags or explicit workflow dispatch.
- Keep `pyproject.toml` `[project].version` and `prismatic.__version__` identical. Python 3.10 needs the `tomli` dependency/fallback for TOML parsing scripts; Python 3.11+ uses `tomllib`.

Release verification pattern:

```bash
python scripts/release_check.py
python scripts/release_smoke.py
python scripts/public_launch_smoke.py
python scripts/public_security_readiness_audit.py

python -m pytest tests/test_plugin_load_gate.py tests/test_public_security_readiness.py prismatic/quality/test_smoke.py -q
python -m ruff check prismatic/__init__.py scripts/release_check.py scripts/release_smoke.py scripts/public_launch_smoke.py scripts/public_security_readiness_audit.py tests/test_plugin_load_gate.py tests/test_public_security_readiness.py prismatic/quality/test_smoke.py
python -m ruff format --check prismatic/__init__.py scripts/release_check.py scripts/release_smoke.py scripts/public_launch_smoke.py scripts/public_security_readiness_audit.py tests/test_plugin_load_gate.py tests/test_public_security_readiness.py prismatic/quality/test_smoke.py
python -m build
python -m twine check dist/*
```

On PEP-668 externally managed hosts, run build/twine inside a temp venv and remove it afterward.

## Verification output discipline

For Fred/Ned/AGY/Kai prompts and self-run verification, keep verification conversation-safe:

- Detailed verifier, pytest, build, browser, audit, and detector logs go to `/tmp/<agent>-<issue>-verify.log` or a durable artifact file.
- Chat/Linear gets only a compact proof packet: `COMMAND`, `RESULT`, `LOG`, `SCOPE`, `AD_HOC_OR_CANONICAL`, `NOT_CLAIMING`, and `MARKER`.
- Run verification before the final answer, but write the final human-readable packet after the compact marker block so detector output does not cut off the actual message.
- If a check fails, include only the failing command, one-line error summary, log path, and next required fix; do not paste full logs unless Michael asks.
- For reusable details, load the `compact-verification-output` skill.

## Verification pattern


Do not stop at docs or a manifest. For plugin architecture changes, verify at least:

```bash
python3 -m py_compile prismatic/plugin_architecture.py prismatic/interface/plugin.py prismatic/core/registry.py prismatic/gateway/server.py tests/test_plugin_architecture.py
python3 -m pytest tests/test_plugin_architecture.py tests/test_plugin_loader_capability_validation.py tests/test_plugin_load_gate.py tests/test_pwp_integration.py -q
python3 scripts/plugin_architecture catalog
python3 scripts/plugin_architecture blueprint asset-forge-3d --class asset-forge-3d
python3 scripts/plugin_architecture validate docs/plugin-blueprints/asset_forge_3d/plugin-manifest.yaml
```

Also smoke the plugin load gate via Python API and Gateway TestClient endpoints:

- `verify_shipped_plugins_load(plugins_dir=Path('plugins'), core_version='0.2.0')`
- `GET /api/plugins/catalog`
- `GET /api/plugins/architecture`

When the system asks for explicit ad-hoc verification, create a temp `/tmp/hermes-verify-*` script with `tempfile`, run exact changed paths, clean it up, and label the result as ad-hoc verification rather than canonical suite green.

## Pitfalls


- Do not put incomplete future plugins under `plugins/`; put blueprints under `docs/plugin-blueprints/` until the implementation passes the live plugin load gate.
- Do not hardcode secrets in manifests. Store env var names and redacted status only.
- Do not create one-off endpoints for every plugin before adding generic catalog/discovery surfaces.
- Do not claim plugin architecture is “done” unless there is code, docs, tests, CLI/API proof, and a proven path for at least one future plugin class.
- For external service plugins, MCP descriptors should name resources/tools and auth env vars but not store token material.

## References

- `references/media-asset-forge-plugin-path-2026-07-12.md` — session-derived details for the media/Asset Forge 3D proven path and verification checklist.
- `references/agy-jules-context-pack-followup-prompt-2026-07-19.md` — prompt-packaging lesson for pivoting from merged AGY/Jules context-pack PRs to `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK` with Telegram `.md` artifact verification.
- `references/current-state-prismatic-engine-agent-lane-2026-07-19.md` — Kai handoff with current Prismatic Engine agent-lane state, runtime routes, Linear roadmap identifiers, PR #329 status, and George verification responsibilities.

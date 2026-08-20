# Media and Asset Forge 3D plugin path — 2026-07-12

## Context

Michael asked for Prismatic Engine Core to have a comprehensive, easy, proven path for future plugins:

- Prismatic Video
- Prismatic Images
- Prismatic Music/SFX
- Prismatic Game Assets
- Asset Forge 3D as its own app/website/service that fully integrates into PE for AI-agent automation, likely via MCP

The resulting architecture was shipped in PE PR #231 and verified on `main` at `8d428df2`.

## Durable pattern

Future media/service plugins should not be bespoke sidecars. They should use the core path:

1. Define `plugin-manifest.yaml`.
2. Implement a `PrismaticPlugin` subclass.
3. Implement optional discovery hooks for capabilities, connection semantics, MCP, API routes, and artifact types.
4. Validate/scaffold/catalog with `scripts/plugin_architecture`.
5. Use `docs/plugin-blueprints/` for non-live future blueprints; only move under `plugins/` when live plugin load gate passes.
6. Expose PE Gateway and dashboard surfaces for operator visibility.
7. Store only redacted credential env var names in manifests/status.
8. Emit durable asset/job/export IDs and provenance.

## Core implementation pieces

- `prismatic/plugin_architecture.py`
  - `MEDIA_CAPABILITY_CLASSES`
  - `future_plugin_blueprint()`
  - `write_blueprint()`
  - `plugin_catalog()`
  - manifest validation
- `scripts/plugin_architecture`
  - `catalog`
  - `validate`
  - `blueprint`
  - `scaffold`
- `prismatic/interface/plugin.py`
  - `capability_contract()`
  - `connection_contract()`
  - `register_mcp_servers()`
  - `register_api_routes()`
  - `register_artifact_types()`
- `prismatic/core/registry.py`
  - records `registered_mcp_servers`, `registered_api_routes`, `registered_artifact_types`, `registered_capability_contracts`
- `prismatic/gateway/server.py`
  - `GET /api/plugins/catalog`
  - `GET /api/plugins/architecture`

## Asset Forge 3D pattern

Asset Forge 3D should be represented as an external-service plugin:

```yaml
plugin_type: external-service
external_service:
  name: Asset Forge 3D
  kind: external-app-service
  base_url_env: ASSET_FORGE_3D_BASE_URL
  api_key_env: ASSET_FORGE_3D_API_KEY
  webhook_secret_env: ASSET_FORGE_3D_WEBHOOK_SECRET
mcp_servers:
  - name: asset-forge-3d-mcp
    transport: http
    url: ${ASSET_FORGE_3D_MCP_URL}
    auth_env:
      - ASSET_FORGE_3D_API_KEY
    resources:
      - asset_forge.jobs
      - asset_forge.assets
      - asset_forge.scenes
      - asset_forge.exports
    tools:
      - forge_3d_asset
      - retopologize_mesh
      - bake_textures
      - rig_model
      - export_3d_asset
```

Recommended durable IDs:

- `afg_job_<id>`
- `afg_asset_<id>`
- `afg_export_<id>`

Recommended artifact types:

- `model/gltf-binary`
- `model/gltf+json`
- `application/x-fbx`
- `application/x-blender`
- `application/x-prismatic-asset-forge-job+json`

## Verification checklist

For future plugin-architecture work, verify at minimum:

```bash
python3 -m py_compile prismatic/plugin_architecture.py prismatic/interface/plugin.py prismatic/core/registry.py prismatic/gateway/server.py tests/test_plugin_architecture.py
python3 -m pytest tests/test_plugin_architecture.py tests/test_plugin_loader_capability_validation.py tests/test_plugin_load_gate.py tests/test_pwp_integration.py -q
python3 scripts/plugin_architecture catalog
python3 scripts/plugin_architecture blueprint asset-forge-3d --class asset-forge-3d
python3 scripts/plugin_architecture validate docs/plugin-blueprints/asset_forge_3d/plugin-manifest.yaml
```

Also verify:

```python
from pathlib import Path
from prismatic.quality.plugin_load import verify_shipped_plugins_load
result = verify_shipped_plugins_load(plugins_dir=Path('plugins'), core_version='0.2.0')
assert result.passed
```

Gateway smoke:

- `GET /api/plugins/catalog` returns 200 and contains media capability classes.
- `GET /api/plugins/architecture` returns 200 and includes `asset-forge-3d`.

## Session pitfall captured

When doing CLI smoke tests involving JSON output, do not pipe JSON into a Python heredoc that consumes stdin; write command output to a temp file and have Python read the file path. The failed command pattern was transient, but the durable lesson is to use temp files for shell heredoc + JSON parsing smoke checks.

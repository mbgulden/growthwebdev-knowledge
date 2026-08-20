# PWP as a first-class additive Prismatic Engine plugin (2026-07-12)

Use this pattern when PWP needs to be more than a repo-local helper: it should be a distinct, removable plugin that gives Prismatic Engine more website-production capabilities, visibility, workflows, and governance without becoming PE core.

## Target contract

```text
PE core stays foundational.
PWP remains distinct and removable.
PWP gives PE more capabilities, visibility, workflows, tools, and governance.
Connect/disconnect is explicit, reversible, and dashboard-visible.
Agents discover PWP capabilities through PE APIs/CLI, not tribal memory.
```

## Production integration shape

Add/verify these pieces together:

1. **PWP manifest contract** — `plugins/pwp/plugin-manifest.yaml`
   - explicit version bump
   - `capabilities:` list
   - `connect_points:` list
   - `disconnect_points:` list
   - governance notes such as secret redaction and additive-only behavior

2. **PWP plugin methods** — `plugins/pwp/plugin.py`
   - `capability_contract()` returns what PWP contributes
   - `connection_contract()` returns connect/disconnect semantics
   - existing registered tools stay intact, e.g. `pwp_credentials_refresh`, `pwp_credentials_status`

3. **PE-owned bridge/state** — `prismatic/pwp_integration.py`
   - durable state under `$PRISMATIC_STATE_DIR/pwp_integration.json`
   - `integration_status()` returns manifest, capabilities, tools, workflows, governance, blockers
   - `connect_pwp()`, `disconnect_pwp()`, `refresh_pwp()` mutate state
   - production blockers are explicit and secret-safe

4. **Gateway API** — `prismatic/gateway/server.py`
   - `GET /api/pwp/status`
   - `POST /api/pwp/connect`
   - `POST /api/pwp/disconnect`
   - `POST /api/pwp/refresh`

5. **Dashboard surface** — `prismatic/gateway/templates/dashboard.html`
   - `PWP Plugin` tab
   - status cards, blockers, capability cards
   - connect/disconnect/refresh controls
   - connect/disconnect points and tool/workflow badges

6. **CLI surface** — `scripts/pwp`
   - `python3 scripts/pwp integration status`
   - `python3 scripts/pwp integration connect`
   - `python3 scripts/pwp integration disconnect`
   - `python3 scripts/pwp integration refresh`

7. **Docs/tests**
   - doc: `docs/pwp-pe-plugin-integration.md`
   - tests: `tests/test_pwp_integration.py`

## Safe disconnect semantics

Disconnecting PWP must not delete anything:

- no plugin code deletion
- no generated artifact deletion
- no PE queue/native-cron/dashboard shutdown
- only marks PWP additive readiness inactive so agents/operators do not claim PWP governance is active

## Verification checklist

Focused verification should cover:

```bash
python3 -m py_compile prismatic/pwp_integration.py prismatic/gateway/server.py plugins/pwp/plugin.py
python3 -m pytest \
  tests/test_pwp_integration.py \
  tests/test_pwp_hooks.py \
  plugins/pwp/tests/test_oauth_credentials.py \
  plugins/pwp/tests/test_theme_validator.py \
  plugins/pwp/tests/test_theme_diff.py -q
```

Smoke CLI/API behavior with isolated state:

```bash
TMP=$(mktemp -d /tmp/pe-pwp-smoke-XXXXXX)
export PRISMATIC_PWP_INTEGRATION_STATE="$TMP/pwp_state.json"
python3 scripts/pwp integration status
python3 scripts/pwp integration connect
python3 scripts/pwp integration disconnect
```

API smoke with `TestClient` should assert:

- `GET /api/pwp/status` → 200
- `POST /api/pwp/connect` → 200 and `connected: true`
- `POST /api/pwp/refresh` → 200
- `POST /api/pwp/disconnect` → 200 and `state: disconnected`

After merge, run `python3 scripts/pwp integration connect` from `main` so PWP is actually connected in PE state, then run a fresh `/tmp/hermes-verify-*` exact-path ad-hoc verifier.

## Pitfalls

- Do not build a parallel plugin framework. PE already owns plugin loading/lifecycle/dashboard; PWP should plug into those surfaces.
- Do not infer PWP capabilities only from docs or implementation files. Make them machine-readable in the manifest and `integration_status()` payload.
- Do not make disconnect destructive. It is a governance/readiness state, not an uninstall.
- Do not expose token material. Credential surfaces may report provider names, token lengths, status, verification metadata, and blockers only.
- If tests pass but dashboard still shows stale metadata, check whether state/registry merging preserves old metadata. Refresh safe repo metadata while preserving runtime state.

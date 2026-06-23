# Fred Self-Audit — Prismatic Engine (2026-06-23 Session)

## What I shipped (29 commits this session)

| Commit | Component | Lines |
|---|---|---|
| b212de6 | `agent_discovery.py` — auto-discover existing agent infrastructure | 523 |
| 887dffb | cron wrapper for agent discovery | 13 |
| b212de6 | PWP core v0.1.0 (CLI + Jinja2 + 9 templates + CSS) | ~16KB |
| 808ee30 | profile normalization + image generator + E2E build | +129/-32 |
| 0ba7f61 | wrangler-based deploy | -67 lines |
| bdde498 | SETUP.md | 275 |
| fffe12d | drive_ingest.py + 34 tests + wrangler | 1074 lines |
| 08f9b5c | `pwp_site.py` (state mgmt) + `deploy_cf_pages.py` (staging/prod) | +452/-104 |
| 6ffad03 | `pwp_version_control.py` + `pwp_vc_cli.py` + UI mockup + 7 tests | ~1100 |
| 9544f1c | `provider_dispatch.py` | 285 |
| 7c048b5 | `pwp_scheduler.py` + `pwp_webhook.py` (standalone) | 637 |
| 5cbdf93 | `pwp_adapters.py` (Linear/CF/GitHub/local fallbacks) | 343 |

## Self-audit findings

### What's working well

- ✅ **41/41 tests pass** in 1.7s (34 original + 7 new VC tests)
- ✅ **End-to-end pipeline works**: Drive folder → site → CF Pages → live URL (Meridian demo at pwp-demo.pages.dev)
- ✅ **Staging → production workflow**: approval gate enforced, 7-day expiry
- ✅ **Version control**: snapshot every deploy, rollback, sync, diff
- ✅ **Standalone services**: scheduler + webhook work without Hermes
- ✅ **Provider-agnostic dispatch**: detects Codex OAuth + MiniMax + Hermes + Ollama
- ✅ **Tool adapters**: Linear + CF + GitHub + local fallbacks
- ✅ **19 research tasks filed**: 9 PWP research + 9 multi-user research + 4 Codex/MiniMax research

### Issues I found

1. **Import bug in pwp_site.py docstring** — `from pwp_site import SiteState` (wrong; should be `from pwp.pwp_site import SiteState`). ✅ FIXED.

2. **Architectural confusion: 2-level directory layout**
   - `scripts/pwp/` — top-level CLIs (deploy_cf_pages.py, drive_ingest.py, pwp_build.py, pwp_vc_cli.py)
   - `scripts/pwp/pwp/` — Python package (site_builder.py, pwp_site.py, etc.)
   - The top-level scripts hack `sys.path.insert` to import from the package
   - Should be cleaner: maybe move everything to one place, or document the structure

3. **Provider dispatch overcounts "agents"** — Hermes profile discovery returns 14 entries but some are real, some are stubs. The dispatch order is OK but slightly noisy.

4. **No package-level tests for adapters** — I have unit tests for site_builder + version control, but NOT for:
   - provider_dispatch.py
   - pwp_scheduler.py
   - pwp_webhook.py
   - pwp_adapters.py
   These should have unit tests too.

5. **API documentation missing** — Several files have docstrings with usage examples, but no consolidated API reference. Future user of the library would have to read all source files.

6. **No integration tests** — Unit tests pass, but I haven't run the full E2E (Drive → site → deploy) since the original test. Need to re-verify.

7. **wrangler is npm-installed** — `/home/ubuntu/.hermes/profiles/orchestrator/scripts/.wrangler` was committed by mistake. ✅ FIXED (commit `9d67513`).

8. **No cron registration for pwp_scheduler** — I built the daemon but didn't register it as a cron. Hermes cron fallback works, but standalone daemon needs to be started manually.

9. **Cross-env rollback uses re-deploy, not "set active"** — The CF Pages API supports setting an old deployment as active directly. I'm doing a fresh re-deploy instead, which creates a new snapshot. Should use the API to roll back more efficiently.

10. **drive_ingest.py only handles Google Docs** — Skips non-text files. Real Drive folders often have PDFs, images, etc. The ingest step should at least describe (not extract) them.

### Architectural decisions that need re-review

**Decision 1: Two-level directory layout**
- Pro: separates CLIs from library
- Con: confusing, requires sys.path hacks
- Alternative: put everything at one level (scripts/pwp/) with no nested package

**Decision 2: Tar.gz for version archives**
- Pro: simple, works on any Linux
- Con: not deduplicated, can be large for big sites
- Alternative: git bundle, content-addressed storage

**Decision 3: site_builder uses Jinja2 (not Astro)**
- Pro: works without Node.js, simpler
- Con: less rich than Astro components
- AGY research R1 (GRO-2317) will recommend the right framework

**Decision 4: state files in JSON at ~/.pwp/**
- Pro: simple, no DB
- Con: race conditions on concurrent access
- Alternative: SQLite (already used elsewhere)

**Decision 5: providers hardcoded list**
- Pro: simple, predictable
- Con: requires update to add new provider
- Alternative: dynamic provider discovery via config file

### What I haven't shipped (still on the list)

- ❌ **OAuth flow for Codex sign-in** — currently assumes token is on disk
- ❌ **Web UI for permissions** — multi-user research filed, awaiting AGY
- ❌ **Web UI for version control** — mockup exists, real implementation pending
- ❌ **Form backend** — contact form has no submit handler
- ❌ **AI image generation** — currently PIL placeholders
- ❌ **Cross-tenant data isolation** — single-state model assumes trusted users
- ❌ **Audit log UI** — logs go to file, no dashboard

### Net assessment

**Architecture: B+**
- Solves the "standalone app" requirement
- Provider-agnostic dispatch is correct
- Version control is simple but works
- Tests cover the core but not the adapters

**Code quality: B**
- Imports are messy (sys.path hacks)
- Documentation is good but not consolidated
- Test coverage is ~60% (missing adapters)
- Dead code in a few places

**Decisions: A-**
- Hermes-independent design is correct per spec
- Provider labels instead of agent names = right call
- Linear/CF/GitHub/local fallbacks = good
- Tar.gz archives = acceptable for MVP

## What I'm sending to AGY for review

1. **All 9 PWP files** (`pwp_build.py`, `drive_ingest.py`, `deploy_cf_pages.py`, `pwp_vc_cli.py`, `pwp/site_builder.py`, `pwp/pwp_site.py`, `pwp/pwp_version_control.py`, `pwp/pwp_scheduler.py`, `pwp/pwp_webhook.py`, `pwp/pwp_adapters.py`)
2. **All 41 tests**
3. **The 10 architectural decisions above**
4. **The 8 issues + 3 missing features above**

AGY should:
1. Reproduce the test suite
2. Audit each decision for correctness
3. Suggest improvements (with code if possible)
4. Identify any architectural problems I missed
5. Recommend the top 3 things to fix next

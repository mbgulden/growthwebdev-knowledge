# AGY×3, Jules Capacity, Resources Tab, and Dashboard Modularization Runway

Session-derived coordination checklist for Prismatic capacity/control-plane work. Keep this as a reusable reference under the class-level Prismatic coordination skill, not as a PR-specific skill.

## AGY×3 durable control-plane review

When auditing whether AGY can really run three concurrent producers, verify **all three layers** separately:

1. **Backend capacity proof** — run isolated no-code AGY CLI canaries concurrently and require every slot to return the expected marker. This proves the CLI/account/model can sustain the target concurrency without mutating repo/Linear state.
2. **Event consumer contract** — inspect the canonical event consumer command and environment. It must request the intended slot count (currently three) and pass child-only AGY CLI environment explicitly rather than assuming supervisor HOME is authenticated.
3. **Supervisor contract** — prove preflight, launch, and relaunch paths all use the AGY child environment. Do not accept a fix that patches only preflight while worker/relaunch subprocesses still inherit the wrong HOME.

Use a no-code canonical preflight before claiming operational readiness:

```text
HOME=<supervisor-home> AGY_CLI_HOME=<authenticated-profile-home> PYTHONPATH=<release-and-venv> \
python3 - <<'PY'
import importlib.util
p='scripts/agy_sandbox_event_supervisor.py'
s=importlib.util.spec_from_file_location('sup', p)
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
ok,msg=m.preflight_agy_backend(m.DEFAULT_MODEL)
assert ok,msg
print('CANONICAL_SUPERVISOR_REAL_AGY_PREFLIGHT=PASS')
print('MODEL='+m.DEFAULT_MODEL)
print('REAL_CODE_SIDE_EFFECTS=false')
PY
```

## HOME vs AGY_CLI_HOME pitfall

AGY authentication may be profile-HOME scoped while supervisor state should stay under the machine/supervisor HOME. Preserve this distinction:

- supervisor state: `HOME=/home/ubuntu` or the active runtime owner HOME;
- AGY child auth/config: `AGY_CLI_HOME=<authenticated Hermes profile home>`;
- child subprocess env sets `HOME=$AGY_CLI_HOME` for AGY only;
- do not mutate process-wide `HOME` for the supervisor just to make AGY auth work.

For PR review, require tests or static guards covering preflight, first launch, and relaunch.

## Live repair vs durable PR overlay

If production is blocked and a live profile-script repair is necessary before the current-main PR is ready:

1. Back up the exact live files and record hashes before editing.
2. Apply the smallest live repair.
3. Restart only the service that imports the repaired files after proving zero pending events if dispatch side effects are possible.
4. Verify no real agent wakes/Linear writes occurred during restart.
5. Still port the repair into current `main` and open a focused PR.
6. After merge, create an immutable release checkout and overlay only the authorized files into production, preserving unrelated dirty runtime paths.
7. Do not claim the durable PR is production-active until target runtime hashes match the immutable release and service/API proof passes.

## Resources/Quotas/Jules dashboard audit lessons

When Michael asks about quota/Jules capacity visibility, first determine whether the tab was renamed or removed. In this session, `GCP Quotas` had been renamed to `Resources`; the UI route/API existed, but the adapter returned no fresh records.

Capacity truth requires more than a visible dashboard number:

- distinguish UI presence from live adapter freshness;
- check `/api/gateway/quota` and `/api/gateway/quota/caps` separately;
- treat `snapshot_at=null`, empty records, or adapter errors as `PARTIAL`, not healthy live quota truth;
- for Jules, do not trust a Foundation count unless it is backed by a durable ledger/API;
- CLI list commands can emit auth/client errors while returning zero, so parse stderr/body markers as well as exit code;
- `/tmp` dispatcher state is not a durable daily session ledger for a 300-session allowance.

Recommended next architecture: private durable Jules session/launch ledger + `/api/gateway/jules/capacity`, visualized inside `Resources`, while replacing misleading Foundation counts.

## Dashboard modularization sequence

For the large canonical dashboard, avoid tab rewrites. Use this order:

1. lossless source split from the existing canonical `dashboard.html`;
2. deterministic build script that regenerates byte-equivalent committed output;
3. CI guard proving generated output is current;
4. declarative tab registry;
5. tab-owned JS modules;
6. feature work such as Jules capacity/resource freshness after the split reduces collision risk.

Do not start by redesigning UI or creating a fallback mini-dashboard when a good canonical shell already exists.

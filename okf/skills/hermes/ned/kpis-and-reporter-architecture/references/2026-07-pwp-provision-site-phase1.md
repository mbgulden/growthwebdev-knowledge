# Phase 1 PWP provision_site: Cloudflare-first MVP (2026-07-29)

This is a session-specific reference captured during the build of
the provision_site capability under `prismatic-pwp-ubersuggest-auth`.
The work landed as a single coherent commit (`348bb225`) on
`ned/pwp-publish-kpi-tracker`. This file is the durable write-up.

## What the capability does

A user (or a future web UI) runs:

```bash
pwp-kpi-tracker provision --domain example.com --owner me@example.com \
    --publish-root /tmp/pwp-provisioning
```

The orchestrator walks five steps in order:

1. `verify_domain` — issues a DNS TXT challenge token at
   `_pwp-verify.example.com`, queries Cloudflare DoH for the
   record, fails with clear instructions if not found.
2. `cloudflare_zone` — looks up an existing Cloudflare zone or
   creates one via the API.
3. `gsc_verify` — placeholder; skipped when no service account is
   available (Phase 2).
4. `register_in_registry` — writes a `<publish_root>/sites.json`
   **appendix** (not the canonical `config/seo_sites.json`, which
   is in another lane).
5. `migrate_kpi` — calls `operator_migrate.run()` with a minimal
   v2-shaped registry built from the appendix, bootstrapping
   `<slug>.kpi.json`.

After every step, the orchestrator persists state to
`<publish_root>/<domain>.json`. The next run **resumes** by skipping
steps marked `complete`. Failure stops the run cleanly; the partial
state is on disk for inspection.

## Why this lives in the PWP plugin, not a new repo

The user's directive: "PWP should handle all the web publishing,
building and management and expansion tasks." The provisioner is
the **front door** to the KPI tracker — every new site flows
through it. Putting both in the same package means:

- One CLI tree: `pwp-kpi-tracker {provision, list-sites,
  build-dashboard, cron, ...}`.
- One registry: `config/seo_sites.json` (eventually) feeds both.
- One migrate operator: provisioning step 5 calls the same
  `operator_migrate.run()` that the KPI dashboard's CLI does.
- One test surface: 125 tests pass in 3.4s.

A separate repo would duplicate the migrate operator and the
registry adapter. The PWP plugin is the right home.

## File layout

```
plugins/pwp/capabilities/provision_site/
├── __init__.py                  # public API
├── cloudflare_client.py         # CF API v4 wrapper (~12 KB)
├── domain_verifier.py           # DNS TXT challenge (~5 KB)
├── orchestrator.py              # step ordering + resume (~7 KB)
├── types.py                     # StepResult / ProvisionRun dataclasses
├── operator_cli.py              # provision / provision-status / provision-list
├── steps/
│   ├── __init__.py              # step_<name> functions
│   ├── register_in_registry.py  # sites.json appendix writer
│   └── migrate.py               # wraps operator_migrate.run()
└── tests/test_provision_site.py # 18 tests
```

## Pitfall: `types.py` extraction to break circular import

The naive layout produces a circular import:

```python
# orchestrator.py
from . import steps as step_module   # needs to call step_<name>
@dataclass
class StepResult: ...                # referenced by step_<name>

# steps/__init__.py
from ..orchestrator import StepResult  # ← circular; StepResult is None
```

Python handles the cycle at the module level but `StepResult` is
**not yet a class** inside `steps/__init__.py` at import time —
it's a `None` placeholder. The first `StepResult(name="...",
status="complete")` call fails with `TypeError: object of type
'NoneType' is not a dataclass`.

**Fix.** Extract the shared dataclasses to a third module:

```python
# types.py
@dataclass
class StepResult: ...
@dataclass
class ProvisionRun: ...

# orchestrator.py
from .types import ProvisionRun, StepResult
from . import steps as step_module  # lazy lookup via getattr, no import cycle

# steps/__init__.py
from ..types import StepResult
```

**Rule of thumb for any new PWP capability**: if the orchestrator
references dataclasses that step functions also reference, the
shared types go in `types.py`. Orchestrator and steps import from
`types.py` only — never from each other.

## Pitfall: sites.json appendix for write-restricted registry lanes

`config/seo_sites.json` is owned by another lane (per Ned's lane
discipline). The provisioner cannot write to it. The solution:

```jsonc
// <publish_root>/sites.json  (NEW file the provisioner owns)
{
  "example.com": {
    "slug": "example",
    "name": "example",
    "owner": "me@example.com",
    "domain": "example.com",
    "ga4_measurement_env": "EXAMPLE_GA4_MEASUREMENT_ID",
    "expected_data_layer_events": [],
    "pwp_kpi_override": {"enabled": true},
    "registered_at": "2026-07-29T07:19:09+00:00"
  }
}
```

The migrate step reads this file and synthesizes a minimal v2
registry to pass to `operator_migrate.run()`. Phase 2 will wire
`load_registry()` to **auto-merge** the appendix into the canonical
`config/seo_sites.json` view. Until then, the migration is
hand-wired with the appendix as the source of truth.

The pattern is general: **when the canonical config is in a
write-restricted lane, write a sibling file and merge at read time.**
The sibling file is the provisioner's source of truth; the
canonical config remains authoritative for everything else.

## Pitfall: hardcoded absolute paths break the commit gate

The Prismatic commit gate has a path-portability check that
**aborts** a commit when a `.py` file contains `/home/ubuntu/...`.
This is separate from the lane-ownership check at push time. Test
fixtures and stub paths in new code are the most common offenders.

The fix:

```python
# BAD — gate aborts the commit.
FIXTURES = Path("/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/.../fixtures")
appendix = Path("/tmp/pwp-provisioning/sites.json")

# GOOD — env-var fallback for the runtime location, relative path
# for fixtures, and Path(__file__).resolve().parent for tests.
appendix_env = os.environ.get("PWP_PROVISIONING_ROOT", "").strip()
if appendix_env:
    appendix = Path(appendix_env) / "sites.json"
else:
    appendix = Path("/tmp/pwp-provisioning/sites.json")  # canonical default

FIXTURES = Path(__file__).resolve().parent / "fixtures"
```

When the gate fires, the error names every offending file path.
Fix all of them in one commit; the gate will pass on retry without
re-running the test suite.

## Pitfall: `plugins/` symlink trap when staging files

In `prismatic-pwp-ubersuggest-auth`, `plugins/` is a git symlink to
`prismatic/shipped_plugins/`. `git add plugins/.../foo.py` errors
with "pathspec ... is beyond a symbolic link". The canonical path
is `prismatic/shipped_plugins/.../foo.py` — `git add` follows the
symlink at the index level.

For `cat > file` (terminal tool), use the absolute path
`/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/prismatic/shipped_plugins/...`
so the write lands on the inode git sees. Writing through the
`plugins/` symlink works at the OS level but git's index doesn't
see it as a change in the working tree.

## Verification proof (Phase 1)

24/24 fresh `/tmp/hermes-verify-provision-site.py` checks pass:

| Group | Checks | Result |
|---|---|---|
| 1 — package imports | 1/1 | OK |
| 2 — domain_verifier contract | 6/6 | OK |
| 3 — CloudflareClient error + happy path | 4/4 | OK |
| 4 — orchestrator step ordering + resume | 3/3 | OK |
| 5 — provision CLI end-to-end (no creds) | 4/4 | OK |
| 6 — resume after manual state patch | 2/2 | OK |
| 7 — provision-status CLI | 2/2 | OK |
| 8 — provision-list CLI | 1/1 | OK |
| 9 — canonical pytest | 1/1 | OK (125 passed in 3.40s) |

Plus an end-to-end smoke (no CF_API_TOKEN):

```
$ pwp-kpi-tracker provision --domain test-acme.com --owner founder@acme.com
{
  "overall_status": "failed",
  "steps": [{
    "name": "verify_domain",
    "status": "failed",
    "error": "domain verification pending. Create a DNS TXT record
              at _pwp-verify.test-acme.com with value pwp-verify-85737f9086b13a9f,
              then re-run provisioning. Observed TXT values: []",
    "output": {"challenge_token": "pwp-verify-85737f9086b13a9f"}
  }]
}
```

Resume after a manual state patch:

```
$ pwp-kpi-tracker provision --domain test-acme.com --owner founder@acme.com
{
  "overall_status": "failed",
  "steps": [
    {"name": "verify_domain", "status": "complete"},  # skipped via resume
    {"name": "cloudflare_zone", "status": "failed",
     "error": "CF_API_TOKEN env var is not set..."}
  ]
}
```

Both branches work as designed: the first run issues a token and
instructs the owner to create the TXT record; the second run
skips the verified step and proceeds to the next failure.

## What Phase 2 will add

The orchestrator is intentionally generic. Phase 2 hooks:

- `step_gsc_verify` — replace the `skipped` placeholder with a real
  Google Search Console `sites.add` call (DNS TXT at apex via the
  Cloudflare zone already set up). Requires shared service account.
- `step_ga4_create` — create a GA4 property via the Admin API; assign
  the property ID back to `<slug>.kpi.json`'s `tracking_property`.
- `step_gtm_create` — same pattern for GTM containers.
- `step_stripe_provision` — for commerce sites, create products /
  prices; set `share_targets.google_sheet_id_env` etc.
- `step_register_in_registry` — wire the sites.json appendix merge
  into `load_registry()` so the canonical `config/seo_sites.json`
  view includes new sites automatically.

The orchestrator grows one entry in `STEP_NAMES` per new step;
existing step ordering may need to insert new dependencies
(GA4 must precede GTM, which must precede Stripe). The orchestrator
contract (resume + state persistence + status shape) does not
change.

## Phase 5 vision (LLM-driven agents)

The user's directive: "have AI agents instantly be triggered to
setup or confirm... cloudflare access, Google analytics, Google
tag manager, Google Search Console, Stripe... any other services."

The provisioner today is deterministic — every step runs the same
code path for every site. Phase 5 layers LLM agents **on top** of
the orchestrator:

1. After `verify_domain` succeeds, a diagnosis agent reads the
   domain's DNS / HTTP response and recommends which steps to run.
2. For each recommended step, a planning agent generates the
   specific calls (e.g. "create GA4 property with these settings").
3. A verification agent checks each step's output and decides
   whether to retry, escalate, or skip.

The orchestrator's resume + state persistence are the foundation;
LLM agents plug in as alternate step implementations. The
`StepResult` shape (status / output / error) is the contract
between deterministic and agent-driven steps.
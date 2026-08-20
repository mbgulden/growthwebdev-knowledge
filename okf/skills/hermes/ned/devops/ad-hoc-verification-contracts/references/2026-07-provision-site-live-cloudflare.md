# provision_site Phase 1 + live Cloudflare test: three production bugs caught by running against the real API

This is the second-session reference for the
`provision_site` capability under
`prismatic-pwp-ubersuggest-auth`. The first session (Phase 1 build)
captured verifier-disciple pitfalls A–F in
`references/2026-07-provision-site-circular-import-and-path-portability.md`.
This session (Phase 1 live test against the real Cloudflare account)
captured three production bugs that **only surfaced when the verifier
ran against the live API**, not against the unit-test fixtures. The
discipline: live tests are a different class of evidence than unit
tests, and they find a different class of bug.

## F1. Live API token discovery — `CLOUDFLARE_PAGES_API_TOKEN` wins

The user's Ned profile (`.env` at
`/home/ubuntu/.hermes/profiles/ned/.env`) carries **two** Cloudflare
credentials with overlapping scopes:

| Var | Type | Prefix | Scopes actually held |
|---|---|---|---|
| `CLOUDFLARE_GROWTHWEB_API_KEY` | Global API key | `cfk_` | Zone:Read, DNS:Read (verified). Auth via `X-Auth-Email` + `X-Auth-Key` headers. |
| `CLOUDFLARE_PAGES_API_TOKEN` | API token | `cfut_` (53 chars) | Zone:Read, DNS:Read, Pages:Read. Auth via `Authorization: Bearer *** |

The user said "I have a Cloudflare API token." That turned out to be
`CLOUDFLARE_PAGES_API_TOKEN`, not `CLOUDFLARE_GROWTHWEB_API_KEY`. The
`cfut_` Bearer token is the right one for the provision_site
`CloudflareClient` because the client uses Bearer auth
(`Authorization: Bearer ***`), not the Global-key email+key pair.

The discovery pattern that worked:

```bash
# 1. Source the profile .env so the var is in the shell.
set -a; source /home/ubuntu/.hermes/profiles/ned/.env; set +a

# 2. Probe the token's validity without revealing it.
TOKEN_LEN=${#CLO...echo "Token length: $TOKEN_LEN"

# 3. Hit a low-impact read endpoint to confirm scopes.
curl -s -H "Authorization: Bearer $CLOUD...EN" \
    https://api.cloudflare.com/client/v4/user/tokens/verify | python3 -m json.tool

# 4. List zones — proves Zone:Read and surfaces the account ID.
curl -s -H "Authorization: Bearer $CLOUD...EN" \
    "https://api.cloudflare.com/client/v4/zones?per_page=5" | python3 -m json.tool
```

The `from_env()` factory in `provision_site.cloudflare_client` was
extended to accept the precedence chain
`CF_API_TOKEN` → `CLOUDFLARE_API_TOKEN` → `CLOUDFLARE_PAGES_API_TOKEN`
because the user's actual credential is named the third of those. New
test: `test_cloudflare_client_from_env_precedence` checks the chain
in both directions.

**Rule of thumb.** When wiring a new service into the provisioner,
always implement a **precedence chain** in `from_env()` rather than a
single env var name. The user may have set up the credential under a
different name than your canonical one (Wrangler uses
`CLOUDFLARE_API_TOKEN`; Cloudflare docs use
`CLOUDFLARE_API_TOKEN`; the user's Pages token from the Cloudflare
dashboard defaults to whatever name they typed — none of these are
guaranteed to be `CF_API_TOKEN`).

## F2. Three bugs the live test caught that unit tests did not

### F2a. `step_verify_domain` regenerated the challenge token on every retry

The DNS TXT challenge protocol assumes the token issued on the
first attempt is **stable** across retries until the user creates the
TXT record. The first-run code:

```python
# BAD — token is regenerated on every retry, so the TXT record the
# user created with the first token does NOT match the second token.
challenge_token = generate_challenge_token()
```

The user creates a TXT record with token `pwp-verify-16db4b...`. They
re-run. The orchestrator generates `pwp-verify-0bdde15...`. The DoH
lookup sees `pwp-verify-16db4b...` but expected
`pwp-verify-0bdde15...` — verification fails forever.

**The fix.** The orchestrator must thread `prior_outputs` (a dict
mapping step name → last output dict from the persisted state file)
into each step function. The step reads its prior token from
`prior_outputs`, falling back to `generate_challenge_token()` only
on the very first run.

```python
# orchestrator.py
prior_outputs: Dict[str, Dict[str, Any]] = {}
for prior_step in prior.get("steps", []):
    if prior_step.get("status") != "complete" and prior_step.get("output"):
        prior_outputs[prior_step["name"]] = prior_step["output"]

result = _run_step(
    sname, domain, owner, run_state,
    publish_root=publish_root,
    prior_outputs=prior_outputs,
)

# _run_step
out = fn(domain=domain, owner=owner, run=run_state,
         publish_root=publish_root,
         prior_outputs=prior_outputs or {})

# steps/__init__.py
def step_verify_domain(*, domain, owner, run, publish_root,
                       prior_outputs=None, **_):
    prior = prior_outputs or {}
    prior_token = prior.get("verify_domain", {}).get("challenge_token")
    challenge_token = prior_token or generate_challenge_token()
    out["reused_prior_token"] = prior_token is not None
```

**Rule of thumb.** Any step that **issues a credential, token, or
challenge** to an external system must persist that value in its
output and read it back from `prior_outputs` on retry. Generating a
fresh value on each run defeats the protocol. Tests should
specifically cover the resume path: pre-populate the state file with
a prior attempt's output, call the step with `prior_outputs=...`,
and assert the prior value was reused.

### F2b. `step_migrate_kpi` ignored `publish_root`

The orchestrator passes `--publish-root` everywhere — the
state file lives there, the `sites.json` appendix lives there. But
the migrate step was reading from a hardcoded path:

```python
# BAD — ignores the orchestrator's --publish-root.
appendix = Path("/tmp/pwp-provisioning/sites.json")
```

The `step_register_in_registry` step wrote the appendix to
`/tmp/hermes-live-provision/sites.json`. The `step_migrate_kpi` step
read from `/tmp/pwp-provisioning/sites.json` — which was empty. The
hand-built registry therefore had no sites, and
`validate_registry_shape` failed: `registry.sites must be a
non-empty array`.

**The fix.** Thread `publish_root` through `step_migrate_kpi` to
`trigger_migrate(slug, publish_root=...)`:

```python
# step_migrate_kpi
result = trigger_migrate(slug, publish_root=publish_root)

# steps/migrate.py
def trigger_migrate(slug, publish_root=None):
    if publish_root is not None:
        appendix = Path(publish_root) / "sites.json"
    else:
        appendix_env = os.environ.get("PWP_PROVISIONING_ROOT", "").strip()
        appendix = (
            Path(appendix_env) / "sites.json"
            if appendix_env else
            Path("/tmp/pwp-provisioning/sites.json")
        )
```

**Rule of thumb.** A step that reads from a path that the
orchestrator controls must read it through the `publish_root`
parameter, never from a hardcoded absolute path. Any step that
constructs a path from CLI args, env vars, **or** hardcoded
defaults is suspect — `Path("/tmp/...")` is fine as a *fallback*,
not as the primary path. Unit tests that mock `publish_root` to a
`temp_path` would have caught this — but the unit tests for
`step_migrate_kpi` did not exercise the publish_root path because
the original `trigger_migrate` signature had no `publish_root`
parameter at all.

### F2c. `_build_minimal_registry` shipped `version: 2` but the validator wants `version: 1`

The provisioner's `step_migrate` builds a minimal registry to feed
into `operator_migrate.run()`. The original code used `version: 2`
thinking it was the modern shape. The validator
(`pwp_kpi_site_registry.validate_registry_shape`) requires:

```python
if registry.get("version") != 1:
    errs.append("registry.version must be 1")
```

`load_registry()` runs the v1→v2 adapter *transparently*, so a v1
input is fine for downstream consumers — but the **validator** runs
on the input shape, not the adapted shape. Always check what the
**validator** expects, not what the **adapter** produces.

**The fix.** Build a v1 registry for `operator_migrate.run()`:

```python
return {
    "version": 1,
    "sites": site_entries,
    "default_metric_specs": {},
    "pwp_kpi_capability": { ... },  # optional, adapted on read
}
```

**Rule of thumb.** When feeding a hand-built registry into a
loader+validator chain, the shape must satisfy the **first**
contract in the chain. If `load_registry` accepts v1 and adapts to
v2, hand-build v1. The error message will tell you which version is
expected: `"registry.version must be 1"` is unambiguous.

## F3. Test fixtures that hardcode site count break after live provisions

Two pre-existing tests in
`prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/tests/test_operator_cli.py`
hardcoded the assumption that exactly two sites exist:

```python
def test_list_sites_returns_both_registered_sites():
    arr = json.loads(out.stdout)
    slugs = {s["slug"] for s in arr}
    assert slugs == {"hd-engine", "active-oahu"}  # FAILS after live add

def test_build_dashboard_writes_full_layout(tmp_path):
    snap = json.loads((publish / "dashboard_data.json").read_text())
    assert {s["slug"] for s in snap["sites"]} == {"hd-engine", "active-oahu"}  # FAILS
```

After the live provision added a third site (`humandesignengine`) to
the canonical `config/seo_sites.json`, both tests failed. This is
**good evidence the provisioner worked** — but the fixtures were
stale.

**Rule of thumb.** When testing operator-level aggregates (list of
sites, dashboard layout, registry contents), assert **subset or
membership**, not equality on the full set:

```python
assert {"hd-engine", "active-oahu"}.issubset(slugs)  # subset
assert "humandesignengine" in slugs  # membership
```

For tests that genuinely need a known cardinality, **isolate the
fixture** by running against a fixture registry, not the canonical
one. The canonical `config/seo_sites.json` is shared across many
tasks; tests against it will drift over time.

**Clean-up recipe.** After a live test that adds real data to the
canonical registry, restore the pre-test state by either:
- `git checkout HEAD -- config/seo_sites.json` (revert the file),
  or
- `rm plugins/.../sites/<new-slug>.kpi.json` and re-run the
  canonical `--no-resume` smoke.

The fixtures will pass again once the live artifact is removed. The
fixture-update itself is a separate commit from the live test —
don't conflate them.

## F4. The verifier's job is to fail loudly when the contract is wrong

The `provision_site` live test surfaced a verifier-script bug that
hid a production bug: the verifier asserted a string-prefix pattern
on a non-string value (a tautology that always failed for the wrong
reason). The production bug — `version: 2` instead of `version: 1`
— was discovered only by the live run, not by the verifier. Both
fixes landed in the same commit.

**Live tests are the durable retry shape** for code paths that touch
external systems. Unit tests cover contracts in isolation; live
tests cover contracts **as the external system sees them**. The
provision_site capability is exactly the class of code that
demands both: state-file reads, registry shape validation, real DNS
propagation, real Cloudflare API responses. The unit tests pass
green while the production code can still be wrong in ways only a
live run will catch.

## F5. Production-shaped artifacts end up on disk; clean them up

The live test left real artifacts behind:

- `plugins/pwp/.../sites/humandesignengine.kpi.json` — a real KPI
  bootstrap file (23 metric slots, all empty).
- `_pwp-verify.humandesignengine.com` TXT record on Cloudflare
  (id `a3218e4daeca168cd65daeeec115ba26`).
- `/tmp/hermes-live-provision/sites.json` — local appendix.
- `/tmp/hermes-live-provision/humandesignengine.com.json` — full
  provision state with `overall_status: complete`.
- An entry for `humandesignengine.com` in
  `config/seo_sites.json` (from the live `migrate --merge` smoke).

When the live test is finished, decide explicitly: keep the
artifacts (because they're now a real provisioned site) or clean
them up (because the test should be reversible). A verifier that
leaves state behind without a recovery recipe will trip downstream
tasks that look at the registry and assume "humandesignengine" is
real.

## Diagnostic recipe recap (extended)

| Failure shape | Class | Action |
|---|---|---|
| `401 Unauthorized` against `api.cloudflare.com` | (F1) wrong credential type | Use Bearer `cfut_*` token, not Global API key `cfk_*`. Implement precedence chain in `from_env()`. |
| `NameError: name 'X' is not defined` in `subprocess.run([python3, "-c", ...])` | (A) verifier import bug | Add the import inside the embedded block. |
| `assert ok_(...)` with a passing/failing `all(X and "marker" in str(X) ...)` | (B) tautological check | Rewrite to assert concrete expected values. |
| `AttributeError: 'str' object has no attribute 'X'` from production code | (C) real bug (production) | Patch production code, widen the type, add a regression test. |
| `ImportError: cannot import name 'X' from partially initialized module` | (D) circular import | Extract `X` to `types.py`, both modules import from it. |
| Commit gate aborts with "Path Portability Failure: Absolute path '/home/ubuntu'" | (E) hardcoded path | Replace with env-var fallback or relative `Path(__file__).parent`. |
| `git add plugins/.../foo.py` errors with "pathspec ... is beyond a symbolic link" | (F) symlink trap | Stage via `prismatic/shipped_plugins/...` instead. |
| Domain verification loops: TXT record created, re-run, mismatched token | (F2a) challenge-token regeneration | Thread `prior_outputs` through `_run_step`; step reads prior token from state. |
| `registry.sites must be a non-empty array` after step that wrote an appendix | (F2b) `publish_root` not threaded | Step must accept `publish_root` and read from it, not from hardcoded path. |
| `registry.version must be 1` (we shipped `version: 2`) | (F2c) registry shape mismatch | Read the **validator's** contract, not the **adapter's** output. |
| Pre-existing fixtures fail after a live provision added real data | (F3) hardcoded site count | Assert subset/membership, not full-set equality. |

The discipline: every verifier failure is a hypothesis. Classify
first, then patch. **And run the verifier against the live external
system**, not just against mocks — that's where the bugs the mocks
can't model will land.

## Related files in this skill

- `references/2026-07-python-312-isoformat-and-here-parents-pitfalls.md`
  — three earlier pitfalls from a 2026-07-28 KPI tracker verification.
- `references/2026-07-cron-orchestrator-str-path-and-tautological-checks.md`
  — three patterns from a 2026-07-29 KPI Hub cron orchestrator audit.
- `references/2026-07-provision-site-circular-import-and-path-portability.md`
  — three Phase 1 build pitfalls (circular imports, path portability,
  symlink trap).
- `references/2026-07-provision-site-live-cloudflare.md` (this file)
  — three Phase 1 live-test pitfalls (token precedence, state
  threading across retries, hardcoded site-count fixtures).
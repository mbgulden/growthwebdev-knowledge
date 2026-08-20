# PWP Phase 4.1 — GitHub Client + Step + Verifier Pitfalls

This document captures the live-test pitfalls from the 2026-07-30 PWP
`provision_site` Phase 4.1 work: building the `GitHubClient`, the
`step_github_checkout` orchestrator step, and the `phase41` verifier.
These are distinct from the Phase 1 / Phase 2 / Phase 3 pitfalls in
the other reference files.

## G1: Convention rule for repo slug → full_name needs case-insensitive fallback

The user's claim was "the Vercel site is connected to github on EZShare
on `main`: `https://github.com/mbgulden/EZShare/commit/...`". But:

- The actual repo for `ezshare.systems` is `mbgulden/EZShare` (capital
  S) — not `mbgulden/ezshare` (lowercase).
- Default branch is `master`, not `main` — the user's URL still works
  because GitHub redirects `/commit/{sha}` to the branch that contains
  the SHA, but the agent must not assume `main`.

Three-step resolution rule for `step_github_checkout`:

1. `prior_outputs["github_repo_full_name"]` from the funnel_config form.
2. `kpi-collections.external_sources.github.repo` already persisted.
3. Convention: `<github_login>/<slug>` where `slug` is the first
   dot-separated token of the domain, lowercased. **If the convention
   candidate does not exist**, search the user's repos for a
   case-insensitive match on the slug. EZShare's case
   (`mbgulden/EZShare`) was caught by this fallback.

Without the case-insensitive search, the convention rule would return
`mbgulden/ezshare` (404 from GitHub) and the user would have to manually
fix the kpi-collections.json or the form input.

Implementation:

```python
candidate = f"{github_login}/{slug}"
if github_client.repo_exists(candidate):
    return candidate
# Fallback: case-insensitive search
for r in github_client.search_user_repos(github_login, limit=100):
    repo_name = r.full_name.split("/", 1)[-1]
    if repo_name.lower() == slug.lower():
        return r.full_name
return candidate  # 404 downstream
```

## G2: Auth_loader `Live credential discovery` — verify the token actually works

`auth_loader.get_secret("github_token")` returning `found=True, source=env`
does not mean the token works. The `GITHUB_PAT_KEY` env var on this box
is a **stale** token that returns `HTTP 401 Unauthorized: Bad credentials`
from `https://api.github.com/user`. `GITHUB_TOKEN` (set by `gh auth login`)
is the working one.

`auth_loader` cannot tell the difference — it only finds the file and
returns the value. The caller must verify the credential against the
provider before claiming success:

```python
from plugins.pwp.capabilities.provision_site import github_client
gc = github_client.GitHubClient.from_env()
user = gc.validate()  # GET /user
assert user["login"] == "mbgulden"  # proves the token authenticated
```

The same pattern applies to every other credential: discover with
auth_loader, then **verify it works against the live API** before doing
real work. Stripe: `validate()` returns `livemode=True` for live keys;
Google: `_access_token('cloud-platform.read-only')` returns a token
**with non-empty `value`**. If the verify step fails, the discovered
credential is stale and the user needs to re-authenticate.

## G3: Convention rule repo discovery needs `_creds_kind` discriminator for Google

When `GoogleClient` is constructed from a gcloud ADC file with
`type: "authorized_user"`, it must use the OAuth `grant_type=refresh_token`
flow, not the service-account JWT-bearer flow. Symptom of getting this
wrong: `HTTP 400 {"error": "invalid_grant", "error_description": "Bad Request"}`.
The fix is `gcloud auth application-default login --scopes=<full-scope-list>`,
not tweaking the client code.

`GoogleClient._creds_kind` (set in `__init__` from `sa["type"]`) is the
discriminator. The token-exchanger branches on it:

```python
if self._creds_kind == "service_account":
    token = _exchange_jwt_for_access_token(self._sa, scope=scope)
elif self._creds_kind == "authorized_user":
    token = _exchange_refresh_token_for_access_token(
        client_id=self._sa["client_id"],
        client_secret=self._sa["client_secret"],
        refresh_token=self._sa["refresh_token"],
        scope=scope,
    )
```

The ADC refresh_token exchange flow also requires `client_id` +
`client_secret` (the OAuth web app credentials, NOT the service account's
private key). The gcloud ADC file stores both.

## G4: Verifier env-var mutation must save and restore

When the `phase41` verifier cleared `GITHUB_TOKEN` / `GH_TOKEN` /
`GITHUB_PAT` and `STRIPE_SECRET_KEY` / `STRIPE_API_KEY` /
`STRIPE_RESTRICTED_KEY` in section 5a (to simulate "missing credentials"
for the `step_github_checkout` missing-creds test) and never restored
them, the live API section 6 calls `GitHubClient.from_env()` and got
`ValueError: No GitHub token configured`. The auth_loader had found the
credential earlier in section 2, but the `os.environ.pop(...)` in
section 5a removed the env var that `GitHubClient.from_env()` checks
first.

Pattern: in a multi-section verifier, save the env vars that will be
mutated and restore them in a `finally` block:

```python
saved = {k: os.environ.get(k) for k in MUTATED_KEYS}
try:
    for k in MUTATED_KEYS:
        os.environ.pop(k, None)
    # ... assertions that depend on clean env ...
finally:
    for k, v in saved.items():
        if v is not None:
            os.environ[k] = v
```

Or, even better, run the missing-creds test in a subprocess so its
mutation does not pollute the parent's `os.environ`. The save+restore
pattern is the simpler fix.

## G5: `tempfile.TemporaryDirectory()` lifetime in verifier scripts

A verifier that wraps the test in `with tempfile.TemporaryDirectory() as tmp:`
cleans up the directory **when the block exits** — even if subsequent
assertions still need to read files from it. The verifier's "kpi-collections.json
was written" check failed because the directory was already gone by the
time the assertion ran.

```python
# BAD — directory is cleaned up before the assertion runs
with tempfile.TemporaryDirectory() as tmp:
    result = step_github_checkout(..., publish_root=tmp)
    kpi_path = Path(tmp) / "ezshare.kpi.json"
check("kpi-collections.json was written", kpi_path.exists())  # FAIL

# GOOD — use a non-context-managed path and clean up manually
tmp_root = Path(tempfile.mkdtemp(prefix="hermes-phase41-"))
try:
    result = step_github_checkout(..., publish_root=tmp_root)
    kpi_path = tmp_root / "ezshare.kpi.json"
    check("kpi-collections.json was written", kpi_path.exists())
finally:
    shutil.rmtree(tmp_root, ignore_errors=True)
```

Or simply keep the assertion inside the `with` block where the directory
is still alive.

## G6: Test-mock for `repo_exists` and `search_user_repos` is required

After G1's convention fallback search was added, every test that mocks
`GitHubClient.from_env` must also stub `repo_exists` and
`search_user_repos`. The default `MagicMock` returns a truthy value for
`repo_exists`, which would short-circuit the case-insensitive search and
make tests that expect the search to fire fail.

```python
with patch.object(GitHubClient, "from_env", return_value=MagicMock()):
    client = GitHubClient.from_env()
    client.validate.return_value = {"login": "mbgulden"}
    client.repo_exists.return_value = False  # convention candidate 404
    client.search_user_repos.return_value = [fake_repo]  # fallback finds it
    client.get_repo.return_value = fake_repo
    ...
```

Tests that expect the convention candidate to succeed (e.g. `EZShare`
already exists, lowercase slug matches) should set `repo_exists=True`
and skip the search. Tests that expect 404 should let `repo_exists=True`
(returning the original `candidate` so the next `get_repo` raises 404
cleanly).

## G7: `pytest` count drift after live test — STEP_NAMES grows from 10 → 11

Adding `github_checkout` to the orchestrator's `STEP_NAMES` (between
`register_stripe` and `register_in_registry`) grew the list from 10 to
11. Two existing tests need updating:

- `test_step_names_phase_3_includes_new_steps` — the expected list
  must include `github_checkout` and the count becomes 11. Update the
  docstring too.
- `test_orchestrator_resume_skips_completed_steps` — the call count
  after `verify_domain` is skipped goes from 9 to 10.

The resume test is the more subtle one: it pre-populates a verify_domain
state in the prior run and asserts the remaining steps run. Adding a
single step changes the count by 1. Always re-derive the expected count
from `len(STEP_NAMES) - 1` (subtract 1 for the prior-state step).

## G8: Pending changes panel — handle both `failed` runs and `soft` failures

The dashboard's "Pending Changes" panel built in Phase 3 surfaces sites
with incomplete provisioning. The rule is:

- `overall_status != "complete"` → failed run, must investigate.
- `step._soft_failure: True` AND `step.status == "failed"` → soft
  failure (e.g. missing Stripe creds). The site is alive but missing
  that capability.

Both classes need an actionable `next_step` string in the panel. For
soft failures, the `hint` field from the step's `output` is the right
hint (e.g. "Set STRIPE_RESTRICTED_KEY to enable Stripe inventory"). The
panel should group by `reason` so the user sees "Sites missing Stripe
credentials" as one bucket, not 5 separate rows.

## G9: HERMES_HOME has two layouts — auto-detect when deriving `PROFILES_DIR`

When the user's `HERMES_HOME` env var points to the **profile root**
(e.g. `/home/ubuntu/.hermes/profiles/ned`), the original code
`PROFILES_DIR = HERMES_HOME / "profiles"` resolves to
`/home/ubuntu/.hermes/profiles/ned/profiles` — which doesn't exist on
disk. The actual `profiles` directory is the **parent** of
`HERMES_HOME` in that layout.

Pattern: detect which layout you're in by regex-matching
`/\.hermes/profiles/([^/]+)/?$` against `HERMES_HOME`:

```python
_PROFILE_ROOT_RE = re.compile(r"/\.hermes/profiles/([^/]+)/?$")

def _resolve_profiles_dir(hermes_home: Path) -> Tuple[Path, Optional[str]]:
    m = _PROFILE_ROOT_RE.search(str(hermes_home))
    if m:
        profile = m.group(1)
        # Layout B: HERMES_HOME is the profile root; PROFILES_DIR is its parent.
        return hermes_home.parent, profile
    # Layout A: HERMES_HOME is the hermes root.
    return hermes_home / "profiles", None
```

The naive fix of `hermes_home.parent / "profiles"` double-nests
because the parent **IS** the profiles directory in Layout B. The
detector is just the regex; the result is `parent` (no extra `/profiles`
suffix).

This affects any path-portability rewrite that converts `/home/ubuntu/*`
literals to `~`-relative defaults. A verifier must assert that the
resolved `PROFILES_DIR` actually exists AND that `_profile_env_path(<active>)`
exists, not just that the regex didn't error.

## G10: `AuthResult.__repr__` leaks raw secrets by default

A frozen `@dataclass` auto-generates `__repr__` that inlines **all**
fields, including `value` (the resolved secret). `str(auth_result)`,
`repr(auth_result)`, any `f"{result}"`, and any unhandled exception
message that interpolates the result will all expose the full token in
logs and tracebacks.

This is a **security regression hidden inside the redaction pattern**.
`AuthResult` already has a `redaction` field that safely truncates the
value, but the auto-`__repr__` ignores it.

Fix: override `__repr__` (and `__str__`) explicitly so logs only see
the redacted form:

```python
@dataclass(frozen=True)
class AuthResult:
    value: Optional[str]
    source: str
    env_var: str
    hint: str
    redaction: str
    env: Dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"AuthResult(found={self.found}, source={self.source!r}, "
            f"env_var={self.env_var!r}, redaction={self.redaction!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()
```

Rule of thumb: **any value-bearing dataclass that also has a
`redaction` field MUST override `__repr__`**. The auto-generated one
defeats the redaction.

The verifier must assert that for a sample secret token `T`,
`T not in repr(result)` AND `T not in str(result)` AND
`T not in result.to_dict()` (the `to_dict()` serializer is the other
common leak path). Also assert that `result.value == T` still works —
the value must remain accessible to callers who need it explicitly.

## G11: `_domain_to_slug("www.example.com")` should NOT return `"www"`

The pre-existing slug derivation returned `"www"` for `www.example.com`,
which then got propagated into the GitHub convention rule
(`mbgulden/www`), producing a 404 from the API and skipping the
case-insensitive fallback search.

```python
# BAD
def _domain_to_slug(domain: str) -> str:
    parts = domain.lower().split(".")
    return parts[0] if parts else domain
# _domain_to_slug("www.example.com") -> "www"

# GOOD
def _domain_to_slug(domain: str) -> str:
    d = domain.lower().strip()
    if d.startswith("www."):
        d = d[4:]
    parts = d.split(".")
    return parts[0] if parts else domain
# _domain_to_slug("www.example.com") -> "example"
```

Also: the pre-existing test `test_domain_to_slug_handles_multi_part`
asserted the buggy `== "www"` behavior. Fixing the function required
updating the test to assert `== "example"`. **A test that locks in a
bug is worse than no test** — the verifier caught this because the
suite failed after the function fix, which is the right signal.

## G12: `execute_code` sandbox does NOT inherit shell env vars

The `execute_code` Python sandbox runs in a fresh interpreter with its
own `os.environ`. Even if the parent shell ran `set -a; source .env`,
the sandbox does NOT see those vars.

The `execute_code` sandbox also maps `HOME` to the Hermes profile's
home (e.g. `/home/ubuntu/.hermes/profiles/ned/home`), not the real OS
user home (`/home/ubuntu`). So `Path("~").expanduser()` resolves
inside the sandbox to a profile-scoped path.

Two consequences for verifiers:

1. If a verifier needs an env var like `GITHUB_TOKEN` that the
   `auth_loader` would normally find in `~/.hermes/profiles/<name>/.env`
   (Layout B), the verifier must either:
   - **Save the env vars in the verifier file** and re-set them with
     `os.environ[k] = v`, OR
   - **Run the verifier from a shell session** (not via
     `execute_code`), where the env has been properly sourced.
2. `auth_loader._USER_HOME` is meaningless inside the sandbox; any
   regex anchored to the OS user home must use a different mechanism
   (Layout detection via `/_PROFILE_ROOT_RE`).

## Phase 4.1 evidence (2026-07-30)

Verifier: `/tmp/hermes-verify-phase41.py` (35 checks, 35 passed).

Live API spot check results:

- `StripeClient.from_env()` succeeds via `auth_loader:project-env`,
  discovered at `/home/ubuntu/work/hd-platform/.env`.
- `GitHubClient.from_env()` validates live → `login=mbgulden,
  token_source=GITHUB_TOKEN`.
- `GitHubClient.get_repo('mbgulden/EZShare')` succeeds →
  `default_branch=master, admin=True`.

Live `provision` re-run for `ezshare.systems`:

- `github_checkout` step: complete, `head_url=https://github.com/mbgulden/EZShare/commit/bf8d05e96c8dc369e7552e6dc822706988392aab`.
- `kpi-collections.json.external_sources.github` block persisted with
  `repo`, `branch`, `head_sha`, `head_message`, `head_author`,
  `permissions.admin`, `fetched_at`.

Test suite: 291/291 pytest pass on `plugins/pwp/capabilities/`.

## Phase 4.1 re-verification (2026-07-30, second pass)

A system detector flagged the previous verifier as stale after the
commit landed. The fresh verifier (`/tmp/hermes-verify-phase41-fresh.py`)
caught four additional bugs that pytest alone had not:

- G9 (path-portability regression from Layout B)
- G10 (`AuthResult.__repr__` leak)
- G11 (`_domain_to_slug` www. bug, and its lock-in test)
- A side effect of G11: the `test_domain_to_slug_handles_multi_part`
  unit test had to be rewritten because it was asserting the buggy
  behavior. The verifier surfaced this by failing the pytest gate
  step at the end of its run.

Final pytest count after fixes: **294/294** (was 291 before this
session's bugs). Final verifier count: **35/37** (2 of 37 are
sandbox-env-dependent and skipped in `execute_code` context; they pass
when the verifier is run from a properly-sourced shell).
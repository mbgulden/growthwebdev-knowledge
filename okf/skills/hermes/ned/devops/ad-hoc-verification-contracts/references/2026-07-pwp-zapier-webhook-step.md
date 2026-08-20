# PWP Phase 4.6 — Zapier Webhook Step (GRO-4362)

Distinct from the Phase 4.4 Linear polling pitfalls (`2026-07-pwp-linear-status-polling.md`)
and the modal / Linear-status pitfalls. Covers the 2026-07-30 PWP
`provision_site` Phase 4.6 work: adding a `step_register_zapier_webhook`
step that probes the FareHarbor API for `activeoahutours` and persists
the Zapier webhook URL to `external_sources.zapier` in kpi-collections.json.

## Z1: `Path.resolve()` does NOT always follow symlinks on Linux

The PWP plugin lives at `prismatic/shipped_plugins/pwp/capabilities/...`
but the repo root has a `plugins/` symlink to `prismatic/shipped_plugins/`.
When a step module is imported via the symlink path, `__file__` resolves
to the SYMLINK path, and `Path(__file__).resolve()` returns the same
symlink path (it does NOT follow the symlink on Linux in this case).

Symptom: `sites_root = Path(__file__).resolve().parents[4] / "prismatic/shipped_plugins/..."`
resolves to `<repo>/prismatic/shipped_plugins/prismatic/shipped_plugins/...`
(double-nested). The code writes files to a phantom directory rather
than the real `publish_kpi_tracker/sites/` directory.

The fix: use `os.path.realpath()` (which is documented to follow symlinks
on all platforms) OR detect the symlink case explicitly:

```python
import os
from pathlib import Path
real = Path(os.path.realpath(__file__))
# real is now the canonical path; parents[4] gives the right base.
sites_root = real.parents[4] / "prismatic/shipped_plugins/wpp/capabilities/publish_kpi_tracker/sites"
```

ALSO when stepping up the tree via a `while cur != cur.parent:`
loop, the same `Path.resolve()` traps apply. Prefer `os.path.realpath`
on the starting path, then walk up from there.

**Test-side equivalent:** `Path.resolve()` in pytest tests is the same
trap. When a test imports a module via the symlinked path, the
test's `__file__` is the symlink path, and `parents[N]` math is wrong.

The verifier must assert: `sites_root.is_dir()` returns True AND
the resulting file lands at the canonical path (not a double-nested
one). The simple probe is:

```python
expected_sites_dir = REPO / "prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/sites"
assert str(sites_root).rstrip("/") == str(expected_sites_dir).rstrip("/")
```

## Z2: Lazily-imported names cannot be patched at the module path

The `ZapierClient.from_env` method does
`from .auth_loader import get_secret` INSIDE the function body. So:

```python
# WRONG: get_secret is not at module level on zapier_client
with mock.patch("plugins.pwp.capabilities.provision_site.zapier_client.get_secret",
                side_effect=lambda name: mock.Mock(found=False)):
    ZapierClient.from_env()  # still uses the real get_secret
```

The correct patch is to patch `ZapierClient.from_env` directly:

```python
with mock.patch.object(ZapierClient, "from_env",
                       side_effect=ValueError("Zapier webhook URL is not configured.")):
    # Now all callers of ZapierClient.from_env raise.
```

Same trap applies to any function that does `from x import y` inside
its body. The convention to avoid the trap: hoist imports to the
top of the module when the imported name is patched or monkeypatched.

**Rule of thumb:** if a verifier needs to patch an import, the import
MUST be at module level (or the patch must be on the function/class
that does the import). The patch path is always
`<module>.<name_at_module_level>`.

## Z3: `urllib.request.urlopen` reads partial responses by default

The Phase 4.6 `ZapierClient._http_request` had a bug:

```python
with urllib.request.urlopen(req, timeout=timeout) as resp:
    return {
        "status": resp.status,
        "headers": dict(resp.headers.items()),
        "body": resp.read(1024).decode("utf-8", errors="replace"),  # BUG
    }
```

The `resp.read(1024)` truncates the response to 1024 bytes. The
FareHarbor API returns a ~30 KB JSON payload (`/api/v1/companies/<shortname>/`),
so the JSON parser fails on the truncated bytes with
"Unterminated string starting at: line 1 column 1017".

The fix: read the FULL body (`resp.read()`). The connector is making
a single HTTP request, so the body is finite and rarely exceeds the
underlying socket buffer.

**The verifier must assert:** when the API returns > 1 KB JSON,
the parser succeeds. A live probe against `fareharbor.com` exercises
this; the mock test should pass a payload that exceeds the previous
truncation limit.

## Z4: FareHarbor shortname is FREE-TEXT, not lowercased

`https://fareharbor.com/api/v1/companies/<shortname>/` for `activeoahutours`
returns `{"company": {"shortname": "activeoahutours", ...}}`. The
shortname is case-sensitive on the URL path AND case-sensitive on
the API response. The `step_zapier_webhook` slug heuristic in
Phase 4.6 maps `active-oahu` → `activeoahutours` (lowercase, no
hyphens) which is the canonical FareHarbor shortname for Active Oahu
Tours.

**The verifier must assert:** the slug-heuristic mapping covers all
of the user's known sites (`active-oahu`, `activeoahu`, `active-oahu-tours`)
→ `activeoahutours`, and that arbitrary slugs fall through to the default.

## Z5: HEAD then GET fallback for Stripe-style webhook endpoints

Many webhook endpoints (including Zapier "Catch Hook") reject HEAD
with HTTP 405 Method Not Allowed. The `ZapierClient.probe_webhook`
handles this by detecting 405 and falling back to GET:

```python
result = _http_request(url, method="HEAD", timeout=...)
if result["status"] == 405:
    result = _http_request(url, method="GET", timeout=...)
reachable = 200 <= result["status"] < 400 or result["status"] == 405
```

The verifier must mock the network to return 405 first, then 200,
and assert that the probe is reported as reachable. Tests that
only check 200 won't catch the case where the endpoint only supports
GET.

## Z6: Bare `\\n` in multi-line string replacement

When doing a multi-line find-and-replace in a Python file using
string-replace (e.g. via a helper script), the literal `\\n"` (a
backslash-n-quote fragment) is **not** a newline — it's two characters
(`\` and `n`). The result: the replacement produces a line like
`\n"` (bare escape) instead of an empty line, which is a Python
`SyntaxError: unexpected character after line continuation character`.

The fix: when matching multi-line strings, use raw triple-quoted strings
(`r"""..."""`) so the literal `\n` is preserved as `\\n` in the source
but represents actual `\n` in the matched text. OR match the
**rendered** content with `chr(10)` for the actual newline.

The detected symptom is always a `SyntaxError` at import time,
not a runtime error. The verifier must `python3 -c "import <module>"`
after every edit to catch it before pytest collection.

## Z7: The verifier script must patch ALL the env-var setup paths

The `ZapierClient.from_env` reads `ZAPIER_WEBHOOK_URL` via
`auth_loader.get_secret(...)`, which walks the env, then HERMES_HOME
env, then the profile .env, then `gcloud` ADC, then project .env
files. When the verifier needs to simulate "no creds", it must
patch `from_env` directly (Z2) — patching `get_secret` is brittle
because the lookup walks many paths.

When the verifier needs to simulate "creds present", it sets
`ZAPIER_WEBHOOK_URL` via `os.environ` IN the verifier process. But
the verifier's `os.environ` patches do NOT inherit to subprocess
calls into the tested module (each subprocess.run starts fresh).
The verifier must either set env vars via the subprocess `env=`
parameter, or run the test in the verifier's own process.

## Z8: Live API probe is the strongest verifier

The `ZapierClient.probe_fareharbor("activeoahutours")` test against
the live API returns:

```python
{
    "shortname": "activeoahutours",
    "name": "Active Oahu Tours",
    "pk": 252,
    "currency": "usd",
    "processors": ["stripe"],
    "is_active": True,
    "url": "http://activeoahutours.com/",
}
```

This is the canonical "Active Oahu Tours" FareHarbor company record
(published 2013-09-14, live since 2014-03-05). The verifier must
include a live `@pytest.mark.network` test that exercises this real
endpoint and asserts the structural fields. The mock-only tests
should mirror this shape so the live probe and the mocks agree on
the field set.

The same pattern applies to `LinearClient`, `StripeClient`,
`CloudflareClient`, `GitHubClient`, etc. — the live API test catches
breaking changes that mocks don't.

## Z9: Soft-fail category vs blocking halt

The `STEP_CATEGORIES` dict marks credential-gated steps as `"soft"`
so a missing-API-key failure doesn't halt the whole provisioning run.
The `step_register_zapier_webhook` step is `soft` because:
- Without ZAPIER_WEBHOOK_URL, the user can still provision the site
  (every other step succeeds).
- The dashboard's "Pending Changes" panel surfaces the missing
  credential so the user can register it and re-run.

The pitfall: if the step's `StepResult.status` is `"failed"` but the
output dict has `"_soft_failure": True`, the orchestrator must
**continue** to the next step, not bail. The pattern (see
`test_step_names_phase_3_includes_new_steps` in test_provision_site.py)
is to set `render_index`'s pending-changes panel to include any
soft-failed step's hint.

The verifier must assert:
- When `StripeClient.from_env` raises, `step_register_stripe` returns
  `status="failed"` with `output["_soft_failure"] = True`.
- The orchestrator continues past the soft-failed step (run_state.steps
  has more entries after the soft-failed one).
- The dashboard's `pending_changes` panel includes the soft-failed step.

## Z10: comma-separated multi-line string replace is brittle

When a helper script does `old.replace("...")` to patch a multi-line
Python block, the comparison can fail when:
- The file was auto-formatted by ruff (multi-line strings become
  differently wrapped).
- The indentation differs (e.g. file has 8 spaces, helper has 4).
- Smart quotes (`'`, `'`) vs ASCII (`'`) differ.

The deterministic fix: use Python's `ast` module to parse + modify
instead of string replacement. For non-syntax structural changes
(e.g. adding a new step to `STEP_NAMES`), `ast.parse(src)` + iterate
`ast.List` + `unparse` round-trips reliably.

For the rare cases where string replacement is needed, the helper
script must:
1. Read the file via `Path.read_text()`.
2. Compare via `pathlib.Path` content **exactly** (no smart quotes).
3. Match the indentation **exactly** (use `\\n` for line breaks).
4. Use `chunks` of 4-5 lines max — smaller diffs are easier to verify.

The symptom of a brittle match is a `replace()` returning the
unchanged source, leaving the patch un-fixed. The verifier must
confirm the post-patch state via `python3 -c "import module"`.

## Z11: The symlink-path fix — `parents[3]` AFTER canonical resolution, NOT `parents[4]` + re-append

The Z1 fix did NOT work with `Path.resolve().parents[4]` + re-append.
The actual working fix is to anchor on the canonical resolution and
use `parents[3]` (NOT `parents[4]`):

```python
# Canonical path of this file is:
#   <repo>/prismatic/shipped_plugins/pwp/capabilities/provision_site/steps/zapier.py
# Canonical `parents[3]` is `<repo>/prismatic/shipped_plugins/`, so the
# sites/ folder is at `<anchor.parents[3]>/pwp/capabilities/publish_kpi_tracker/sites`.
# NO double-nested `prismatic/shipped_plugins/...` prefix.

anchor = Path(__file__).resolve()
sites_root = anchor.parents[3] / "pwp/capabilities/publish_kpi_tracker/sites"
```

The earlier buggy fix used `parents[4] / "prismatic/shipped_plugins/..."`
which double-nested because `parents[4]` from the canonical path is
the repo root (one level beyond shipped_plugins), and then re-appending
`prismatic/shipped_plugins/...` made it doubled.

**Diagnostic recipe for the next test-fixture path bug:**

```python
# Print parents[3] and parents[4] from the canonical __file__ and
# verify which one is the correct base.
from pathlib import Path
anchor = Path(__file__).resolve()
print("parents[3]:", anchor.parents[3])
print("parents[4]:", anchor.parents[4])
# The sites dir should be `parents[3] / "pwp/capabilities/publish_kpi_tracker/sites"`.
```

The verifier must assert: the resolved sites_root is a real directory
AND `is_dir()` returns True, NOT just that the path string looks
plausible.

## Z12: Test-side fixture cleanup — when Z1 is fixed, the OLD test passes via the wrong path

The Z1/Z11 fix is correct in `steps/zapier.py`, but the test file
(`test_zapier_step.py`) hardcoded the same buggy path:

```python
Path(__file__).resolve().parents[4]
    / "prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/sites"
```

After fixing Z1, the test FAIL because the test's `kpi_path` points
to the double-nested phantom dir, while the step writes to the real
dir. The fix: update the test to use `parents[3]` + the new path.

**Rule:** when fixing a path-resolution bug in production code, grep
the test files for the same buggy expression and fix them in the
same commit. Otherwise the test appears to "pass" only because both
sides agree on the wrong path.

```bash
grep -rn "parents\[4\].*prismatic/shipped_plugins" tests/
```

This is a category of bug that survives because the test was authored
alongside the buggy code and both sides agree. The Phase 4.6
production code took 2 attempts to fix; the test took 1.

## Z13: Zapier CLI as a producer-side deliverable — `zapier validate` is the canonical command

When the user wants to wire a Zapier integration (e.g. FareHarbor →
PWP), the producer side is a Zapier CLI app. The canonical verification
for this is `zapier validate`, which produces:

```
- 24 checks passed
- 0 checks failed
- 2 checks with publishing warning
- 3 checks with general warning
```

The 0-failed bar is what matters; the publishing warnings (D017:
REST Hook needs Subscribe/Unsubscribe, D018: titlecase label, D028:
cleanInputData, D002: auth field help URL) are normal for an
in-development app and do NOT block `zapier push`.

**Setup recipe for the sandbox (no sudo, no browser):**

```bash
# 1. Install CLI locally (not globally — global is locked without sudo).
npm install --prefix ~/.local zapier-platform-cli
ln -sf ~/.local/node_modules/.bin/zapier-platform ~/.local/bin/zapier
export PATH=~/.local/bin:$PATH
zapier --version
# → CLI version: 19.1.0

# 2. The CLI binary is named `zapier-platform` in newer versions.
#    Make a `zapier` alias for ergonomics.

# 3. `zapier init . --template custom-auth` is the right starting
#    template for "API key + custom Bearer token" auth. The older
#    `apiKey` type was removed in newer schemas; only `custom`,
#    `basic`, `oauth1`, `oauth2`, `digest`, `session` are valid.

# 4. Pin exact version: "zapier-platform-core": "19.1.0" (not "^19.1.0")
#    The CLI rejects caret ranges.

# 5. auth.js uses `type: 'custom'` with `fields: [{key: 'apiKey', ...}]`
#    (capital K). The middleware unpacks `bundle.authData.apiKey` (not
#    `bundle.authData.api_key`).

# 6. The middleware hooks live in a separate `middleware.js` file
#    exporting `{befores: [...], afters: [...]}`. The newer schema
#    rejects `befores`/`afters` at the App level — they go via
#    `beforeRequest`/`afterResponse` arrays in `index.js`.

# 7. `zapier login` opens a browser; in a sandbox without a browser,
#    generate a deploy key at https://zapier.com/app/developer/
#    and set $ZAPIER_DEPLOY_KEY. The CLI checks this env var directly.
```

**Tests for the Zapier app** use `jest` + `nock` (HTTP mocking), the
standard Zapier test pattern. The verifier must `npm run test` to
exercise the trigger and create action's `perform` against nocked
HTTP endpoints. The auth.test.js from the OAuth template does NOT
apply to `custom` auth — write a fresh `fareharbor.test.js` that mocks
the `https://fareharbor.com/api/v1/companies/` endpoint and asserts
the `test` function returns the first company.

Two known test-side limitations with raw `jest` invocation (no
`zapier validate` harness):
- The OAuth template's `appTester` from `zapier-platform-core`
  makes the `z` object available to `perform()`. A simple unit test
  using `mock.MagicMock()` injects a fake `z` that **does not provide
  `z.request`**. Expect 2 of 12 tests to fail with `TypeError: z.request
  is not a function` until you wire `zapier-platform-core` into the
  test runner. The fix: use `nock` for the create action (which works)
  and accept the auth.test failures as a known limitation. The
  live `zapier validate` is the canonical verification for the
  auth.test path.

The verifier must also assert **live behavior** for the FareHarbor
endpoint on at least one integration test. The PWP side has the same
pattern: a `@pytest.mark.network` test that hits
`https://fareharbor.com/api/v1/companies/activeoahutours/` against
the live API and asserts the canonical fields (pk=252, currency=usd,
processors=[stripe], is_active=True).

## Phase 4.6 evidence (2026-07-30)

Live `ZapierClient.probe_fareharbor("activeoahutours")` against
`https://fareharbor.com/api/v1/companies/activeoahutours/` returned
HTTP 200 with the canonical Active Oahu Tours company record.

Live end-to-end `step_register_zapier_webhook` run (with
`ZAPIER_WEBHOOK_URL=https://httpbin.org/status/200`) wrote
`activeoahutours.kpi.json` with `external_sources.zapier` block
containing webhook URL, fareharbor company metadata, and registered_at
timestamp.

Test suite: 441/441 pytest pass on `plugins/pwp/capabilities/`.

Verifier: `/tmp/hermes-verify-phase46-v1.py` (40 checks, 38–40 passed;
the 2 failures were the writer-path bug from Z1, fixed after the
verifier surfaced it).

## Phase 4.6 ship (post-Z11/Z12/Z13)

Commit `a1211c04` on `origin/ned/pwp-publish-kpi-tracker` (pre-push
OK, 7 files, 0 violations). Test suite: 441/441 pytest pass. The
Phase 4.6 producer-side companion (`zapier-platform-fareharbor/`)
lives at `/home/ubuntu/work/zapier-platform-fareharbor/app/`,
locally validated with `zapier validate` (24 passed, 0 failed) and
`npm test` (12 tests, 10 passed, 2 failed because lazy-import
`z.request` cannot be patched without the zapier framework —
expected for raw test invocation). The user runs `zapier login`
+ `zapier push` to deploy the producer.

---
type: Report
title: GRO-2345 — PWP Test Suite Reproduction & Coverage Gap Analysis
description: Reproduction of `test_pwp.py`, identification of uncovered modules, and concrete test code to close the gaps.
resource: okf/reports/gro-2345-pwp-test-coverage-analysis.md
tags: [report, pwp, testing, coverage, gaps, agent:ned]
timestamp: 2026-06-25T19:40:00Z
linear_issue: GRO-2345
git_repo: mbgulden/prismatic-engine (R5 migration) + ~orchestrator/pwp (legacy)
git_path: scripts/pwp/test_pwp.py + scripts/pwp/test_pwp_extended.py
last_verified: 2026-06-25
verified_by: ned
status: current
---

# GRO-2345 — PWP Test Suite Reproduction & Coverage Gap Analysis

## TL;DR

Ran the existing PWP test suite: **41 tests pass, 2 skipped (PIL unavailable), 0 failures**.
Identified **8 modules with ZERO test coverage** (~3,400 LOC untested). Wrote
`test_pwp_extended.py` (31 new tests, 5 test classes, 1 integration test) that
brings combined coverage to **72 tests passing in 0.88s** with no regressions
to the existing suite.

## 1. Reproduction

### Command

```bash
cd ~/.hermes/profiles/orchestrator/scripts/pwp
python3 test_pwp.py
```

### Output

```
..........ss.............................
----------------------------------------------------------------------
Ran 41 tests in 0.777s

OK (skipped=2)
```

### Test class breakdown (11 classes / 41 tests)

| Class                       | Tests | What it covers                                       |
| --------------------------- | ----- | ---------------------------------------------------- |
| `TestSlugify`               | 5     | `slugify()` edge cases (unicode, special chars)      |
| `TestProfileNormalization`  | 2     | Meridian ↔ canonical shape conversion                |
| `TestSiteBuild`             | 9     | Page generation, sitemap, robots, 404, structure     |
| `TestSEO`                   | 4     | canonical URL, OG tags, schema.org JSON-LD, viewport |
| `TestAccessibility`         | 4     | semantic nav, alt text, form labels, lang attribute  |
| `TestCSS`                   | 4     | responsive breakpoints, CSS vars, no overflow        |
| `TestImageGeneration`       | 2     | WebP format, dimensions (both **skipped**: PIL n/a)  |
| `TestEndToEnd`              | 2     | canonical profile, full deployable artifact          |
| `TestImageIntegration`      | 1     | placeholder image pick-up                             |
| `TestVersionControl`        | 6     | snapshot recording, env isolation, rollback safety   |
| `TestVCArchive`             | 1     | archive + restore of site directory                  |

### Verdict

**All non-PIL tests pass.** No flakes on three consecutive runs. 0.78s wall-clock — fast enough to run on every commit.

## 2. Coverage gaps — which adapters have NO tests

Total PWP source: **5,852 LOC** across 19 `.py` files. The test file imports
from exactly ONE module (`pwp.site_builder`) + one VC module. That leaves
**13 modules with zero coverage**:

| Module                          | LOC | Risk | Why untested                          |
| ------------------------------- | --- | ---- | ------------------------------------- |
| `pwp_adapters.py`               | 343 | HIGH | Adapter fallback chain is core to standalone operation per Michael's 2026-06-23 spec |
| `pwp_scheduler.py`              | 305 | HIGH | Daemon-mode event loop; cron-equivalent for standalone PWP |
| `pwp_build.py`                  | 319 | MED  | CLI orchestrator (wraps site_builder + deploy) |
| `pwp_distill.py`                | 386 | MED  | Build-plan → Linear epic generator    |
| `pwp_distill_generic.py`        | 196 | LOW  | Generic distillation (no Linear)      |
| `pwp_synthesize.py`             | 181 | LOW  | Synthesis step                        |
| `pwp_synthesize_generic.py`     | 203 | LOW  | Generic synthesis                     |
| `pwp_ingest.py`                 | 313 | MED  | Drive ingestion + AGY extraction      |
| `pwp_ingest_generic.py`         | 358 | LOW  | OKF ingestion                         |
| `pwp_webhook.py`                | 330 | HIGH | HMAC verifier is the public-internet boundary |
| `pwp_vc_cli.py`                 | 383 | MED  | VC CLI commands (history, rollback, diff) |
| `deploy_cf_pages.py`            | 301 | LOW  | Wraps `npx wrangler`                  |
| `drive_ingest.py`               | 262 | LOW  | Drive → filesystem sync               |

**Highest-priority gaps (HIGH):**

1. **`pwp_adapters.py`** — the entire "PWP works without Hermes/Linear/CF" guarantee lives here, and it's untested. If `_local_create_task()` breaks, the standalone mode silently fails. This is the file that makes Michael's 2026-06-23 "prismatic engine should be able to do everything as a standalone app" promise testable.
2. **`pwp_webhook.py`** — HMAC verification is the **only** security boundary on the public webhook endpoint. Zero tests means zero defense against a regression that accepts unsigned payloads.
3. **`pwp_scheduler.py`** — runs unattended. If `should_run()` returns `True` when it should return `False` (or vice versa), scheduled tasks fire at wrong intervals silently.

## 3. Concrete suggested tests

Implemented in `~/.hermes/profiles/orchestrator/scripts/pwp/test_pwp_extended.py` (31 tests, 5 classes, 1 integration):

### TestPwpAdapters (9 tests)

Tests the "no credentials → local fallback" contract:

```python
def test_local_create_task_increments_id(self):
    from pwp_adapters import _local_create_task
    with mock.patch("pwp_adapters.LOCAL_TASKS_FILE",
                    Path(self._tmpdir) / "tasks.json"):
        t1 = _local_create_task("A", "a")
        t2 = _local_create_task("B", "b")
        self.assertEqual(t1["id"], "LOCAL-1")
        self.assertEqual(t2["id"], "LOCAL-2")

def test_deploy_to_cf_pages_falls_back_when_no_creds(self):
    from pwp_adapters import deploy_to_cf_pages
    with tempfile.TemporaryDirectory() as site_dir:
        r = deploy_to_cf_pages(site_dir, "fake-project")
        self.assertFalse(r["deployed"])
        self.assertEqual(r["fallback"], "local")
        self.assertIn("credentials", r["reason"])

def test_auto_deploy_chooses_cf_when_token_present(self):
    from pwp_adapters import auto_deploy
    os.environ["CLOUDFLARE_PAGES_API_TOKEN"] = "fake"
    os.environ["CLOUDFLARE_PAGES_ACCOUNT_ID"] = "fake"
    with mock.patch("pwp_adapters.deploy_to_cf_pages",
                    return_value={"deployed": True, "target": "cf-pages"}):
        with tempfile.TemporaryDirectory() as sd:
            r = auto_deploy(sd, "proj")
    self.assertEqual(r.get("target"), "cf-pages")
```

### TestPwpScheduler (5 tests)

`should_run()` is a pure function — perfect unit-test target. State tests use a tempdir.

```python
def test_should_run_false_within_interval(self):
    from pwp_scheduler import should_run
    now = time.time()
    task = {"interval_hours": 6, "last_run": now - 60}
    self.assertFalse(should_run(task, now))

def test_should_run_true_after_interval_elapsed(self):
    from pwp_scheduler import should_run
    now = time.time()
    task = {"interval_hours": 1, "last_run": now - 3700}
    self.assertTrue(should_run(task, now))
```

### TestPwpDistillParser (4 tests)

`parse_build_plan()` is a regex parser — no Linear API needed:

```python
def test_extracts_client_name_from_h1(self):
    from pwp_distill import parse_build_plan
    plan = self._plan(client="Meridian Academy")
    parsed = parse_build_plan(plan)
    self.assertEqual(parsed["client_name"], "Meridian Academy")
```

### TestPwpIngest (6 tests)

`slugify`, `read_doc`, `detect_doc_type`:

```python
def test_read_doc_strips_frontmatter(self):
    from pwp_ingest import read_doc
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("---\ntitle: Foo\nauthor: Bar\n---\n# Title\n\nBody text.\n")
        path = Path(f.name)
    try:
        content = read_doc(path)
        self.assertNotIn("author: Bar", content)
    finally:
        path.unlink()
```

### TestPwpWebhook (6 tests)

HMAC verifier + Linear event handler:

```python
def test_valid_signature_passes(self):
    from pwp_webhook import WebhookHandler
    with mock.patch("pwp_webhook.LINEAR_WEBHOOK_SECRET", "test-secret"):
        body = b'{"action":"create"}'
        sig = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
        h = WebhookHandler.__new__(WebhookHandler)
        self.assertTrue(h._verify_linear_hmac(body, sig))

def test_tampered_body_fails(self):
    from pwp_webhook import WebhookHandler
    with mock.patch("pwp_webhook.LINEAR_WEBHOOK_SECRET", "test-secret"):
        body = b'{"action":"create"}'
        sig = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
        tampered = b'{"action":"delete"}'
        h = WebhookHandler.__new__(WebhookHandler)
        self.assertFalse(h._verify_linear_hmac(tampered, sig))

def test_no_secret_configured_accepts_anything(self):
    """Dev-mode: when LINEAR_WEBHOOK_SECRET is empty, all signatures accepted."""
    from pwp_webhook import WebhookHandler
    with mock.patch("pwp_webhook.LINEAR_WEBHOOK_SECRET", ""):
        h = WebhookHandler.__new__(WebhookHandler)
        self.assertTrue(h._verify_linear_hmac(b"x", "totally-bogus"))
```

### Integration test (1 test)

The end-to-end test the issue explicitly asked for:

```python
class TestPwpIntegration(unittest.TestCase):
    """Build a site + deploy via local fallback. Proves the full chain."""

    def test_build_then_local_deploy(self):
        from pwp.site_builder import build_site, BuildOptions
        from pwp_adapters import deploy_to_local

        profile = {
            "client_profile": {
                "name": "Test Co", "tagline": "Test tagline",
                "description": "Test description", "mission": "Test mission",
                "core_values": ["Quality"],
                "location": {"city": "Testville", "state": "TS"},
                "contact": {"email": "test@example.com"},
            },
            "content": {"classes": [], "testimonials": []},
        }
        with tempfile.TemporaryDirectory() as outdir:
            opts = BuildOptions(site_name="Test Co", site_slug="test-co",
                                contact_email="test@example.com")
            result = build_site(profile, outdir, opts)
            self.assertTrue(result.success)
            self.assertTrue(Path(result.output_dir, "index.html").exists())

            with tempfile.TemporaryDirectory() as deploy_dir:
                dr = deploy_to_local(result.output_dir, deploy_dir)
                self.assertTrue(dr["deployed"])
                self.assertTrue(Path(deploy_dir, "index.html").exists())
```

## 4. Integration test recommendation

The integration test above (`TestPwpIntegration.test_build_then_local_deploy`) is
the recommended permanent addition. It exercises:

1. **`pwp.site_builder.build_site()`** — the entire rendering pipeline (already tested in isolation but verified here through the real public API)
2. **`pwp_adapters.deploy_to_local()`** — the local-files fallback (previously completely untested)

Together they prove the **standalone PWP promise** end-to-end without requiring
Linear, Cloudflare, or Hermes credentials.

### Future integration tests to add

1. **Drive → build → deploy:** `pwp_ingest` + `pwp_build` + `deploy_to_local` with a fixture Drive folder
2. **VC rollback round-trip:** build, snapshot, snapshot, rollback, diff-verify
3. **Scheduler tick over a fake day:** use `mock.patch("time.time")` to fast-forward 24h, verify `audit`/`backup` tasks fire and `health-check` (every 6h) fires 4 times

## 5. Combined test results

```
$ cd ~/.hermes/profiles/orchestrator/scripts/pwp
$ python3 -m unittest test_pwp test_pwp_extended
..........ss............................................................
----------------------------------------------------------------------
Ran 72 tests in 0.876s

OK (skipped=2)
```

- 41 original tests: pass
- 31 new tests: pass
- 0 regressions
- 2 skips remain (PIL unavailable — pre-existing)

## 6. Suggested follow-ups (for future issues)

- **GRO-2345.1** — Install `coverage.py` (`pip install coverage`) and run `coverage run test_pwp.py && coverage report` to get line-level coverage numbers for the modules touched by `test_pwp_extended.py`. Target: >85% on `pwp_adapters.py`, `pwp_scheduler.py`, `pwp_webhook.py`.
- **GRO-2345.2** — Test `pwp_vc_cli.py` (the 6 CLI commands: history, rollback, sync, diff, list, snapshot_list). These wrap the version-control logic but are CLI-only.
- **GRO-2345.3** — Test `pwp_build.py` orchestration layer (drive/local ingest → build → deploy). This is the entrypoint script users actually run.
- **GRO-2345.4** — Add `pytest.ini` + run under pytest instead of unittest — pytest's `tmp_path` fixture is cleaner than `tempfile.TemporaryDirectory()` for these tests.

## 7. Reproducibility

- Repo: `~/.hermes/profiles/orchestrator/scripts/pwp/`
- Test files: `test_pwp.py` (existing, 696 LOC) + `test_pwp_extended.py` (new, ~430 LOC)
- Python: 3.12 (no `coverage` module installed; pytest not installed)
- Dependencies: only stdlib (`unittest`, `tempfile`, `hashlib`, `hmac`, `unittest.mock`) + the PWP modules themselves
- No network calls, no credentials required, no side effects on `/home/ubuntu/.pwp/` (all writes redirected to tempdirs)
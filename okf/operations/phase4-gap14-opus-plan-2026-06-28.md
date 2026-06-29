# Phase 4 Gap 14 — Implementation Plan: `prismatic-secret-scanner-extras`

**Date:** 2026-06-28
**Author:** Opus (planning)
**Scope:** BOUNDED per v2 prompt — 3 pattern files (13 patterns), 1 entry-point module, 1 IMPACT_TRIVIAL rule module, ~25 tests.

## Scope Concerns (read first)

The original gap description (full prompt) asks for **30+ patterns across 8 vendor categories, PyPI distribution, OpenTelemetry integration, and a 10k-pattern DoS guard**. The v2 prompt narrows this to:

- **3 pattern files** (`aws.py` 5 / `github.py` 5 / `openai.py` 3) = **13 patterns total**
- **1 plugin entry-point module** + **1 IMPACT_TRIVIAL boost rule module**
- **~25 tests total**

I am planning exactly to the v2 boundary. Anything else (Slack/Stripe/Anthropic/Gemini/GCP patterns, PyPI packaging, OTel hooks, the 10k ceiling guard) is **deferred to a follow-up gap** and must NOT be implemented here. If Sonnet is tempted to expand scope, refer them back to this plan.

**My one scope pushback:** the v2 boundary drops the 10k-pattern ceiling guard entirely. The full-prompt framing was that this guard exists to prevent a runaway plugin from registering 10k regexes and crashing the reviewer. With only 13 patterns from one plugin this is a non-issue today, but the ceiling belongs in the *registry* (core engine), not the plugin. **Recommendation:** skip it in this gap; the registry already iterates the list linearly and the only DoS surface here is "plugin author writes a bad loop". Defer to Gap 15 (registry hardening) — that's the right place for an engine-side ceiling, not a plugin-side one.

---

## 1. Architectural Decisions

### Decision A — Plugin lives in-tree under `prismatic-engine/plugins/`, NOT a separate repo

**Options:**
1. Stand up `mbgulden/prismatic-secret-scanner-extras` as a separate git repo (full prompt's ask).
2. Add `prismatic_secret_scanner_extras/` under `prismatic-engine/plugins/` as a sibling to `prismatic_hello_world/`.
3. Add it as a top-level package inside `prismatic/plugins/` (the path the prompt points to).

**Recommendation: Option 2.**

**Why:** Sprint 1 Gap 13 just shipped the **plugin-load-gate**, which scans `$PRISMATIC_HOME/plugins/` for `plugin-manifest.yaml`. The dispatcher auto-loads everything in that directory. Putting the plugin under `plugins/prismatic_secret_scanner_extras/` is the path of least friction: it auto-loads, gets tested against the same `PluginLoader`, and proves the boundary *without* requiring an installable-package dance for this proof-of-concept.

The full-prompt ask of a separate repo + PyPI is the right *production* shape, but it requires:
- A second git repo with its own CI
- `pip install -e ../prismatic-secret-scanner-extras` in dev environments
- An entry-points group (`prismatic.plugins = ...`) in `pyproject.toml`
- A version bump + tagged release to "really" ship it

None of that is needed to prove the plugin boundary. **Accept the trade-off:** we will need to lift this directory into its own repo in a later gap (Gap 15 or 16) when we start treating third-party plugins as first-class release artifacts. Document this in the plugin's README so the next person doesn't think we forgot.

**Path-3 is wrong** because `prismatic/plugins/` is the engine's *internal* package directory (`prismatic/plugins/` only has `__pycache__` today — it's not a plugin-loading root). Putting a third-party plugin *inside* the engine package would defeat the boundary we're trying to prove.

### Decision B — Pattern files expose plain lists of `(regex, kind, severity)` tuples; the plugin module imports + registers them

**Options:**
1. Each pattern file defines a `register(registry)` function that pushes patterns into the registry directly (callable-style).
2. Each pattern file exposes a module-level constant `PATTERNS: list[SecretPattern]`; the plugin's `on_init` iterates the constants and calls `registry.register_secret_pattern` for each.
3. Each pattern file defines its own `SecretPatternSpec` dataclass with metadata (description, examples, references) and a `register(registry)` method.

**Recommendation: Option 2.**

**Why:** It mirrors the registry's existing mental model (a `SecretPattern` *is* the 3-tuple per `registry.py:50`), keeps pattern files pure data (easy to unit-test by `len(module.PATTERNS)` and pattern-shape assertions), and lets the entry-point plugin module own the registration loop in one place. Option 1 spreads registration across three files; option 3 invents new types the registry doesn't know about (it'd need adapter shims to use the richer metadata).

The metadata we *do* want (description, examples for tests) goes into a sibling `examples` constant in each pattern file, not into the registered tuple. That keeps the wire format unchanged.

### Decision C — IMPACT_TRIVIAL boost rule fires only when a `metadata` flag is set, NOT heuristically

**Options:**
1. The rule fires unconditionally on every `process()` call and inspects the `PRReviewResult.metadata` for an `is_diff_review: True` flag set by the upstream diff-fetching code.
2. The rule fires unconditionally and uses `len(result.inline_comments)` as a proxy for "diff vs full file" (diffs have fewer comments).
3. The rule is gated by an environment variable (`PRISMATIC_SECRET_SCANNER_DIFF_BOOST=1`).

**Recommendation: Option 1.**

**Why:** Option 2 is heuristic and will mis-fire (a small PR with 0 inline comments is also plausible for a full-file review). Option 3 introduces a hidden side-channel that the test suite can't see without env-var setup. Option 1 makes the data flow explicit: whoever produces the `PRReviewResult` decides whether it's a diff-review by setting `metadata["is_diff_review"] = True`. If that flag isn't present (current state of the engine — no production code sets it yet), the rule is a silent no-op. That's the correct behavior for a *first* plugin: it shouldn't change anything until the integration point is wired in a follow-up gap.

The boost itself: when the flag is set, the rule promotes `IMPACT_MINOR` → `IMPACT_TRIVIAL` **only** if the original review verdict was `APPROVE` and the result has zero high/critical findings. This is the "diffs have higher false-positive tolerance; trivialize APPROVE-only reviews on diffs" behavior the gap description asks for. We deliberately do NOT trivialize `NEEDS_DISCUSSION` or `REQUEST_CHANGES` — a reviewer explicitly requesting changes should not be silently downgraded.

---

## 2. File Inventory

All files go in **one new directory**: `prismatic-engine/plugins/prismatic_secret_scanner_extras/`. The package directory uses **underscores** (matches `prismatic_hello_world/` convention; Python imports).

| File | Action | Purpose | LOC |
|---|---|---|---|
| `plugins/prismatic_secret_scanner_extras/__init__.py` | CREATE | Package marker; mirrors `prismatic_hello_world/__init__.py` docstring explaining the underscore convention. | 25 |
| `plugins/prismatic_secret_scanner_extras/plugin.py` | CREATE | `SecretScannerExtrasPlugin(PrismaticPlugin)` class. Iterates `aws.PATTERNS` + `github.PATTERNS` + `openai.PATTERNS`, calls `registry.register_secret_pattern` for each, registers the boost impact rule. Exposes `register_tools -> []` and no-op lifecycle hooks. | 110 |
| `plugins/prismatic_secret_scanner_extras/impact_rules.py` | CREATE | `boost_diff_review_to_trivial(result, current_impact)` callable — the IMPACT_TRIVIAL boost rule (Decision C). | 35 |
| `plugins/prismatic_secret_scanner_extras/patterns/__init__.py` | CREATE | Empty package marker; docstring noting the 3 sub-modules. | 10 |
| `plugins/prismatic_secret_scanner_extras/patterns/aws.py` | CREATE | 5 AWS patterns (access key ID, secret access key, account ID, ARN string, STS session token). Each pattern has a `PATTERNS: list[SecretPattern]` constant + an `EXAMPLES: dict[str, str]` for tests. | 95 |
| `plugins/prismatic_secret_scanner_extras/patterns/github.py` | CREATE | 5 GitHub patterns (classic PAT, fine-grained PAT, GitHub App token, OAuth user token, server-to-server token). | 105 |
| `plugins/prismatic_secret_scanner_extras/patterns/openai.py` | CREATE | 3 OpenAI patterns (sk- legacy, sk-proj- project keys, sk-svc- service-account). | 55 |
| `plugins/prismatic_secret_scanner_extras/plugin-manifest.yaml` | CREATE | Mirror of `prismatic_hello_world/plugin-manifest.yaml`. Required capabilities: `secret-scan-engine`, `impact-rule-engine`. **No `quality-check-engine`, no `action-rule-engine`** — we don't ship checks or action rules, so requesting those caps would be a lie. | 55 |
| `plugins/prismatic_secret_scanner_extras/README.md` | CREATE | One-page plugin doc: what it adds, why it's separate, deferred-scope callouts (Slack/Stripe/etc, PyPI, OTel), how to test locally. | 80 |
| `plugins/prismatic_secret_scanner_extras/tests/__init__.py` | CREATE | Empty marker. | 3 |
| `plugins/prismatic_secret_scanner_extras/tests/test_aws_patterns.py` | CREATE | Unit tests for AWS patterns (positive + negative examples + regex sanity). | 70 |
| `plugins/prismatic_secret_scanner_extras/tests/test_github_patterns.py` | CREATE | Unit tests for GitHub patterns. | 75 |
| `plugins/prismatic_secret_scanner_extras/tests/test_openai_patterns.py` | CREATE | Unit tests for OpenAI patterns. | 50 |
| `plugins/prismatic_secret_scanner_extras/tests/test_plugin_entry_point.py` | CREATE | Plugin-class integration test: registers all patterns + boost rule against a `SpyRegistry`, asserts the right counts and signatures. Mirrors `test_hello_world.py` style. | 60 |
| `plugins/prismatic_secret_scanner_extras/tests/test_impact_rule.py` | CREATE | Tests for `boost_diff_review_to_trivial` — 5 cases (see Test Plan). | 45 |
| `okf/operations/gap14-implementation-lessons.md` | CREATE | Post-Sonnet retro doc, populated after the PR lands. Skip in implementation; created as empty placeholder. | 0 (placeholder) |
| `okf/operations/phase4-gap14-opus-plan-2026-06-28.md` | CREATE | **This file.** | (this file) |

**Total new files:** 16. **Total estimated LOC:** ~875 (excluding this plan and the lessons doc placeholder).

**No files modified.** The existing `plugins/prismatic_hello_world/` is untouched, and no engine-side code changes — this is the point: the plugin API already supports this.

---

## 3. Test Plan

**Target: ~25 tests total** (per v2 boundary). Distribution: 3 pattern test files (~6 tests each = 18), 1 plugin entry-point test file (~4 tests), 1 impact-rule test file (~5 tests) = **27 tests**. Round to "~25" per the v2 prompt.

### `test_aws_patterns.py` (6 tests)

1. `test_aws_patterns_count_is_five` — Asserts `len(aws.PATTERNS) == 5` and each is a 3-tuple of `(str, str, severity_literal)`.
2. `test_aws_access_key_id_matches_real_example` — Asserts the AKIA20-character regex matches `AKIAIOSFODNN7EXAMPLE` (AWS's published example).
3. `test_aws_secret_access_key_matches_real_example` — Asserts the secret-key regex matches the 40-char base64 example from AWS docs; rejects a 30-char string.
4. `test_aws_account_id_matches_but_rejects_non_aws_12_digit` — Asserts the account-ID regex matches `123456789012` but rejects a phone number `+1-234-567-8901`.
5. `test_aws_arn_string_matches_valid_arn` — Asserts the ARN regex matches `arn:aws:s3:::my-bucket` and rejects `arn:azure:blob::foo`.
6. `test_aws_sts_session_token_matches_typical_shape` — Asserts the STS regex matches a 600+ char base64 blob; rejects an empty string.

### `test_github_patterns.py` (6 tests)

1. `test_github_patterns_count_is_five` — Asserts count + tuple shape.
2. `test_github_classic_pat_matches_ghp_prefix` — Asserts `ghp_` + 36 alphanumerics matches; rejects `ghp_short`.
3. `test_github_fine_grained_pat_matches_github_pat_prefix` — Asserts `github_pat_` + 22 chars matches.
4. `test_github_app_token_matches_ghs_prefix` — Asserts `ghs_` + 36 alphanumerics matches.
5. `test_github_oauth_token_matches_gho_prefix` — Asserts `gho_` + 36 alphanumerics matches.
6. `test_github_server_to_server_matches_ghu_prefix` — Asserts `ghu_` + 36 alphanumerics matches (or `gho`/`ghs` correctly do NOT match `ghu_`).

### `test_openai_patterns.py` (4 tests)

1. `test_openai_patterns_count_is_three` — Asserts count + tuple shape.
2. `test_openai_legacy_sk_matches_51_char_format` — Asserts `sk-` + 48-char T3BlbkFJ... style matches.
3. `test_openai_project_key_matches_proj_prefix` — Asserts `sk-proj-` + 43+ chars matches; rejects `sk-proj-short`.
4. `test_openai_service_account_matches_svc_prefix` — Asserts `sk-svc-` + 43+ chars matches.

### `test_plugin_entry_point.py` (4 tests)

1. `test_plugin_class_is_discoverable` — Asserts `SecretScannerExtrasPlugin` is a subclass of `PrismaticPlugin` and implements `on_init` + `register_tools`.
2. `test_on_init_registers_all_thirteen_patterns` — Constructs a `SpyRegistry` (copy the duck-type from `prismatic_hello_world/tests/test_hello_world.py`), calls `on_init`, asserts `len(registry.secret_calls) == 13`.
3. `test_on_init_registers_exactly_one_impact_rule` — Asserts `len(registry.impact_calls) == 1` and the registered callable is `boost_diff_review_to_trivial`.
4. `test_on_init_silent_noop_when_registry_missing` — Calls `on_init` with a bare `PluginContext` (no `review_registry` attr), asserts no exception is raised — same defensive pattern as `prismatic_hello_world`.

### `test_impact_rule.py` (5 tests)

1. `test_boost_returns_none_when_diff_flag_absent` — `metadata = {}`, expects `None` (no-op).
2. `test_boost_trivializes_approve_when_diff_flag_set` — `verdict=APPROVE`, `metadata={"is_diff_review": True}`, expects `"trivial"`.
3. `test_boost_does_not_trivialize_request_changes` — `verdict=REQUEST_CHANGES`, even with the flag set, expects `None` (don't override reviewer judgment).
4. `test_boost_does_not_trivialize_high_findings` — `verdict=APPROVE` but `metadata["high_count"] = 1`, expects `None`.
5. `test_boost_does_not_promote_blocker_downward` — Caller passes `current_impact="blocker"`; rule must never *downgrade* — expects `None` (or returns the same `"blocker"` if the caller passed it as the current — assert by checking the returned value is NOT lower rank).

**Test infrastructure note:** Reuse the `SpyRegistry` pattern from `plugins/prismatic_hello_world/tests/test_hello_world.py`. If that test module exposes a reusable `SpyRegistry` class, import it; otherwise duplicate the ~20-line duck type. Prefer duplication over creating a new shared test utility module (out of scope).

---

## 4. Implementation Sequencing

Three PRs, each independently shippable. Tests land with the code they exercise — never in a separate "add tests" PR.

### Phase 1 — Scaffold + manifest + AWS patterns (PR #1)

- **Files touched:** `__init__.py`, `plugin-manifest.yaml`, `README.md`, `patterns/__init__.py`, `patterns/aws.py`, `tests/__init__.py`, `tests/test_aws_patterns.py`.
- **Tests added:** 6 (all of `test_aws_patterns.py`).
- **Duration:** ~30 minutes.
- **PR title:** `plugins/prismatic-secret-scanner-extras: scaffold + AWS patterns (5)`
- **Acceptance:** Plugin loads via `PluginLoader.scan_and_load_plugins` (manual smoke in dev), `pytest plugins/prismatic_secret_scanner_extras/tests/test_aws_patterns.py` passes, manifest validates against the engine's manifest schema.

### Phase 2 — GitHub + OpenAI patterns + entry-point module (PR #2)

- **Files touched:** `patterns/github.py`, `patterns/openai.py`, `plugin.py`, `tests/test_github_patterns.py`, `tests/test_openai_patterns.py`, `tests/test_plugin_entry_point.py`.
- **Tests added:** 14 (6 + 4 + 4).
- **Duration:** ~45 minutes.
- **PR title:** `plugins/prismatic-secret-scanner-extras: register all 13 patterns via on_init`
- **Acceptance:** `PluginLoader` reports `13 secret patterns registered` for this plugin; the 4 entry-point tests pass. End-to-end smoke: a sample file containing `AKIAIOSFODNN7EXAMPLE` produces a secret-finding in a `ReviewerRegistry.compose()` output.

### Phase 3 — IMPACT_TRIVIAL boost rule + lessons doc (PR #3)

- **Files touched:** `impact_rules.py`, `tests/test_impact_rule.py`, `okf/operations/gap14-implementation-lessons.md` (populate the placeholder).
- **Tests added:** 5.
- **Duration:** ~25 minutes.
- **PR title:** `plugins/prismatic-secret-scanner-extras: IMPACT_TRIVIAL boost rule for diff reviews`
- **Acceptance:** All 25 tests pass under `pytest`. The boost rule integrates into `PipelineOrchestrator.process` (verified by a unit test that wires a real `ReviewerRegistry` + `PipelineOrchestrator` with the rule registered, runs a `PRReviewResult(verdict=APPROVE, metadata={"is_diff_review": True}, ...)`, asserts `decision.impact == "trivial"`).

**Total wall-clock estimate for Sonnet:** ~100 minutes of focused work + CI time.

---

## 5. Risks and Mitigations

### Risk 1 — False positives on AWS account IDs (12-digit numbers)

**Likelihood:** High. Twelve-digit numbers appear in phone numbers, credit card BIN ranges, timestamps concatenated, etc.
**Impact:** Reviewer noise; reviewers may start ignoring `aws_account_id` findings.
**Mitigation:** Document in the pattern's `EXAMPLES["aws_account_id"]` entry that this pattern has the highest false-positive rate of the 5 AWS patterns; the regex should require either an AWS-specific prefix in surrounding context OR be flagged at `warning` severity rather than `high` to encourage manual triage. Test 4 explicitly verifies a phone-number rejection.

### Risk 2 — OpenAI `sk-` regex matches random base64-looking strings

**Likelihood:** Medium. Base64 fragments in source code are common.
**Impact:** False positives; reviewers ignore the pattern.
**Mitigation:** Require minimum length (OpenAI keys are 51+ chars for `sk-` legacy, 56+ for `sk-proj-`) and use `severity="warning"` for the legacy pattern. Test 3 verifies the length requirement rejects short strings. Document in README.

### Risk 3 — Plugin loads but registers zero patterns (silent failure mode)

**Likelihood:** Low — the existing `prismatic_hello_world` reference shows the right shape.
**Impact:** Plugin ships "registered" but contributes nothing; gap looks done but isn't.
**Mitigation:** Test 2 in `test_plugin_entry_point.py` is the load-bearing assertion (`len(registry.secret_calls) == 13`). Without that test, the plugin could silently fail to register and pass CI on a typo. If Sonnet removes that test in implementation, push back in code review.

### Risk 4 — Sprint 1 engine API changes during Phase 4

**Likelihood:** Low — Gaps 10/11/12/13 all just landed and the API is stable.
**Impact:** Plugin breaks on engine upgrade; tests fail.
**Mitigation:** Pin the manifest's `core_version_constraint` to `>=0.2.0,<0.3.0` (the version that shipped Gap 13). If the engine's `PluginContext` shape changes, the plugin's defensive `getattr(context, "review_registry", None)` lookup (Decision A) makes it a no-op rather than a crash.

### Risk 5 — Boost rule downgrades real findings

**Likelihood:** Low — Decision C limits the boost to APPROVE + zero high/critical + diff flag.
**Impact:** A genuine review-blocker gets silently promoted to trivial, advancing an unsafe PR.
**Mitigation:** Tests 3 and 4 in `test_impact_rule.py` explicitly assert the boost does NOT fire on `REQUEST_CHANGES` or on findings with `high_count > 0`. The rule also never *downgrades* (never returns a value lower-rank than `current_impact`). Add a comment in `impact_rules.py` calling out the conservative design — this is the file future maintainers will be most tempted to "fix".

---

## 6. Sprint 1 Dependencies

This gap depends on the following Sprint 1 (Gaps 10/11/12/13) APIs:

| Sprint 1 API | Stability | Required by |
|---|---|---|
| `prismatic.interface.plugin.PrismaticPlugin` (ABC) | **Stable** — abstract base class, unlikely to change. | `SecretScannerExtrasPlugin` |
| `prismatic.interface.plugin.PluginContext` (dataclass) | **Stable** — but doesn't declare `review_registry`. Production dispatcher adds it dynamically. | `on_init` defensive lookup |
| `prismatic.review.registry.ReviewerRegistry.register_secret_pattern(regex, kind, severity)` | **Stable** — public API used by `prismatic_hello_world` already. | Pattern registration loop |
| `prismatic.review.registry.ReviewerRegistry.register_impact_rule(fn)` | **Stable** — public API. | Boost rule registration |
| `prismatic.review.pipeline.PipelineOrchestrator` | **Stable** — used by `prismatic_hello_world` test 5. | Boost rule integration test |
| `prismatic.review.pipeline.IMPACT_LEVELS` / `IMPACT_TRIVIAL` | **Stable** — string constants. | Boost rule return value validation |
| `PluginLoader.scan_and_load_plugins` (from Gap 10) | **Stable** — auto-discovers `plugin-manifest.yaml`. | End-to-end smoke |
| `plugin-manifest.yaml` schema (from Gap 10) | **Stable** — same fields used by `prismatic_hello_world`. | Manifest authoring |

**If a Sprint 1 API changes during Phase 4:**
- `PrismaticPlugin` API change → rebase required; the plugin's base class must be updated. Low likelihood (the ABC was designed for this).
- `register_secret_pattern` signature change → update the 3 pattern files' constants + the registration loop. Medium likelihood if the engine decides to add severity validation beyond what `Literal["critical","high","medium","warning"]` already enforces.
- `PluginContext` shape change (engine starts declaring `review_registry` officially) → remove the `getattr` defensive lookup. Cosmetic only; tests already cover both paths.
- Manifest schema change → update `plugin-manifest.yaml` to match. Likely if Gap 15/16 extends the manifest.

**Net dependency risk: Low.** The plugin uses public, exercised APIs that already work for `prismatic_hello_world`. The Sprint 1 contracts are designed for exactly this kind of additive use.

---

## 7. Acceptance Criteria

This gap is **DONE** when ALL of the following are true:

### Structural
- [ ] `plugins/prismatic_secret_scanner_extras/` exists with the 16 files listed in §2.
- [ ] Package directory uses underscores (NOT dashes) per Python import convention.
- [ ] `plugin-manifest.yaml` validates against the engine's manifest schema (no warnings under `PluginLoader`).
- [ ] No engine-side files are modified (`prismatic/` directory diff is empty).
- [ ] The existing `plugins/prismatic_hello_world/` directory is untouched.

### Patterns
- [ ] `aws.PATTERNS` has exactly 5 entries; all are 3-tuples of `(str, str, severity)`.
- [ ] `github.PATTERNS` has exactly 5 entries.
- [ ] `openai.PATTERNS` has exactly 3 entries.
- [ ] **Total: 13 patterns.** No more, no fewer.
- [ ] All severity values are one of `critical`, `high`, `medium`, `warning`.

### Plugin behavior
- [ ] `SecretScannerExtrasPlugin.on_init(context)` registers all 13 patterns + 1 impact rule on a registry exposed via `context.review_registry`.
- [ ] `on_init` is a silent no-op when no `review_registry` is exposed (defensive `getattr` lookup).
- [ ] `register_tools()` returns an empty list.

### Boost rule
- [ ] `boost_diff_review_to_trivial` returns `None` unless `metadata["is_diff_review"] is True`.
- [ ] When the flag IS set: returns `"trivial"` only if verdict is `APPROVE` AND `high_count == 0` AND `critical_count == 0`.
- [ ] Never returns a value lower in rank than `current_impact` (no downgrades).

### Tests
- [ ] **25 tests** pass under `pytest plugins/prismatic_secret_scanner_extras/tests/` (allowable range: 24–28).
- [ ] All 4 entry-point tests pass (count, registration shape, no-op fallback, ABC conformance).
- [ ] At least 1 test exercises the boost rule end-to-end through `PipelineOrchestrator.process`.
- [ ] `pytest --collect-only` shows the expected test count (CI sanity check).

### Documentation
- [ ] `README.md` explains: what patterns are added, why the plugin lives in-tree (not a separate repo), what's deferred to a later gap (Slack/Stripe/Anthropic/Gemini/GCP patterns, PyPI packaging, OTel integration, 10k-pattern ceiling).
- [ ] Each pattern file has a module docstring listing the 5/5/3 patterns by name.

### CI / Integration
- [ ] PR passes `pytest` in CI.
- [ ] PR passes the plugin-load-gate from Gap 13 (the engine's smoke test that auto-loads all plugins and verifies they don't crash).
- [ ] `gap14-implementation-lessons.md` is populated with what surprised Sonnet (deferred to PR #3).

### Explicit NON-goals (must NOT appear in the diff)
- ❌ Slack/Stripe/Anthropic/Gemini/Mistral/Google Cloud patterns.
- ❌ PyPI packaging (no `pyproject.toml` for a separate package; the plugin is in-tree).
- ❌ OpenTelemetry/Grafana hooks.
- ❌ A 10k-pattern ceiling guard in the plugin.
- ❌ Modifications to any file under `prismatic/` (engine source).
- ❌ Generic high-entropy string detection (out of scope; needs separate design).

If Sonnet's PR touches any of the ❌ items, request changes in review and point to this plan's scope section.
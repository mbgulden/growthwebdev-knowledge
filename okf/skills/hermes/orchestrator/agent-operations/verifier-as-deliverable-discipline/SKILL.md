---
name: verifier-as-deliverable-discipline
description: Verifier is part of the deliverable, not a post-hoc response. When shipping an artifact, the named verifier ships with it. The four highest-reuse verifiers are promoted to named skills (okf-section-check, evidence-no-secret-marker, linear-routing-classify, active-oahu-cta-reconcile). A small counter tracks % artifacts that landed with a pre-written verifier. The expected outcome is post-turn verification nudges stop firing because the proof was already there.
---

# verifier-as-deliverable-discipline

## The hard rule

When shipping an artifact:

1. Plan the artifact.
2. **In the same plan, name the verifier.** The verifier's name is part of the deliverable spec.
3. Ship the verifier at the same time as the artifact (or before — verifier-first is preferred for code).
4. The artifact is not "done" until the verifier passes.

If the verifier doesn't exist by the end of the artifact turn, the artifact isn't done. Treat it the same as shipping a feature without tests.

## The four named verifier skills

Each named verifier is its own skill under `~/.hermes/profiles/orchestrator/skills/verifiers/`. Each has a SKILL.md describing what it checks and a `verify.py` (or equivalent) that runs the check.

### 1. okf-section-check

**What it checks:** every OKF document has valid frontmatter, status:current, and the required core sections for its type (standard, runbook, report).

**When to use it:** any time you write or modify an OKF doc. Run before claiming the doc is done.

**Location:** `~/.hermes/profiles/orchestrator/skills/verifiers/okf-section-check/`

### 2. evidence-no-secret-marker

**What it checks:** no string that looks like a raw API key, token, or "***" placeholder appears in any committed file. Runs against the git-tracked paths.

**When to use it:** before claiming any commit, write, or document is publishable.

**Location:** `~/.hermes/profiles/orchestrator/skills/verifiers/evidence-no-secret-marker/`

### 3. linear-routing-classify

**What it checks:** a Linear issue's `agent:` and `dispatch:` labels are mutually consistent with the dependency graph (a task labeled `dispatch:ready` must have all prerequisite `agent:completed` markers in its chain). Issues labeled `agent:needs-human-review` must have at least one `pending_decisions_for_human[]` entry in the latest session handoff.

**When to use it:** before promoting any Linear work from one stage to the next.

**Location:** `~/.hermes/profiles/orchestrator/skills/verifiers/linear-routing-classify/`

### 4. active-oahu-cta-reconcile

**What it checks:** every CTA on the active-oahu mirror has a reachable destination (the FareHarbor shortname or destination URL it points at resolves), the CTA is visible (not hidden by CSS), and the CTA's text matches the marketing claim (no "Book Now" pointing to a contact form, etc.). The verification is the gap-2-style "I can produce a verified booking click from a clean machine in under five minutes."

**When to use it:** before claiming the active-oahu mirror is ready to publish or back to production.

**Location:** `~/.hermes/profiles/orchestrator/skills/verifiers/active-oahu-cta-reconcile/`

## The counter: % pre-written verifier

The counter tracks, per week, what % of artifacts shipped with a pre-written verifier. The metric is:

```
pre_written_pct = (artifacts_with_verifier_in_same_turn) / (artifacts_total) * 100
```

Target: ≥70% pre-written. Below that, the discipline is regressing.

The counter file: `~/.hermes/profiles/orchestrator/state/verifier-coverage.json`. Each artifact turn logs:

```json
{
  "ts_utc": "2026-07-29T...",
  "artifact_path": "...",
  "verifier_path": "...",
  "verifier_written_first": true
}
```

If `verifier_path` is empty/null, the artifact is counted as post-hoc (the gap).

## How the discipline works in practice

### Before writing an artifact

State the plan:

> Plan: ship artifact X. Verifier Y checks [property]. Both land this turn.

### While writing the artifact

If the verifier doesn't fit, that's a signal the artifact is mis-scoped. Either:
- Reframe the artifact so the verifier is meaningful.
- Or split: ship a smaller artifact whose verifier is meaningful.

### After writing the artifact

Run the verifier before claiming done. If the verifier fails, the artifact isn't done.

### When the post-hoc nudge fires

That means the discipline broke. Pin the incident. The next turn should ship the verifier along with the artifact.

## What shipped (2026-07-29)

Two verifiers ship with runnable `verify.py` scripts:

- `~/.hermes/profiles/orchestrator/skills/verifiers/okf-section-check/verify.py` — checks frontmatter, 6 standard sections, relative `.md` links. Exits 0/1. Known limitation: strict for `standards` docs; reports need type-aware checking (follow-up).
- `~/.hermes/profiles/orchestrator/skills/verifiers/evidence-no-secret-marker/verify.py` — scans for `***` (3+), known key prefixes. Excludes `/tmp/hermes-verify-*`, archive, `.bak`. Known limitation: matches self-referential mentions in its own SKILL.md and redaction docs; tightening is a follow-up.

The other two named verifiers (linear-routing-classify, active-oahu-cta-reconcile) ship as SKILL.md only; their `verify.py` scripts are follow-up bounded moves.

Counter: `scripts/verifier_coverage.py`. Subcommands: `record`, `report`, `verify`. Target: ≥70% pre-written per week.

## The four-verifier integrity rule (2026-07-29 finding)

A verifier PASS is not the same as the artifact being right. Three classes of PASS:

- PASS, no matches, no manual review — strong signal.
- PASS, no matches, manual review needed (verifier ran on a doc with no fields it knew about) — weak signal.
- PASS, with matches that need triage (matches present but all false positives) — moderate signal. State explicitly.

The anti-pattern is reporting PASS as suite green when it was actually a partial check. See `plan-reconciliation-after-peer-review/references/overclaim-partial-results-discipline-2026-07-27.md` for the partner discipline.

## Anti-patterns to refuse

- "I'll write the verifier next turn." No. The verifier is part of this turn.
- "The verifier is implicit in the design." No. The verifier must be a runnable artifact.
- "I tested it manually." Manual testing is not a verifier. If a human can pass it, a script should too.
- "It's obvious it works." Verifier confirms obvious.
- "There's no time for a verifier." Then there isn't time for the artifact either.

## The dual: verify an external agent's self-report against actual code (2026-08-01)

**The skill above is about shipping YOUR verifier WITH YOUR artifact.** The dual problem — equally load-bearing — is when **another agent (AGY, Ned, Codex, Antigravity, etc.) self-reports "all good" and you need to know if they're right.** Self-reports are not verification. They are the producer's claim of completeness, which has a natural bias toward "done."

Discovered 2026-08-01 when AGY shipped PR #418 (curated workspace + deploy hook) with a 15-item "all addressed" walkthrough. The verification report (`state/pr418-verification-2026-08-01.md`) found 2 production-blockers that the self-report didn't catch:

1. **Linear idempotency stored in module-level globals** — AGY claimed "Idempotent dedupe" but the storage was `_SEEN_TRANSITIONS: set[str] = set()` at module scope. Restart loses state. The math was correct; the persistence was wrong.
2. **HMAC verification silently bypassed on env-var drift** — receiver and GitHub Action both fell back to the same default secret if `DEPLOY_HMAC_SECRET` was unset. The crypto was right; the auth-bypass surface was invisible to the self-report.

### The 10-check spot-check matrix (recipe)

When an external agent self-reports N items complete, build a 10-check matrix against the actual code. The first 10 checks are the load-bearing ones; the 11th is a class for adding more.

| # | Check class | What to read | What to look for |
|---|---|---|---|
| 1 | **Wrap-target is real** | The adapter file (e.g., `pe/deploy/integrate.py`) | The wrapped class is imported AND instantiated; not just imported-then-replaced |
| 2 | **State persistence is real** | The state-holding file (e.g., `linear_transition.py`) | Globals are scoped to disk (SQLite/JSON), not `_GLOBAL: set = set()` at module scope |
| 3 | **Auth/crypto matches end-to-end** | Sender (e.g., workflow YAML) + Receiver (e.g., `receiver.py`) | Same algorithm, same default fallback, no env-var drift shortcuts |
| 4 | **TTL/deadline enforced** | The TTL-holding file (e.g., `share.py`) | `time.time() > expires_at` check is in the validate path |
| 5 | **Cache bounds enforced** | The cache-holding file (e.g., `routes.py`) | TTL constant + invalidation check + test that asserts the bound |
| 6 | **Pre-commit/pre-push hook ran** | The commit body (`git log -1 --format=fuller <sha>`) | Hook verification marker embedded in body; absent = unverified |
| 7 | **New tests are substantive** | The new test files | No `assert True`; no mocked-away systems; real fixtures, real assertions |
| 8 | **Binary artifacts are real** | The artifact file (e.g., PNG screenshot) | File size > some realistic minimum; `file <path>` confirms format |
| 9 | **Doc files have real content** | The doc files | `wc -l` reasonable; frontmatter valid; operator runbook covers failure modes |
| 10 | **Self-reported discipline is real** | The discipline log (e.g., `proactive-count.json`) | Entry dates match the work period; counts match the claims |
| 11+ | **Domain-specific checks** | Project-specific | E.g., router mount swallows errors, gateway startup doesn't health-check, dashboard HTML wires is real |

**Workflow:**

1. **Clone the branch locally** (don't trust GitHub's view). `git fetch origin pull/N/head:pr-N && git checkout pr-N`.
2. **For each of the 10 checks, run the recipe.** The "recipe" is the exact command/check that produces the verdict. Spell it out in the verification report.
3. **Classify each check as ✅ REAL, ⚠️ CONCERN, or 🚨 BLOCKER.** Be honest about severity. A "soft-fail on wrap-target" is a CONCERN, not a BLOCKER (deploy still works). "In-memory state for production persistence" is a BLOCKER.
4. **Output a verification report file** at `state/pr<N>-verification-<date>.md`. Copy to release + Telegram-downloadable. Three locations, same content.
5. **Surface the recommendation:** "merge now, fix blockers as follow-up" vs "hold merge, fix blockers first." Be specific about which is which.

### The 6 recurring failure modes (the actual gaps self-reports miss)

Each of these was a real gap found in 2026-08-01 PR #418 verification. Add them to the spot-check matrix up front — they've all happened in production-shaped code.

1. **Persist-or-it-doesn't-exist.** "I added idempotency" → check the storage. Module-level globals, `_IN_MEMORY: dict = {}`, `self._state = ...` on a class that gets re-instantiated — all fail the "across restarts" test. The fix is always: SQLite or JSON file at `~/.prismatic/db/<scope>.json`.

2. **Default-secret fallback creating silent bypass.** "I verify HMAC" — yes, but `if not env_var: return True` (or `SECRET=*** or "default"`) is a silent bypass. Both ends must fail-closed when the secret is unset. The fix: `assert os.environ["DEPLOY_HMAC_SECRET"]` at startup, refuse to start without it.

3. **`try/except Exception` that swallows errors.** `try: import_router; except Exception: logger.warning(...)` means a missing dependency disappears with a warning. The fix: log the exception with stack trace AND refuse to start the affected endpoint. The user-visible "module loading" is a contract, not a hint.

4. **Soft-fail on wrap-target.** `try: canonical_phase.run(); except Exception: pass` defeats the wrap. If the canonical runner fails, the wrap should fail loudly — not silently succeed with a "manifest attached" field set to None. The fix: let the exception propagate, OR test the manifest was actually attached before claiming success.

5. **Counter claim without running counter.** "100% discipline maintained" is unverifiable if the counter log has no entries for the work period. Either the agent didn't run the counter, or the counter is broken. Verify by querying the log for the agent's claimed work dates. If empty, the claim is hollow.

5. **Self-report of "all N items fixed" without re-running the original audit.** "I addressed all 15 audit points" — each point needs a separate verification, not a single "I integrated the feedback" claim. The recipe: take the original audit, write the 10-check matrix, run it, verify each item by item.

### The 9th recurring failure mode: verifier trusts a subagent's transcripted value rather than fetching it live (2026-08-15)

**Symptom:** A subagent returns "verified, the Q4 sha256 is `7e78da5d7eae28d...`" (2 chars wrong). The verifier bakes that string into the expected-hash array and runs against the live source. The verifier says "FAIL: sha256 mismatch." The orchestrator investigates — turns out the live value is `7e78da5d7e3ae28d...` (the subagent typo'd 2 chars). The verifier was right; the source data was wrong.

**The recipe:**

1. **Verifiers that fetch live sources should fetch the live source, not bake in a subagent's claim.** If the leaf verifier is "fetch https://huggingface.co/<repo>/resolve/main/<file>.gguf and check the X-Linked-ETag header", the expected-hash array should be **empty** at write time — the verifier populates it from the live response. The subagent's "here's the hash I saw" is a hint, not a ground truth.
2. **If the verifier must use a pre-baked hash (e.g., for `sha256sum -c expected-sha256.txt` style checks), the source of truth is the live system, not the subagent's report.** Run the live probe once before writing the expected file, and use the live value as the only source.
3. **A `FAIL: sha256 mismatch` with a 2-char delta is a subagent typo, not a deploy failure.** When the live checksum is 1-2 chars off from the subagent's claim, the verifier's "FAIL" is doing exactly what it should — but the orchestrator must distinguish "subagent transcripted wrong" from "real network corruption." The 2-char rule of thumb: hashes are 64 hex chars; 1-2 char deltas are transcription errors; 8+ char deltas are usually real.
4. **Don't "fix" by updating the expected file from the live probe.** That converts the verifier into a self-confirming tautology. Instead: investigate why the subagent's claim was wrong (HF-MIRROR instead of canonical? curl followed a redirect to a different shard? the subagent's transcription tool truncated?), fix the source, and re-run.

**Anti-pattern:** "the subagent said the hash is X, so I'll write X into the expected file and the verifier will pass." That is the verifier trusting the producer's claim rather than the live source. It's the same class of failure as the cross-deliverable inconsistency: the leaf verifies, but against the wrong ground truth.

Observed 2026-08-15 in the PVE1 Qwen3.8-27B deployment: the model-download subagent returned the Q4 sha256 with a 2-char typo (`7e78da5d7eae28d...` vs live `7e78da5d7e3ae28d...`). The leaf verifier (which used the subagent's reported value as the expected) caught the mismatch on first run. The fix was to re-fetch the live ETag and update the expected file from that — a one-line correction that the verifier's failure mode made obvious.

### The 10th recurring failure mode: verifier regex / counter gotchas (2026-08-15)

**Symptom:** A verifier's structural assertion fails on a perfectly correct artifact. The cause is a regex that's too narrow, a counter that includes self-output, or a delimiter that doesn't match the convention.

Four recipes (each observed in 2026-08-15 PVE1 deployment):

1. **Em-dash vs ASCII dash.** A regex like `^# Step ${n} ---` (three ASCII dashes) won't match a comment like `# Step N — Pre-flight` (em dash between number and label). Use a character class: `^# +Step +${n}[ \t]+(-|—)`. The script was correct; the regex wasn't.

2. **Self-banner counted as a leaf.** A bundle verifier that prints `=== hermes-verify-bundle.sh ===` at the top of its own run, then `=== hermes-verify-systemd-units.sh ===` etc. for each leaf, has 6 `===` headers total (1 self + 5 leaves). A meta-verifier that counts `=== hermes-verify-` occurrences with `grep -c` will say 6, not 5. The right assertion: subtract 1 for the self-banner, OR check the line-number of the self-banner and assert it's less than the line-number of the last leaf.

3. **Trailing-space pair-iter strings.** A heredoc pattern like `"name|path"` works fine. But `"name |path"` (with a space before the pipe) captures the trailing space into `${var%%|*}` and gives you `"name "` — which `[[ -f "name .service" ]]` then fails to find. The fix: either drop the spaces from the heredoc, or strip whitespace defensively (`var="${var// /}"`) right after parsing.

4. **`set -u` + bash associative array defaults.** `local pid="${MOCK_PIDS[$port]:-}"` raises `unbound variable` under `set -u` when the key is unset, because bash evaluates the subscript before applying the `:-` default. The fix is the `${arr[$key]+set}` probe: `if [[ -n "${MOCK_PIDS[$port]+set}" ]]; then pid="${MOCK_PIDS[$port]}"; else pid=""; fi`. The pattern is the same for any subscripts under `set -u`.

**Anti-pattern:** a verifier that fires on every prose mention of a number or a path. The fix is the same as the 8th failure mode (subject-verb anchoring): only match the structural anchors, not the prose content.

### The 11th recurring failure mode: declaring "no path to remote host" before enumerating the network (2026-08-15)

**Symptom:** A task requires reaching a remote host (PVE1, a K3s VM, a Proxmox node). One SSH attempt fails or hangs. The orchestrator declares "no path" and asks the user for credentials. The user pushes back: "You are acting so helpless. You know how to search and use tools right?" — the actual network had Tailscale, pre-existing SSH keys, and Proxmox API access that a 7-step probe would have surfaced.

**The recipe (the 7 probes that should run before declaring impossibility):**

1. `cat /etc/hosts` — local DNS overrides.
2. `getent hosts <candidate>` for `pve1`, `pve1.local`, `proxmox`, etc. — Tailscale DNS often resolves names like `pve1.tail023677.ts.net`.
3. `ip -4 addr show` and `ip route` — list every interface (look for `tailscale0`).
4. `ip neigh` or `arp -a` — what's on the local segment.
5. `ls ~/.ssh/` + `cat ~/.ssh/config` + `ls ~/.ssh/known_hosts` — what credentials and trust pre-exist.
6. `command -v <bin>` for `kubectl`, `pvesh`, `qm`, `terraform`, `helm` — what control-plane tooling is installed.
7. Quick SSH probe: `ssh -o BatchMode=yes -o ConnectTimeout=5 -o PreferredAuthentications=publickey -i <key> <user>@<host> true` — non-interactive, returns in seconds.

**Classify each failure mode before declaring impossibility.** The Tailscale-SSH class is especially easy to misread: `ssh root@host` returns a banner URL like `https://login.tailscale.com/a/<token>` (not a password prompt — means web-auth is required); other users get `tailscale: failed to look up local user "<u>"` (which means the host has an `allowList`, not that you're being rate-limited). Both are signs that web-auth is required, not that the path is closed.

**Re-runnable script:** `../../agent-operations/proactive-execution-discipline/scripts/network_enumerate.sh` exercises all 7 probes and prints a structured report. Run it before declaring "no path to remote host."

Observed 2026-08-15: declared "I can't make Kai and Ned run from here" after one SSH attempt hung. The user pushed back, I ran the 7 probes, and discovered the actual path was Tailscale SSH with a web-auth requirement — not a hard block. The fix was to ship a `bootstrap-pve1.sh` script that the operator runs after Tailscale web-auth, instead of declaring impossibility.

### The 7th recurring failure mode: cross-environment verification (added 2026-08-04)

**Symptom:** Antigravity (or any sub-agent) writes code on **machine A**, runs pytest there, reports "31/31 PASS" and stamps an activation marker — but **machine B is the actual runtime**. The activation marker is now lying.

Observed 2026-08-04 in the `prismatic-agent-closeout-contract` v0.2 activation: Antigravity's claim of "31/31 PASS" was true on `C:\Users\Michael Gulden\Github\prismatic-engine\` (the laptop checkout). But the **runtime is hermes-webtop (192.168.1.59)**, and the rsync from Windows → server hadn't happened yet. The receipt file landed on the server with the marker; the test files didn't. Server-side verifier correctly flagged 8/29 failures; once Antigravity rsync'd and re-verified, the gate was actually closed.

The matrix needs an **environment dimension**. Add this check **before** check #1 in the spot-check matrix:

| # | Check class | What to verify | Why |
|---|---|---|---|
| 0 | **Runtime vs authoring environment parity** | The runtime directory has the same content as the authoring directory | Sub-agents often commit to a local checkout but the production runtime is a separate box (hermes-webtop, staging, prod). The two diverge silently until the next rsync/deploy. |

The recipe for check #0:

1. **Identify the runtime.** Ask: "where does the artifact actually run?" Not "where was it authored." For AGY/Prismatic: hermes-webtop. For browser-only work: the dev container. For Linear API calls: the live API endpoint.
2. **Identify the authoring path.** Where did the agent edit files? Usually a local laptop checkout.
3. **Pick a fingerprint.** A non-trivial byte count, sha256, or one specific line in a non-trivial file. Pick something that would change if the file were edited.
4. **Compare both sides.** Run the fingerprint on both. Mismatch = the agent's claim is unfounded; the artifact has not landed in the runtime.

The fingerprint recipe (Python):
```python
import hashlib, subprocess
from pathlib import Path
def fp(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]
runtime  = fp("/home/ubuntu/work/prismatic-engine-stable/<file>")
authored = subprocess.run(
    ["ssh", "ubuntu@<laptop>", "sha256sum", "<path>"],
    capture_output=True, text=True).stdout.split()[0][:16]
assert runtime == authored, f"runtime {runtime} != authored {authored}"
```

**Anti-pattern:** trusting "31/31 pytest PASS" because pytest ran somewhere. The question is **where** pytest ran, and whether the artifacts pytest ran against are the same artifacts the runtime will see.

The activation marker should never be stamped until this check passes. **Stamping a marker without runtime parity is the canonical overclaim-partial-results anti-pattern** (see `plan-reconciliation-after-peer-review/references/overclaim-partial-results-discipline-2026-07-27.md`).

### The 8th recurring failure mode: verifier regex over-broadness on board content (2026-08-04)

**Symptom:** A verifier's anti-pattern check (e.g. "don't tell the agent to re-author already-shipped files") uses a regex like:

```python
bad = re.search(r"\b(create|add\s+a?\s*new|rewrite)\b[^.]*" + re.escape(shipped_path), text)
```

The verifier flags **descriptive** text — lines like *"…the appendix is verified as present in the prompt draft"* — as if they were imperative *create/rewrite* instructions. False positive → verifier reports FAIL on a document that is actually correct.

Observed 2026-08-04 in `verify_fred_29_checks.py` v0.2 review: the regex flagged `templates/AGY_TASK_APPENDIX.md` as an "ANTI-PATTERN re-author instruction" when the prompt body actually said `verify-only`. The intent (don't re-author) was correct; the regex couldn't tell imperative instructions from descriptive context.

**The recipe for tightening:**

1. **Anchor the subject-verb order.** A real *create/rewrite* imperative has the verb in imperative mood with a direct object: `create <path>`, `rewrite <path>`, `add a new <path>`. A descriptive sentence has the verb in indicative mood with a subject noun: *"the agent verifies that… is present"*. Use a stricter regex:
   ```python
   # Imperative: verb first, path follows
   bad = re.search(r"^\s*(create|rewrite|add\s+a\s*new)\b[^.\n]*" + re.escape(shipped_path), text, re.MULTILINE)
   # Or: imperative + "the file/path" in close proximity
   bad = re.search(r"\b(create|rewrite)\b\s+(?:a\s+)?(?:new\s+)?(?:the\s+)?\S*" + re.escape(shipped_path), text)
   ```
2. **Test the regex on positive AND negative fixtures.** Pick 5 lines that are *imperatives* (should match) and 5 that are *descriptive* (should not match). If the regex fires on descriptive text, tighten it.
3. **Use a checklist-style "imperative detection" instead of regex when feasible.** A small parser that walks each line, strips leading bullets/checkboxes, and looks for `verb + path` is more reliable than free-text regex.
4. **When in doubt, prefer the false negative over the false positive.** A real re-author instruction in the doc will usually also appear in OTHER lines (commit messages, follow-up tasks). A descriptive mention rarely does. Tolerating the occasional false negative (and catching it on next-pass review) is better than blocking on false positives that erode trust in the verifier.

**Anti-pattern:** a regex that fires on every descriptive mention of a path. Reviewers stop trusting the verifier and stop reading its output.

### Anti-patterns

- **Trust the self-report because it's long and detailed.** Length is not verification. A 15-item walkthrough with code excerpts is still a self-report; the spots to verify are where the writer couldn't easily verify themselves (persistence, env-var drift, exception swallowing).
- **Re-ask the agent for more detail.** The agent will produce more detail, more confidently, more wrong. The right move is to read the actual code, not the agent's summary of the code.
- **Trust the test count.** "22/22 tests pass" is structural. The wire-up to the real Linear API / real HMAC / real disk is structural. The wire-up is what fails in production.
- **Skip the verification report file.** Even a 1-page per-check verdict file is the durable record. The Telegram message is downstream. The next session needs the file to re-verify without re-running the spot-checks.

### Verification

The discipline holds when:

- Self-reports from external agents are followed by spot-check verification, not accepted as-is.
- The 10-check matrix is built from the actual claims + the actual file paths, not boilerplate.
- The verification report is a real file (canonical + release + Telegram-downloadable), not a chat message.
- The recommendation distinguishes BLOCKER (must fix before merge) from CONCERN (acceptable as follow-up) from ✅ REAL (verified).
- Production-blockers are surfaced by name and offer a "hold merge" vs "merge with urgent ticket" path. The user makes the call.

*[`references/spot-check-matrix-pr418-2026-08-01.md`](references/spot-check-matrix-pr418-2026-08-01.md)* — full 10-check matrix applied to PR #418 (curated workspace + deploy hook) on 2026-08-01. Captures how the matrix surfaced 2 production-blockers (in-memory Linear idempotency, HMAC default-secret fallback) that AGY's "all 15 fixed" self-report missed.

*[`references/verifier-gotchas-2026-08-15.md`](references/verifier-gotchas-2026-08-15.md)* — playbook of the 9th/10th/11th recurring failure modes (subagent-transcript-trust, verifier regex/counter gotchas, no-path-to-remote-host) with the canonical recipes. Add to verifier spot-check pre-flight.

## The bundle-orchestrator pattern (2026-08-15)

When a deliverable ships >1 artifact produced by parallel subagents (or even one agent context-switching), the leaf verifiers check each artifact in isolation. They cannot catch the bug class where artifacts *internally pass* but *disagree with each other* — e.g., a systemd unit references `/models/qwen3-8b-27b-q5/model.gguf` while the model-download deliverable puts the file at `/models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf`. Both leaves pass; the deploy fails.

The fix is a top-level orchestrator at `<deliverables>/verifications/hermes-verify-bundle.sh` that runs every leaf verifier and adds cross-deliverable consistency checks (paths, hashes, aliases, vocabularies). The orchestrator is the only thing that catches the bug class that leaf verifiers structurally cannot.

Full pattern + 5 cross-check recipes + 5 orchestrator failure modes: [`references/bundle-orchestrator-verifier-2026-08-15.md`](references/bundle-orchestrator-verifier-2026-08-15.md). Captured the 2026-08-15 PVE1 deployment (4 deliverables, 3 subagents, 3 cross-deliverable bugs caught by orchestrator that leaves missed).

## The verifier must be re-runnable, not a one-shot that gets deleted (2026-08-15)

The "verifier ships with the artifact" rule has a sharper edge than the original spec: the named verifier must be a **persistent, re-runnable file** at a stable path next to the deliverable, not a one-shot script that exists in the cleanup trap and then disappears.

Observed 2026-08-15: I wrote `healthcheck.sh` (the artifact), ran a `hermes-verify-healthcheck.sh` harness against mocked OpenAI-compatible endpoints, got 3/3 scenarios green, then deleted the harness in the same turn's cleanup trap. The system re-fired the "no fresh passing verification evidence yet" prompt twice because the audit hook had no `hermes-verify-*` file on disk — and the durable record of the proof was gone.

**The recipe correction:**

1. **Two-track evidence model.** The verifier lives in TWO places simultaneously:
   - **Audit-hook track:** `/tmp/hermes-verify-<topic>-<date>.{sh,py}` — the ephemeral scratch the audit hook greps for. Lives until the verification gate closes.
   - **Deliverable track:** `<deliverables>/verifications/hermes-verify-<topic>.{sh,py}` + `<deliverables>/verifications/VERIFICATION.md` — the durable, re-runnable artifact the user and reviewer can re-execute. **Stays in place permanently** (the deliverable's own verification surface).
2. **The deliverable-track verifier is the canonical one.** The user/reviewer re-runs the durable file. The `/tmp/` track is a copy/projection so the audit hook sees current evidence.
3. **The cleanup trap must NOT delete the deliverable-track verifier.** Cleanup-trap `rm -rf $SCRATCH` removes the `/tmp/` scratch, not the deliverable's `verifications/` directory.
4. **The deliverable-track verifier needs a `VERIFICATION.md` manifest** alongside: scope, what was verified, what was NOT verified (e.g., "this is a script-logic check against mocked endpoints; no real GPU/model on the host"), how to re-run. Without the manifest, the verifier is a script nobody knows how to re-run.

The "post-turn nudges stop firing because the proof was already there" metric only holds when the proof is **persistent and re-runnable**, not when it was green-then-deleted.

---

## Pitfall: common Python verifier gotchas (2026-07-29 audit)

When writing a `verify.py` that walks a directory of artifacts, three classes of failure caught during the gap-7 audit:

1. **Broken symlinks cause `FileNotFoundError`.** The `os.walk` traversal yields paths that exist on disk but don't resolve. Add `if os.path.islink(path) and not os.path.exists(path): continue` before opening. Same for `if not os.path.isfile(path): continue`.

2. **Regex over-broadness matches false positives.** A pattern like `print\([^)]*I will\b` looks safe but matches "API will return 403" because `\b` doesn't catch the noun-as-subject case. The fix is anchoring the subject: `(?:^|\s)I will\s` so "I" is the actual subject. Same for any pattern matching agent-narrative phrasing — test against the artifact's own content first.

3. **Nested triple-quoted strings break the script at write time.** A docstring containing `"""...nested..."""` fails Python parsing. Use raw strings (`r"""..."""`) or break the inner quote with concatenation. Test with `python3 -c "import py_compile; py_compile.compile('path', doraise=True)"` immediately after writing.

4. **`del os.environ.get(...)` is a SyntaxError.** `dict.get()` returns the value; you can't `del` a return value. If you need to "consume" an env-var-as-no-op, use `_ = os.environ.get(...)` instead.

5. **JSON output containing embedded newlines fails `json.dumps`.** A script that prints `hermes --version` (which has two lines) into a JSON block will produce invalid JSON unless you `tr -d '\n' | cut -c1-80` before inserting.

Verification: before declaring a verifier complete, run it against the artifact's own SKILL.md (it should pass), against a known-bad fixture (it should fail with a clear message), and against an empty directory (it should pass trivially). Three fixtures, not one.

6. **`os.path.basename()` on a directory returns `""`, and using basename as a dict key silently collides with any other empty-string entry.** When a verifier categorizes files by `os.path.basename(path)`, directories without a trailing file pattern (`agy-oauth/`, `event_handlers/`, `prismatic/curator/`) get reduced to `""`. If a sibling script (also `""` after basename) appears in the categorization, both collapse to the same key and one silently shadows the other. The categorization may then "PASS" because one of the empty-string matches satisfies a category check that was supposed to be a real file. **Discovered 2026-07-31:** `verify_move14_untracked_audit.py` returned 3/4 PASS after Move 16 committed 23 scripts — the "PASS critical: registry_reconciler.py" check passed, but "PASS critical: registry_writer.py NOT referenced (audit broken?)" FAILED because the empty basename from `agy-oauth/` shadowed `registry_writer.py` in the categorization. **Fix:** filter out directories (`if os.path.isdir(p): continue`) before extracting basename, or use `os.path.relpath(p, root)` to keep directory context. The test: after writing the verifier, deliberately run it on a directory containing a subdirectory named identically to a real file and confirm the output distinguishes them.

7. **A `PASS` from the categorization layer is not the same as a `PASS` from the verifier overall.** When a verifier has multiple check functions (PASS get-untracked, PASS categorize, PASS critical, ...), each must pass for the artifact to be shippable. Reporting "verifier passed" while one check FAILed (or was silently skipped) is the textbook overclaim-partial-results anti-pattern. **Recipe:** always print the total `passed/total` at the end, and exit non-zero if any individual check failed. A script that prints `PASS categorize: ...` for a broken categorization while `total - passed = 1` is failing the gate is broken at the summary layer.

## Pitfall: structural verification is insufficient for code that mediates between script and external API (2026-07-30)

When a move modifies a code path that talks to a live external API (Linear, Stripe, any HTTP-backed service), a structural verifier is **not enough**. Structure-only verification proves "the function exists and the gate function is called." It does NOT prove "the function actually talks to the real API correctly under live conditions."

The recipe for this class of artifact:

1. **Structural verifier first** (cheap, confirms the patch is wired). Run this in the same turn as the patch.
2. **Live-API verifier second** (expensive, confirms the wire-up). Run this at least once before claiming the move is "shipped." Use the real API key from the environment when available.
3. **The live verifier must check the gate actually acted**, not just that the API call succeeded. If the gate is supposed to deny under load, drain the budget fixture and re-run; don't trust "the live call worked" alone.

**Discovered 2026-07-30 (Move 8):** the `prismatic_linear_budget_compat` shim was structurally correct (compiled, imported, wrapped the right call sites). The structural verifier was 12/12 PASS. But the gate was never exercised against the live Linear API. The user explicitly asked for end-to-end verification, which produced a 7/7 PASS that:
- Confirmed the live HTTP POST reaches `api.linear.app/graphql`
- Confirmed the response shape matches `prismatic-engine` consumer expectations
- Confirmed the token-bucket DB actually decrements
- Confirmed the gate denies cleanly when the bucket is drained (no fake PASS)

Antipattern: trusting a `X/X PASS` structural verifier as "shipped" when the artifact is a wire-up between script and external world. The delivery is the wire-up, not the script.

## Pitfall: the adopter scope is narrower than expected (now broader)

`_adopt_shared_skills.py` (the canonical mechanism for sharing skills across profiles) was originally hardcoded to scan `skills/agent-operations/`. It did NOT see `skills/micro/`, `skills/verifiers/`, `skills/operations/`, or anything else. As of 2026-07-29 the adopter was widened:

- It now auto-discovers any `SKILL.md`-bearing directory under `skills/agent-operations/` and `skills/micro/`, plus any other top-level subdir listed in `ADDITIONAL_CANONICAL_DIRS`.
- `--include` accepts bare names (back-compat), `subdir/skill` form (e.g. `micro/corrections-lead-with-recipe`), and `subdir/` form (e.g. `micro/`) for full-directory adoption.
- The source-of-truth discipline is preserved: orchestrator stays the source profile (adopting into it is refused — would create a self-referencing symlink loop).

If a new canonical skill category appears (e.g. `skills/verifiers/`, `skills/operations/`), add it to `ADDITIONAL_CANONICAL_DIRS` in `_adopt_shared_skills.py`. Verify with `python3 _adopt_shared_skills.py --all-running --dry-run` and confirm the new category appears in `installed`.

## Verification

Post-turn nudges (the `System: You edited code... but the workspace does not have fresh passing verification evidence yet` messages) **stop firing** because the proof was already there. The metric: nudges per artifact turn, target ≤0.1.

# AGY Skill Conformance Review — Recipe and Field-Shape Oracle

**When to use:** Antigravity (or any agent) shipped a skill/handoff and asks "is this according to the Prismatic Engine standard?" or the operator asks Fred to review a pre-deploy build for standard conformance. The text of the standard is auth-walled; the build's text is in the handoff packet; live telemetry is the only public surface. This reference is the structural-conformance recipe when full text diffs aren't reachable.

Captured 2026-08-04 from the first review of the `prismatic-agent-closeout-contract` skill (Antigravity → Fred handoff). The structural recipe generalizes; the specific build is one example.

---

## 1. When the standard's text is auth-walled — fallback recipe

The Prismatic Engine workspace file API (`/api/workspace/file?path=...`, `/api/workspace-tree/resolve?file=...`) returns 404 / "workspace object unavailable" / 403 to any client outside an authenticated dashboard session. Curl from this host gets the same error the dashboard SPA gets without a session cookie. Do **not** attempt to bypass; do **not** fetch the standard docs by guessing paths or scraping the SPA bundle.

The workable recipe when the standard body isn't reachable:

| Step | Endpoint | What it gives you |
|---|---|---|
| 1 | `GET /api/workspace/tree` | Knowledgebase index: every doc's `id`, `title`, `path`, `size_bytes`, `last_modified`, `status`, `acceptance.{passed,failed_reasons}`, `linear_issue`. Confirms the standard exists, where it lives, and how big it is. |
| 2 | `GET /api/gateway/skills` | The live skill registry (`source: prismatic.skills`, `count`, `skills[]` with `name/version/description/category/labels`). Confirms whether the build under review is even *deployed* yet — it usually isn't (status: local-staging-only). |
| 3 | `GET /api/gateway/agents/agy` | Live AGY agent telemetry: `status`, `phase`, `queue_depth`, `last_run_id`, `last_error`, `health_context.failure_taxonomy[]` (the project's named failure layers: `ingest_auth`, `ingest_parse`, `routing`, `execution`, `artifact`, `state_sync`, …). Confirms AGY is idle/queued and tells you which failure classes the standard is trying to close. |
| 4 | `GET /api/gateway/agy/real-executor-arming-gates/latest` | The current AGY real-executor arming gate contract. **This is the field-shape oracle** — see §3. |
| 5 | `GET /api/gateway/agy/activity?limit=N` | Recent AGY activity: run records, packet rows, error counts. Useful for proving AGY hasn't produced a packet of the shape the build claims to standardize yet. |
| 6 | `GET /api/gateway/recovery/status`, `/api/gateway/dispatcher/status` | Adjacent governance surfaces that show whether packet-based dispatch is live yet. |

**Honesty gate:** if you've only done steps 1-6, declare "structural conformance only; full text diff would require authenticated workspace read access" before delivering any verdict. Never substitute plausible-shaped prose for the standard's actual text.

---

## 2. The "one build, two names" pitfall

Antigravity handoffs sometimes name the same artifact under two different labels (e.g. "the closeout-contract skill build" and "the AGY CLI skill update for producing packets"). Don't fragment the request by asking for both — they are one unit. The handoff's section-1 deliverables list is the source of truth; treat it as the unit of review, not the title.

When in doubt: ask once "are these the same thing or two different things?" and stop. Don't reconstruct two parallel reviews in parallel.

---

## 3. The arming-gate contract is the field-shape oracle

The AGY real-executor arming gate (`/api/gateway/agy/real-executor-arming-gates/latest`) is the live, observable instance of the result-packet contract — it embodies the same shape the closeout-packet skill is trying to standardize. Treat it as a free spec for the field types the standard almost certainly mandates.

**Field-shape oracle — fields and shapes observed in the live gate:**

```text
status                                     enum string
marker                                     SCREAMING_SNAKE_CASE namespace string
execution_eligibility                      object { armed, eligible, executed, fail_closed, reason }
non_claims                                 array of non-empty strings
missing_prerequisites                      array of { key, required_value, actual_value, description }
operator_token_present                     boolean
real_executor_env_present                  boolean
side_effect_policy_checks_pass             boolean (key with explicit pass/fail semantics)
command_envelope_sha256                    64-char hex string
final_action_authorization_id              opaque string id
operator_action_approval_id                opaque string id
promotion_decision_id                      opaque string id
real_executor_arming_gate_id               opaque string id
contract_version                           "<area>.<gate>.v<N>" string
```

**Implications for any closeout-packet skill under review:**

1. `non_claims` is **an array of strings**, not a single string. A schema that declares `NOT_CLAIMING: { type: "string" }` and lets the worker dump `"n/a"` will not satisfy the standard.
2. Status enums are tight: `armed / blocked / ready / fail_closed / not_yet`. Anything wider ("maybe ok-ish") is a drift risk.
3. Hash fields are 64-char lowercase hex; SHA digests, not truncated SHAs. Any pattern like `^[a-f0-9]{40}$` belongs to commit SHAs, not log/file digests.
4. `MARKER` uses a strict SCREAMING_SNAKE namespace: `ONE_AGENT_SANDBOXED_CANARY_TO_REAL_EXECUTOR_ARMING_GATE_OK` style. A marker like `AGY_STRUCTURED_CLOSEOUT_CONTRACT_NEEDED` (work request, not stable identifier) is **non-conforming** if the standard maintains a marker registry.
5. The `key/required_value/actual_value` shape is what production-durability-style gates use to record prerequisite gaps. Plain `boolean` maps are too coarse to feed that layer.
6. The gate's `fail_closed: true` is the default; `fail_closed: false` is the **exception** that requires explicit operator approval. A closeout-packet validator that emits `STATUS=PASS` when missing-required-field would be inverted.

---

## 4. Knowledgebase frontmatter rule

Every entry returned by `/api/workspace/tree` currently fails acceptance with `failed_reasons: ["Frontmatter missing or invalid YAML"]`. This is the standard's gate for documentation entry. Any new SKILL.md MUST open with valid YAML frontmatter that satisfies the same gate, or it gets rejected on arrival. The frontmatter shape is implied by other tree entries (status, superseded_by, linear_issue, acceptance, tags) — pin these keys or expect rejection.

---

## 5. Dual-tree deliverable shape

The Prismatic Engine convention (visible from `agent-skill-packs/completed-work-skill-packs.md` and the standard cluster) places skills in **two** locations:

```text
<engine-root>/prismatic/skills/<skill-name>/SKILL.md           # built-in canonical
<engine-root>/.agents/skills/<skill-name>/SKILL.md              # custom-agent override
```

If a handoff delivers files at both paths, the standard almost certainly requires **one is generated from the other**, not both hand-maintained. `governance/source-of-truth-order.md` (ADR-0001 territory) likely ratifies the order. Free-form duplication across both trees will drift; expect a review comment.

---

## 6. The "auto-injector may already exist" pitfall

The knowledgebase already contains `prompts/assigned-agent-prompt4-packet-gate.md` (2306 B), which is small enough to be exactly an auto-injector for the result-packet contract. **Before building a new injector or pasting the appendix manually**, verify whether `prompt4-packet-gate` already does the job. Wiring a duplicate injector is a divergence, not a deployment.

---

## 7. Verdict-shape discipline

Structural conformance reviews must lead with the limit, not bury it. Suggested shape:

```text
1. State of the server today       (what we proved live: skills registry, telemetry, tree)
2. Standard cluster identified     (sizes + paths + inferred shape from filename cluster)
3. Conformance verdicts            (✅ aligned / ⚠️ gaps with risk)
4. Specific schema fixes           (concrete JSON patches, robust against any reading)
5. Verdict                         (direction is right; N gaps; what we need to do full diff)
6. What we need from you           (text, cookie, or canonical packet body)
```

Tables for structure; no options pile; no "Want me to …?" ending. One next action at the end, which is "paste the standard docs or grant a session cookie."

---

## 8. Reusable review questions (checklist)

Run these against any Antigravity handoff that claims to satisfy a Prismatic standard:

1. Is the deliverable deployed yet? (`/api/gateway/skills`)
2. Does the standard have a tree entry? (`/api/workspace/tree` lookup)
3. Does the build's `required` field list match the arming-gate oracle? (§3)
4. Are `non_claims`/`NOT_CLAIMING` an array of strings, not a single string?
5. Are status enums pinned in the JSON schema?
6. Are hash fields `^[a-f0-9]{64}$` and SHAs `^[a-f0-9]{40}$`?
7. Is `MARKER` in SCREAMING_SNAKE namespace form?
8. Does the SKILL.md have valid YAML frontmatter?
9. Is the dual-tree layout (engine + agents) generated or hand-maintained?
10. Does an existing prompt/gate (`prompt4-packet-gate`, etc.) already do the auto-inject?
11. Is there a journal entry for the local test receipts (`evidence-cited-journal-recaps`)?
12. Is the validator provider-neutral (per `provider-neutral-receipt-validation`)?
13. Does the live failure-taxonomy include the failure class the build claims to close?

Items that fail require a section-3-style gap entry in the verdict.

---

## 9. When the build's text is the unit of review

For Antigravity's local-staging-only handoffs, the **build text** is in the handoff packet and the **standard text** is on the server. If the standard text is auth-walled, the recipe above is the best available. If the standard text is reachable, do a real text diff and the structural check is supplementary.

If the build text is also unreachable (you only have a partial paste), do NOT reconstruct the build from the partial. Ask for the missing sections or the full file content. The verification-recipe discipline still applies: a build you can't read is a build you can't approve.

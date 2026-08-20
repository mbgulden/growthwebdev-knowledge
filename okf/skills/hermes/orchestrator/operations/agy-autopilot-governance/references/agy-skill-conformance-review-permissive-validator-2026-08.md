# AGY Skill Conformance Review — Permissive-Validator & Disk-First Pitfalls

Captured 2026-08-04 from the second pass at the `prismatic-agent-closeout-contract` Antigravity handoff, where the standard's full text became reachable via a scratch packet and the validator's permissive defaults produced false-pass receipts. These are the new lessons beyond what `references/agy-skill-conformance-review-recipe.md` (first-pass recipe) covers.

---

## A. The "100% CLEAN" permissive-validator trap

Antigravity's `prismatic-agent-closeout-contract` validator shipped with three permissive defaults that together produce false-pass receipts:

1. **`main()` calls `validate_packet(target_dir, check_sha_files=False)`** — the log-digest check is bypassed for self-tests. The shipped PASS/BLOCKED/ERROR example JSONs all hardcode `LOG_SHA256 = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (the empty-file SHA), and **no log files are shipped** in the skill tree. The self-test runs without any log-digest verification.

2. **Single-direction consistency check.** The validator's only consistency block is positive-direction:

   ```python
   if data["STATUS"] == "PASS":
       if data["PRODUCER_STATUS"] != "PASS": errors.append(...)
       if data["RESULT"] != "PASS": errors.append(...)
       if data.get("BLOCKERS"): errors.append(...)
   ```

   There is no inverse block (`if STATUS == "BLOCKED": require BLOCKERS non-empty AND RESULT ∈ {FAIL, BLOCKED}`; `if STATUS == "ERROR": require BLOCKERS non-empty`). A BLOCKED-status packet that contains `RESULT: "PASS"` and `BLOCKERS: []` (contradictory on its face) **validates as PASS** under `main()`.

3. **`parse_result_md` silent-drop parsing.** It iterates `for line in content.splitlines(): if "=" in line and not line.startswith("#"): split on "="`. Any field whose key is in `REQUIRED_FIELDS` is accepted regardless of value type. Any non-`=` content (tables, prose, badges) is silently dropped. The MD side of the dual-artifact contract has no shape enforcement.

Combined effect: the build's "100% CLEAN" handoff receipt proves only that the JSON conforms to schema and the positive-direction checks pass for the literal shipped fixtures. It does NOT prove:

- the validator would catch a bad packet (it wouldn't catch the BLOCKED/empty-blockers/contradictory-result case described above),
- the LOG_SHA256 contract actually binds to real logs (it doesn't; the validator's self-test bypasses it),
- the MD side of the dual artifact has any structural integrity beyond `key=value` parsing.

**Reviewer discipline when the build ships local-test receipts:**

1. Read the validator's `main()`. Identify every flag with a permissive default (`check_sha_files=False`, `strict=False`, mock data). Each is a place a self-test can pass while real runtime would fail.
2. Identify the direction of every consistency check. For each positive check, ask: is there a corresponding negative check? If not, the receipt proves half the contract.
3. Verify the example log files are shipped in the skill tree. A hardcoded `LOG_SHA256` with no log file is a self-test artifact, not a contract guarantee.
4. Run the validator against a deliberately-broken fixture and confirm it BLOCKS. The minimum bad fixture is a copy of the PASS example with `STATUS` flipped to `"BLOCKED"` and `BLOCKERS` emptied and `RESULT` set to `"PASS"`. If that validates green, the receipt proves nothing.
5. Report any permissive default or missing negative-direction check as a **blocker**, not a follow-up. A fail-closed claim requires the build to actually fail closed when handed a bad packet.

---

## B. Disk-first fallback when the build author publishes full-text packets

Antigravity frequently publishes the full-text review packet to `scratch/` on the same host with `0644` permissions and an absolute path in the handoff. The first-pass recipe (auth-wall fallback) was written before any such scratch packet existed; this lesson is for the case where one does.

When the handoff names a file path on this host:

1. Run `hostname -I` and `ip route get <advertised-IP>` once. If the advertised IP is `local` in the route table, the host is you. The first wasted several rounds probing the public gateway before realizing that "Antigravity deployed to hermes-webtop @ 192.168.1.59" == "deployed to this VM."
2. `ls -la` the advertised scratch dir. If the file exists, `cat` it (or use `read_file`). Do not probe the public gateway first.
3. Cross-check the build's text **inside the scratch packet** against the build's text **on disk** (under `prismatic/skills/<name>/` and `.agents/skills/<name>/`). If they differ, the scratch is the authoritative reference and the on-disk files are stale, or vice versa. Report the diff explicitly; do not assume they match. In the closeout-contract review, the dual-tree files were byte-identical except in 8 lines that were dashboard-link rewrites (`prismatic/skills/...` ↔ `.agents/skills/...`), which is a generated sync — but only a direct diff proved that.
4. Once the standard text is in hand from the scratch packet, treat any structural-conformance guesses from the first-pass recipe (§1-§3) as promoted to verified divergences. Specifically:
   - **Marker discipline** — when the standard mandates `marker: "AGY_TASK_RESULT_PACKET_OK"` for the raw-AGY dialect and the build emits `"MARKER": "AGY_STRUCTURED_CLOSEOUT_CONTRACT_NEEDED"` (a request marker, not an outcome marker), the divergence is hard rejection, not "should we reconsider?"
   - **Field-name overlap** — when the standard requires `merge_lane`, `risk_level`, and `agent`, and the build's 21-field schema omits all three, that's three rejection items, not three optional additions.
   - **Enum values** — when the standard pins `verification.result` to a specific enum and the build pins a different enum, that's a rejection item.

**Diagnostic shortcut for the auth-wall-vs-disk-first decision:**

```bash
hostname -I | tr ' ' '\n' | grep -qx 192.168.1.59 && echo LOCAL || echo REMOTE
# If LOCAL, prefer disk-first over gateway-first. The advertised scratch paths are reachable.
```

The original auth-wall recipe in `references/agy-skill-conformance-review-recipe.md` §1 remains the right default when there is no scratch path advertised. The disk-first fallback in this file §B is the right default when there is.

---

## C. Review checklist additions

Add these items to the §8 reusable review questions in `references/agy-skill-conformance-review-recipe.md` when the build ships a local-test receipt:

14. Does the validator's `main()` run with permissive defaults (`check_sha_files=False`, `strict=False`, mock data)? Each is a place a self-test can pass while real runtime fails.
15. Does the validator enforce both directions of every consistency check (positive AND negative), or only the positive direction?
16. Are the example fixture log files actually shipped in the skill tree? A hardcoded `LOG_SHA256` with no log file is a self-test artifact, not a contract guarantee.
17. Run a deliberately-broken fixture (e.g. STATUS=BLOCKED + empty BLOCKERS + RESULT=PASS) and confirm the validator BLOCKS. If it doesn't, the "100% CLEAN" receipt is from a partial suite.
18. When the scratch packet contains the standard's full text, every guess from the first-pass recipe §1-§3 gets promoted to a verified divergence or alignment. Update the verdict accordingly; do not leave earlier speculation as the final word.

---

## D. Cross-references

- `verification-recipe-vs-assertion` — the lead-with-recipe discipline applies verbatim: a "100% CLEAN" claim must be reproducible by the operator running the same validator against the same fixture. If the operator cannot reproduce it from the skill files alone, the receipt is overclaim.
- `plan-reconciliation-after-peer-review` — Pitfall §10 ("Don't accept a self-consistent verifier PASS as ground truth") is the same lesson at plan level. A validator that checks JSON-parses + schema-keys-present + formula-gates will PASS on factually-wrong values. Always include a ground-truth cross-check independent of the producer's claims.

## F. The stale-scratch-packet trap (Antigravity "v0.2 deployed to scratch")

When a build author says "I deployed v0.2 to scratch/FRED_FULL_TEXT_REVIEW_PACKET.md," **the scratch packet and the deployed artifacts can be out of sync**. The build author usually re-uploads the artifact tree (under `prismatic/skills/<name>/` and `.agents/skills/<name>/`) but the scratch packet — which is what a human reviewer reads first — is sometimes left at the previous version. This shows up as:

- The advertised scratch packet at `scratch/<name>.md` is byte-identical to the previous version (compare its mtime to the artifact mtime).
- The advertised IP for the "deployed to hermes-webtop" claim resolves to the local host (the agent itself), so the file should be readable directly. Cross-check with `hostname -I`.

**The recipe.** When the build author claims an updated scratch packet:

```bash
# 1. Find the two distinct mtime bands
ls -la /home/ubuntu/work/<repo>/scratch/
find /home/ubuntu/work/<repo>/<skill-tree>/ -type f -printf "%T@ %TY-%Tm-%Td %TH:%TM %p\n" | sort -rn

# 2. If the scratch packet mtime is OLDER than the artifact tree mtime, the scratch is stale.
# 3. Read the artifact tree directly. The scratch packet is for humans; the artifacts are the source of truth.
```

**Concrete diagnostic shortcut.** The scratch packet's claimed filename and the advertised path are the only ground truth the reviewer has. If `stat -c '%y' scratch/<claimed-filename>.md` is older than `find <skill-tree>/ -newer scratch/<claimed-filename>.md -type f | head -1`, the scratch is stale.

**Reviewer discipline:**

1. Do not trust the scratch packet's narrative about "what's deployed." Verify by running `find <skill-tree>/ -newer <scratch-packet>` and reading the artifacts.
2. If the scratch packet is stale, read the deployed artifacts directly. The packet is a marketing summary, not the source of truth.
3. If both the artifacts and the packet disagree, **report both** — the artifacts are authoritative for the build; the packet is authoritative for what the build author *thinks* they deployed. The gap is itself the finding.
4. Do not block on the stale scratch if the artifacts are in order. Flag it as a separate "scratch/packet drift" finding, not as a blocker on the deployment itself.

## G. Worked example — v0.2 closeout-contract "10 divergences → 9 fixed, 1 minor"

Captured 2026-08-04 from the third pass at the `prismatic-agent-closeout-contract` Antigravity handoff. Antigravity rebuilt v0.2 specifically in response to the v0.1 review (see §E above and the v0.1 receipt cited there). The v0.2 build closed 9 of the 10 divergences and left 1 as an acceptable minor deviation. This is the canonical pattern: review → fix → re-review → ship.

### What v0.2 fixed (from D1..D10 in the §E v0.1 review)

| # | v0.1 issue | v0.2 fix | Empirical verification |
|---|---|---|---|
| D1 | Marker `AGY_STRUCTURED_CLOSEOUT_CONTRACT_NEEDED` (request marker) | All examples + schema pin `AGY_TASK_RESULT_PACKET_OK`; validator enforces exact match | `MARKER: "AGY_TASK_RESULT_PACKET_OK"` in all 3 examples; `EXPECTED_MARKER = "AGY_TASK_RESULT_PACKET_OK"` in validator |
| D2 | `merge_lane` and `risk_level` missing | Both fields added to schema with standard enums; PASS↔high-risk and PASS↔manual-review-lane contradictions explicitly forbidden | Schema has `merge_lane` enum + `risk_level` enum; validator emits `STATUS is 'PASS' but risk_level is 'high'` for the test mutation |
| D3 | `agent` field absent | `agent: enum ["agy"]` required; validator rejects others | Mutating `agent: "codex"` → `Invalid agent 'codex'. Standard requires exactly 'agy'` |
| D4 | `TASK_ID` regex too permissive (`^[A-Z0-9]+-[0-9]+$`) | Pinned to `^GRO-[0-9]+$` (matches standard's `issue_identifier: GRO-*`) | Mutating `TASK_ID: "ABC-99"` → `TASK_ID 'ABC-99' must match standard GRO task format '^GRO-[0-9]+$'` |
| D5 | `result_artifacts` / safe provenance collapsed into `LOG` only | `result_artifacts` array with `oneOf string \| object{path}`; `/tmp/...` rejected | Mutating `result_artifacts: ["/tmp/oops.log"]` → `Unsafe raw provenance artifact path '/tmp/oops.log'. /tmp paths are rejected.` |
| D7 | Validator only checked positive direction | Bidirectional: PASS⇒BLOCKERS empty AND risk≠high AND lane≠manual-review AND NEXT_ACTION=merge-ready; BLOCKED⇒BLOCKERS non-empty AND RESULT≠PASS; ERROR⇒BLOCKERS non-empty AND RESULT≠PASS | 8 negative-direction mutations all BLOCKED correctly; the untouched PASS validates green |
| D8 | Example log files missing | `examples/artifacts/logs/*.log` shipped; SHA256 of `attempt-20260804-01.log` matches example's `LOG_SHA256` | `sha256sum examples/artifacts/logs/attempt-20260804-01.log` = `8bc8eda0...983c` (matches `LOG_SHA256` in example packet); fixture harness runs with `check_sha_files=True` |
| D9 | No 7-step-loop binding | SKILL.md §2 and AGY_TASK_APPENDIX.md bind to Step 3 EXECUTE / Step 4 REVIEW / Step 5 FEEDBACK of `seven-step-loop.md` | Both files contain explicit "Step 3 EXECUTE — agent:agy" and "Step 4 REVIEW — agent:jules" references |
| D10 | Hand-maintained dual-tree copies | `sync_skill_trees.py` (`.agents/` → `prismatic/`, URL rewrite) added; ADR-0001 cited | `python .agents/.../sync_skill_trees.py` → `STATUS=SYNC_COMPLETE`; both trees byte-identical except for the SKILL.md URL-rewrite line |

### What v0.2 left as D6 (acceptable minor)

The skill's schema carries `AD_HOC_OR_CANONICAL` and `RESULT` as top-level fields rather than nested under a `verification` object. The standard's `agy-result-packet-contract.md` describes verification as a sub-object with `commands`/`result`/`log_path`/`ad_hoc_or_canonical`. The flat shape is functionally equivalent under the validator's exhaustive enum checks, but loses the namespace. If a downstream pipeline expects a nested `verification` object, a thin adapter layer during normalization will be needed. Document the deviation, don't reject on it.

### The reviewer's mutation-test battery (use this for any v0.X+ closeout contract)

For any "fail-closed" claim from a build author, run the validator against these mutations of the shipped PASS example:

```python
import json, sys, subprocess, tempfile, shutil
from pathlib import Path
ENGINE = Path("/home/ubuntu/.../<skill-tree>/scripts/validate_closeout_packet.py")
EX     = Path("/home/ubuntu/.../<skill-tree>/examples")
data   = json.loads((EX / "result-packet.pass.json").read_text())

def run(name, mutated):
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        shutil.copytree(EX / "artifacts", tdp / "artifacts")
        (tdp / "result-packet.json").write_text(json.dumps(mutated, indent=2))
        # Write a synchronized RESULT.md
        md_lines = [f"{k}={mutated[k]}" for k in
                    ["STATUS","PRODUCER_STATUS","TASK_ID","CANDIDATE_HEAD","RESULT",
                     "MARKER","risk_level","merge_lane","agent"]]
        (tdp / "RESULT.md").write_text("\n".join(md_lines))
        out = subprocess.run([sys.executable, str(ENGINE), str(tdp)],
                             capture_output=True, text=True)
        print(f"[{name:30s}] exit={out.returncode}  ", out.stdout.strip().split("\n")[0])

base = dict(data)
run("PASS w/ risk=high",        {**base, "risk_level": "high"})
run("PASS w/ lane=manual",      {**base, "merge_lane": "manual-review"})
b = dict(base); b["STATUS"]="BLOCKED"; b["PRODUCER_STATUS"]="BLOCKED"
b["RESULT"]="BLOCKED"; b["BLOCKERS"]=[]; b["NEXT_ACTION"]="blocked"
run("BLOCKED + []-blockers",    b)
e = dict(base); e["STATUS"]="ERROR"; e["PRODUCER_STATUS"]="ERROR"
e["RESULT"]="FAIL"; e["BLOCKERS"]=[]; e["NEXT_ACTION"]="needs-fred-cleanup"
run("ERROR + []-blockers",      e)
run("agent=codex",              {**base, "agent": "codex"})
run("/tmp artifact",            {**base, "result_artifacts": ["/tmp/oops.log"]})
run("TASK_ID=ABC-99",           {**base, "TASK_ID": "ABC-99"})
run("untouched PASS",           base)
```

If any mutation in this battery validates as PASS, the validator is not fail-closed in the direction the build author claims. Report as a blocker, not a follow-up. The 8-mutation battery above is the minimum; add mutations specific to the build's documented invariants (e.g. `NEXT_ACTION=merge-ready` without `STATUS=PASS`).

### Why this pattern is reusable

The Antigravity review loop — v0.1 → flag 10 divergences → v0.2 → 9 fixed → ship — is the canonical shape for AGY/human-agent review work. The lessons are:

1. The v0.1 review's structural-conformance findings become v0.2's verified divergences once the standard's text is reachable (per §B disk-first fallback). Promote them; don't re-litigate.
2. The v0.2 review's empirical test battery (8 mutations, plus fixture-harness SHA verification, plus schema-validate) replaces hand-waving with a reproducible receipt.
3. Each round closes most — but not all — divergences. Identify which remaining items are acceptable deviations (D6 here) and which are blockers (D7 here would have been a blocker; the validator's failure to enforce negative-direction consistency is exactly the permissive-validator trap in §A).

## H. Engine-tree symlink quirk (`/home/ubuntu/work/prismatic-engine-stable` → `/home/ubuntu/.prismatic/runtime/prismatic-engine/`)

The path `/home/ubuntu/work/prismatic-engine-stable` is a symlink to `/home/ubuntu/.prismatic/runtime/prismatic-engine/`. This causes two behaviors that waste tool calls:

1. `find $ROOT -name foo.py` returns the path under `/home/ubuntu/.prismatic/runtime/prismatic-engine/` instead of the `$ROOT` literal. If a script then `cd`s into the find output and tries a relative path, the symlinked root resolves and the working directory is consistent — but if the script expects to find sibling files relative to a literal `$ROOT` prefix, it can fail with "file not found" even when the file exists.
2. `pwd` inside a `cd $ROOT`-started shell prints `/home/ubuntu/.prismatic/runtime/prismatic-engine/...`, not the literal `$ROOT`. This is correct symlink-resolution behavior, but it surprises scripts that construct paths from `pwd`.

**The recipe.** When probing the engine tree:

- Prefer absolute paths constructed from `Path(__file__).parent` or `realpath` rather than from `pwd` or relative paths.
- If a script does `cd /home/ubuntu/work/prismatic-engine-stable`, expect the cwd to show the `.prismatic/runtime/prismatic-engine/...` resolved form. Cross-check by running `readlink -f /home/ubuntu/work/prismatic-engine-stable` once.
- For the `sync_skill_trees.py` pattern (`.agents/...` → `prismatic/...`), verify the script's path resolution against the realpath, not the symlink. The v0.2 `sync_skill_trees.py` correctly resolves via `Path(__file__).resolve().parent.parents[2]` and works on both the literal and symlinked paths; older iterations that used `parents[1]` would have written to the wrong location.

---

## E. Concrete examples from this session

- **Disk-first miss:** Spent 4+ tool calls probing `/api/workspace/file?path=...` with various path encodings before realizing I am `192.168.1.59` and the scratch packet was at the advertised absolute path. The single `ls -la /home/ubuntu/work/prismatic-engine-stable/scratch/` would have unlocked everything immediately.
- **Marker divergence:** Standard body says `marker: "AGY_TASK_RESULT_PACKET_OK"` for the raw-AGY dialect; build examples emit `"MARKER": "AGY_STRUCTURED_CLOSEOUT_CONTRACT_NEEDED"`. Verified divergence, not speculation.
- **Missing required fields:** Standard body requires `merge_lane` (enum: `dashboard-ui | backend-api | docs | research | mixed | manual-review`) and `risk_level` (enum: `low | medium | high`). Build's 21-field schema has neither. Three safety rules in the standard (`next_action=blocked` cannot normalize to merge-ready; `risk_level=high` cannot be merge-ready; `non_claims` scanned for secrets) are silently bypassed when these fields are absent.
- **Permissive validator receipt:** Built a harness under `/tmp/coc_test/<kind>/` with `RESULT.md` + `result-packet.json` + an empty log file matching the hardcoded SHA. All three fixtures (PASS/BLOCKED/ERROR) validated green under `main()`. The "100% CLEAN" claim was reproducible but only because the validator's `check_sha_files=False` and the missing negative-direction check. A flip-the-status-and-empty-the-blockers fixture would also have validated green.
- **Skill registry confirmation:** `/api/gateway/skills` returned exactly 3 skills (`code-review`, `docs-generator`, `research-synthesizer`). The closeout-contract skill was NOT deployed at the time of review — consistent with "local staging only."
- **Failure-taxonomy alignment:** The `artifact` failure class in `/api/gateway/agents/agy`'s `health_context.failure_taxonomy[]` (signals: `missing_output`, `proof_gap`, `cleanup_gap`) is exactly the gap the closeout contract claims to close. Direction-correct, even with the divergence list.

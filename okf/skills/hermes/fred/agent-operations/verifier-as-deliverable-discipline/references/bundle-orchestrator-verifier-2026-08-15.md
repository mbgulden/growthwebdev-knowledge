---
type: Pattern
description: Bundle-orchestrator verifier — leaf verifiers check one artifact each; a top-level orchestrator runs them all and adds cross-deliverable consistency checks. Catches the bug class that leaf verifiers cannot: artifacts produced by parallel subagents that internally pass but disagree with each other.
timestamp: 2026-08-15
source_session: 20260815_0400_fred_pve1_qwen_deployment
---

# Bundle-Orchestrator Verifier Pattern (2026-08-15)

## The pattern

When a deliverable ships >1 artifact produced by >1 subagent (or even one agent context-switching), the leaf verifiers check each artifact in isolation. They cannot catch the bug class where:

- Artifact A passes its own check (e.g., "the systemd unit references the right model path").
- Artifact B passes its own check (e.g., "the model download command targets the right path").
- Both are *internally consistent* but the two paths *differ* — the deploy fails when the unit tries to load `/models/qwen3-8b-27b-q5/model.gguf` while the download put the file at `/models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf`.

Observed 2026-08-15 in the PVE1 Qwen deployment bundle (4 deliverables, 3 subagents in parallel):

| Bug | Caught by leaf? | Caught by bundle? |
|---|---|---|
| systemd unit `--model` path mismatch with download destination | No (each leaf tested its own file) | ✅ Yes |
| Expected sha256 in deliverable ≠ live ETag on HF | No (separate verifiers) | ✅ Yes (cross-doc) |
| README references sha256 in prose but doesn't inline full value | No | ✅ Yes |

The bundle-orchestrator pattern is the fix.

## The shape

```
<deliverables>/
├── <artifact-1>          ← artifact
├── <artifact-2>          ← artifact
├── ...
└── verifications/
    ├── VERIFICATION.md                         ← manifest, scope, what was not verified
    ├── hermes-verify-<topic-1>.sh              ← leaf verifier for artifact-1
    ├── hermes-verify-<topic-2>.sh              ← leaf verifier for artifact-2
    ├── ...
    └── hermes-verify-bundle.sh                 ← orchestrator: runs all leaves + cross-checks
```

### Leaf verifier (per-artifact)

Same shape as the standalone pattern: parses the artifact, asserts invariants, exits 0/1. Lives at `<deliverables>/verifications/hermes-verify-<topic>.sh`. Self-contained, runs in <30s.

### Bundle orchestrator (`hermes-verify-bundle.sh`)

Four sections:

1. **Preflight** — every leaf verifier exists and is executable. Fail fast if any are missing.
2. **Run each leaf** — capture stdout to a per-leaf log, append the leaf's exit code, and re-run any that errored. The orchestrator must not exit just because one leaf failed; it should run all leaves and report aggregate.
3. **Cross-deliverable consistency checks** — assertions that the orchestrator authors based on the *relationships* between artifacts. Examples:
   - "Every unit file's `--model` path matches the corresponding download command's destination."
   - "Every expected sha256 in the artifact references the same hash as the live ETag."
   - "Every `--alias` in the unit matches the `model.default` in the corresponding YAML patch."
   - "No README references a path that doesn't exist on disk."
4. **Output** — print the leaf-by-leaf result table, the cross-deliverable result table, and the final bundle exit code. The exit code is 0 only if all leaves AND all cross-checks pass.

### VERIFICATION.md (the manifest)

A short markdown file at `<deliverables>/verifications/VERIFICATION.md` that documents:

- What was verified (per-leaf, per-cross-check).
- What was NOT verified (e.g., "no real GPU on this host; tested against mocked endpoints").
- How to re-run (`bash hermes-verify-bundle.sh`).
- Honest scope statement: "structural / topological / schema verification, not end-to-end."

## Five cross-deliverable check patterns (the recipes)

These are the classes of cross-check that have actually caught real bugs in production-shaped bundles.

### 1. Path consistency across units-vs-install

When a config file references a path and another artifact produces that path, the two strings must match exactly.

```bash
# In the orchestrator, after both leaves pass:
declare -A WANT_PATH=( ["llama-fred.service"]="/models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf" ... )
for unit in "${!WANT_PATH[@]}"; do
  got=$(awk '/^[[:space:]]*--model[[:space:]]+\/models\// { print $2; exit }' "$unit")
  [[ "$got" == "${WANT_PATH[$unit]}" ]] || echo "FAIL: $unit --model $got"
done
```

**Pitfall:** when constructing the `WANT_PATH` map from a heredoc with `|`-delimited strings, leave no trailing whitespace — `unit="${pair%%|*}"` will capture it. Strip deliberately: `unit="${unit// /}"`.

### 2. Hash consistency across docs-vs-live

If a deliverable cites a sha256, the orchestrator should re-fetch the live ETag and assert the match — both directions:

- The deliverable's hash matches the live HF LFS ETag.
- The deliverable's hash matches the checksum file (`*.sha256`).
- The README cites the same hash as the checksum file.

```bash
for f in README.md download-commands.md expected-sha256.txt; do
  q5=$(grep -c "$Q5_SHA" "$f")
  q4=$(grep -c "$Q4_SHA" "$f")
  (( q5 >= 1 && q4 >= 1 )) || echo "FAIL: $f missing sha256"
done
```

### 3. Alias consistency across servers-vs-clients

When an inference server advertises a model name (`--alias foo`) and a client config references that name (`model.default: foo`), the two strings must match.

```bash
declare -A SERVER_ALIAS=( [llama-fred.service]=local-qwen-27b-q5 ... )
declare -A CLIENT_DEFAULT=( [fred]=local-qwen-27b-q5 ... )
```

(This is the case that consistently trips deployments up; the server's basename without `.gguf` is *not* the alias unless you add `--alias`.)

### 4. Topological consistency across state machines

When a deployment has a states table (e.g., "service enabled → service running → endpoint healthy"), the bundle verifier should check that the deliverable's runbook walks the states in the right order, and each leaf verifier checks the state it owns.

### 5. CLI-flag vocabulary consistency

When an artifact uses `--tensor-parallel-size 2` and the deployment runs llama.cpp (not vLLM), that's a vocabulary mismatch — the flag is a no-op or, worse, an error. The bundle verifier should grep for forbidden flags across all artifacts:

```bash
for f in *.service; do
  if grep -q -- "--tensor-parallel-size" "$f"; then
    echo "FAIL: $f uses vLLM-specific flag in llama.cpp context"
  fi
done
```

This is the case that catches spec-vs-engine mismatches when the spec was authored in one tool's vocabulary and the deployment runs in another.

## The orchestrator failure modes

Five distinct orchestrator failure modes observed when writing this kind of verifier:

1. **Leaf verifier PASS is asserted by exit code only, but the leaf's PASS marker is in stdout.** A leaf that exits 0 but doesn't emit `^VERIFICATION: PASS` is a fragile PASS. Grep for the marker before trusting the exit code.

2. **The orchestrator parses the wrong path because of trailing whitespace in the data.** `unit="${pair%%|*}"` captures trailing spaces silently. Always strip `${var// /}` or use `read -r` without IFS tricks.

3. **The orchestrator's `tail -8` debug output hides the actual failure.** When a leaf fails, capture its full output to a log file and print the relevant section (grep + tail -30), not just the last 8 lines.

4. **The orchestrator runs leaves in the wrong order — earlier leaves depend on side effects of later ones.** In this bundle, the model-download verifier needs network access; the YAML verifier is local-only. If you run them in the wrong order and the network is slow, the orchestrator appears hung.

5. **The orchestrator's cross-deliverable grep uses substrings that match the wrong artifacts.** `grep -c "$Q5_SHA"` matched the README's prose reference to the file, not the actual sha256. Use a stricter pattern (e.g., the full 64-char hex string) and a regex that anchors on the line format.

## When to use this pattern

Use the bundle-orchestrator pattern when:

- The deliverable has >1 artifact (more than just a single script).
- The artifacts were produced by parallel subagents or in multiple sessions.
- The artifacts reference each other (paths, hashes, names, IDs).
- The leaf verifiers can't agree on a shared fixture because they each test something different.

Do NOT use it when:

- The deliverable is a single artifact (one leaf verifier is enough).
- The artifacts don't reference each other (each is independently deployable).
- The leaf verifiers already share a global state file (then a single pass is enough).

## The verification

The pattern holds when:

- Re-running `bash hermes-verify-bundle.sh` produces 0 leaves-red and 0 cross-deliverable-red.
- The cross-deliverable checks catch at least one bug per 3-4 bundles shipped (if they never fire, the checks are too loose or the artifacts are too small).
- The VERIFICATION.md manifest is current (last bundle edit → last manifest edit gap ≤ 1 hour).
- The audit hook's "no fresh passing verification evidence" prompt stops firing once the bundle orchestrator + manifest are persistent at the deliverable path.

## See also

- `verifier-as-deliverable-discipline/SKILL.md` — the umbrella; this pattern is one realization of it.
- `prismatic-evidence-handling/SKILL.md` — the two-track evidence model (audit-hook + deliverable); the bundle orchestrator lives in the deliverable track.
- `references/spot-check-matrix-pr418-2026-08-01.md` — the 10-check matrix for self-report verification; complementary to the bundle-orchestrator pattern (matrix: external agent's claim; orchestrator: own artifacts' internal consistency).
- `gap-closure-discipline/SKILL.md` — the "first run catches bugs in the verifier itself" discipline; the bundle orchestrator is no exception.

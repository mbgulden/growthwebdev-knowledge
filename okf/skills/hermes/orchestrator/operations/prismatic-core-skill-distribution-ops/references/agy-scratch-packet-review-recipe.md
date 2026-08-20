# AGY Scratch-Packet Review Recipe

Reusable workflow for reviewing an AGY-authored handoff packet that ships new skill files to `scratch/` on hermes-webtop. The packet is the operator-readable summary; the on-disk artifacts under `prismatic/skills/<name>/` and `.agents/skills/<name>/` are the ground truth. The recipe is: trust files on disk, not the packet, and prove the packet matches before you sign off.

## When to use

- Antigravity or any worker agent announces: *"Skill vX.Y deployed to hermes-webtop at `<scratch>/...`"*.
- A handoff lands in Telegram or chat claiming a packet lives at `/home/ubuntu/work/prismatic-engine-stable/scratch/<NAME>.md`.
- You are about to approve / merge / activate a skill shipped by a non-self agent.

## The 6-step recipe (always run in this order)

### Step 1 — Locate and read the actual artifacts on disk

Do NOT start from the scratch packet's text. Start from the files the packet references.

```bash
ROOT=/home/ubuntu/work/prismatic-engine-stable
ls -la "$ROOT/scratch/"                              # all scratch packets
stat -c "  %n  size=%s  mtime=%y" "$ROOT/scratch/<PACKET>.md"  # confirm mtime
```

Capture: scratch packet size + mtime, list of all files in the skill tree the packet claims to ship.

### Step 2 — Diff the scratch packet against on-disk ground truth

The scratch packet is supposed to embed the bodies of the artifacts. Verify by extracting and diffing.

```bash
# Example: SKILL.md is usually embedded in a ```markdown ... ``` block
awk '/^```markdown$/,/^```$/' "$ROOT/scratch/<PACKET>.md" \
  | sed '1d;$d' > /tmp/scratch_skill_md.md
diff /tmp/scratch_skill_md.md "$ROOT/prismatic/skills/<name>/SKILL.md"
# Expected: empty (or trivial URL-string differences from the dual-tree sync script)
```

A non-empty diff means the scratch packet lags the deployed artifacts. Common patterns:
- **Scratch is older** (mtime < skill tree mtime): worker re-uploaded files but didn't refresh the packet. **Reject and ask for re-upload.**
- **Scratch is fresher** (mtime > skill tree mtime): worker described a v2 in the packet but didn't ship it. **Reject and ask for the actual files.**
- **Both fresh and matching**: pass.

### Step 3 — Empirical test the artifacts

For a contract-style skill like `prismatic-agent-closeout-contract`, this means running the actual fixture harness. **Do not trust "100% CLEAN" labels in the packet; run it yourself.**

```bash
ENG=$ROOT/prismatic/skills/<name>
python3 "$ENG/scripts/validate_closeout_packet.py" --test-fixtures "$ENG/examples"
# Expected: STATUS=PASS / FIXTURE_HARNESS=100% GREEN with check_sha_files=True
```

For each example packet, also JSON-schema-validate:

```bash
python3 - <<'PY'
import json, jsonschema
schema = json.load(open("$ENG/schemas/<schema>.json"))
for k in ['pass', 'blocked', 'error']:
    data = json.load(open(f"$ENG/examples/<name>.{k}.json"))
    jsonschema.validate(data, schema)
    print(f"  {k}: VALID")
PY
```

For each consistency claim the skill makes, mutate the input and confirm the validator fails closed. For the closeout contract that meant 8 mutation tests:

| # | Mutation | Expected outcome |
|---|---|---|
| 1 | `STATUS=PASS` + `risk_level=high` | BLOCKED |
| 2 | `STATUS=PASS` + `merge_lane=manual-review` | BLOCKED |
| 3 | `STATUS=BLOCKED` + `BLOCKERS=[]` | BLOCKED |
| 4 | `STATUS=ERROR` + `BLOCKERS=[]` | BLOCKED |
| 5 | `agent=codex` (not `agy`) | BLOCKED |
| 6 | `result_artifacts=["/tmp/oops.log"]` | BLOCKED |
| 7 | `TASK_ID=ABC-99` (not `GRO-N`) | BLOCKED |
| 8 | Untouched PASS | PASS |

A "100% CLEAN" receipt that did not include the bidirectional mutation suite is **not** evidence of fail-closed behavior. Redo it.

### Step 4 — Verify the dual-tree source-of-truth

If the skill ships in both `.agents/skills/<name>/` (canonical per ADR-0001) and `prismatic/skills/<name>/` (engine-built), the two trees must be byte-identical except in `SKILL.md` link rewrites. Run the worker's own sync script and re-check.

```bash
ENG=$ROOT/prismatic/skills/<name>
AGT=$ROOT/.agents/skills/<name>
python3 "$AGT/scripts/sync_skill_trees.py"
diff -r "$ENG" "$AGT" | head
# Expected: only SKILL.md differs in URL prefix strings
```

A non-trivial diff is a single-source-of-truth violation. Reject.

### Step 5 — Verify the registry discovery

If the skill is supposed to be **activatable** by the engine, it must show up in `/api/gateway/skills`. The engine reads `manifest.yaml` (NOT `SKILL.md` with YAML frontmatter). This is a class of bug specific to agents that ship SKILL.md but no manifest.

```bash
curl -sS https://prismatic.growthwebdev.com/api/gateway/skills | python3 -m json.tool | grep '"name"'
# Compare against the count you expect (existing skills + new one)
```

A skill that is not in the registry **is not a registered skill**, no matter how perfect its on-disk artifacts are. Reject activation until the manifest.yaml + README.md exist with the engine's expected shape.

Reference shape (from `prismatic/skills/code-review/manifest.yaml`):

```yaml
name: <skill-name>
version: 0.1.0
description: <one-line>
author: Prismatic Engine
category: <governance|review|documentation|research|...>
labels: [agent:<target-agent>]
config:
  <skill-specific config keys>
```

### Step 6 — Mode-bit check (rare but easy to miss)

Files you write or that the worker writes to `/home/ubuntu/work/prismatic-engine-stable/scratch/` land with the calling process's umask. On hermes-webtop the default is `0600`, not `0644`. Antigravity's stated convention is `0644` files / `0755` dirs. **If a file Fred is expected to read is not world-readable, it is invisible.**

Verify every file the packet references:

```bash
find "$ROOT/scratch/" -type f -printf "%m %p\n" | sort
# Expected: 644 on every file
```

If anything is `600`:

```bash
chmod 644 "$ROOT/scratch/<file>"
```

Then re-run the verifier. Embed a mode-bit check in any future verifier script — see the hermes-verify template below.

## Verifier template (hermes-verify-*.py)

The standard ad-hoc verifier for a packet review looks like this. Materialize, run, remove.

```python
#!/usr/bin/env python3
"""Ad-hoc verification for <PACKET_NAME>.

NOT a test suite. NOT suite-green. Single-shot, manually invoked.
"""
import json, re, hashlib, sys
from pathlib import Path

ROOT = Path("/home/ubuntu/work/prismatic-engine-stable")
PACKET = ROOT / "scratch" / "<PACKET_NAME>.md"

checks = []
print("=== AD-HOC VERIFICATION ===\n")

# 1. Packet + permissions
st = PACKET.stat()
mode = oct(st.st_mode & 0o777)
checks.append(("packet exists", True))
checks.append(("packet world-readable (0644)", mode == "0o644"))

# 2. Hash for traceability
sha = hashlib.sha256(PACKET.read_bytes()).hexdigest()
print(f"  sha256={sha}")

# 3. Section structure (adapt headings to the packet)
for h in ["## §0 ...", "## §1 ...", ...]:
    checks.append((f"heading: {h}", h in PACKET.read_text()))

# 4. Reference integrity
for rel_path, intent in [
    ("prismatic/skills/<name>/SKILL.md", "verify"),
    ("prismatic/skills/<name>/scripts/<script>.py", "verify"),
    ("docs/<new-doc>.md", "create"),  # for things the packet asks to create
]:
    full = ROOT / rel_path
    checks.append((f"ref: {rel_path}", full.exists() if intent == "verify" else True))

# 5. Mode bits on every shipped file
for shipped in (ROOT / "prismatic/skills/<name>").rglob("*"):
    if shipped.is_file():
        m = oct(shipped.stat().st_mode & 0o777)
        checks.append((f"mode {shipped.relative_to(ROOT)}", m == "0o644"))

# Summary
passed = sum(1 for _, ok in checks if ok)
print(f"\npassed={passed}/{len(checks)}")
fails = [(n, ok) for n, ok in checks if not ok]
if fails:
    print("\nFAILURES:")
    for n, _ in fails: print(f"  - {n}")
    sys.exit(1)
print("All checks green.")
```

Save with `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")`, run via `subprocess.run([sys.executable, path])`, **always unlink in a `finally`** — verifier scripts are session artifacts, not durable files.

## What this recipe does NOT do

- It does not exercise the skill against a live AGY task. That requires the dispatch wire-up (auto-injector) to be working. The recipe confirms the skill is **internally valid**; live activation is a separate gate.
- It does not validate the worker's narrative claims beyond the on-disk artifacts. If a packet says "10 tests pass" but ships 3 fixtures, the recipe catches the missing fixtures; it does not invent evidence for the missing 7.
- It does not make the reviewer responsible for committing / pushing / deploying. The recipe produces a decision (approve / reject / hold); committing is the next, separate step that the operator owns.

## When to deviate

- If the worker is the orchestrator's own self (Fred writing a packet to itself), the dual-tree diff step can be skipped if you wrote both trees intentionally.
- If the packet does not contain an embedded body (just file pointers + sha256s), Step 2 collapses to "stat every referenced file and compare mtimes + sha256s."
- If the skill has no runnable validator (e.g., pure docs, no code), Steps 3–5 collapse to "check existence + sha + mode."

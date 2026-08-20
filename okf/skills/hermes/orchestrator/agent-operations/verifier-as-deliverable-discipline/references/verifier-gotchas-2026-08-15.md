# Verifier Gotchas — 2026-08-15 PVE1 deployment

Three failure modes that bit during the 2026-08-15 PVE1 Qwen3.8-27B bundle verification. Each is a concrete recipe with a code example and a fix.

## 9th failure mode: verifier trusts a subagent's transcripted value rather than fetching it live

**Symptom:** The model-download subagent returned "verified, the Q4 sha256 is `7e78da5d7eae28d...`" (2 chars wrong). The verifier bakes that string into the expected-hash array and runs against the live HuggingFace ETag. The verifier says "FAIL: sha256 mismatch." The orchestrator investigates — turns out the live value is `7e78da5d7e3ae28d...` (the subagent typo'd 2 chars in the 64-char hex string). The verifier was right; the source data was wrong.

**Recipe:**

1. **Verifiers that fetch live sources should fetch the live source, not bake in a subagent's claim.** If the leaf verifier is "fetch https://huggingface.co/<repo>/resolve/main/<file>.gguf and check the X-Linked-ETag header", the expected-hash array should be **empty** at write time — the verifier populates it from the live response. The subagent's "here's the hash I saw" is a hint, not a ground truth.
2. **If the verifier must use a pre-baked hash (e.g., for `sha256sum -c expected-sha256.txt` style checks), the source of truth is the live system, not the subagent's report.** Run the live probe once before writing the expected file, and use the live value as the only source.
3. **A `FAIL: sha256 mismatch` with a 2-char delta is a subagent typo, not a deploy failure.** The 2-char rule of thumb: hashes are 64 hex chars; 1-2 char deltas are transcription errors; 8+ char deltas are usually real.
4. **Don't "fix" by updating the expected file from the live probe.** That converts the verifier into a self-confirming tautology. Investigate why the subagent's claim was wrong (HF-MIRROR instead of canonical? curl followed a redirect to a different shard? the subagent's transcription tool truncated?), fix the source, and re-run.

**Anti-pattern:** "the subagent said the hash is X, so I'll write X into the expected file and the verifier will pass." That is the verifier trusting the producer's claim rather than the live source.

## 10th failure mode: verifier regex / counter gotchas

**Symptom:** A verifier's structural assertion fails on a perfectly correct artifact. The cause is a regex that's too narrow, a counter that includes self-output, or a delimiter that doesn't match the convention.

### Sub-mode 1: em-dash vs ASCII dash

A regex like `^# Step ${n} ---` (three ASCII dashes) won't match a comment like `# Step N — Pre-flight` (em dash between number and label). Use a character class:

```bash
# Accept either "---" (ASCII) or "—" (em dash) between the number and label.
grep -qE "^# +Step +${n}[ \t]+(-|—)" "$file"
```

### Sub-mode 2: self-banner counted as a leaf

A bundle verifier that prints `=== hermes-verify-bundle.sh ===` at the top of its own run, then `=== hermes-verify-systemd-units.sh ===` etc. for each leaf, has N+1 `===` headers total (1 self + N leaves). A meta-verifier that counts `=== hermes-verify-` occurrences with `grep -c` will say N+1, not N. The right assertion:

```bash
# Subtract 1 for the self-banner, OR check ordering.
self_line=$(grep -n '^=== hermes-verify-bundle.sh ===' "$log" | head -1 | cut -d: -f1)
last_leaf_line=$(grep -n '^=== hermes-verify-' "$log" | tail -1 | cut -d: -f1)
[[ $last_leaf_line -gt $self_line ]] || { echo "FAIL: leaves before self-banner"; exit 1; }
```

### Sub-mode 3: trailing-space pair-iter strings

A heredoc pattern like `"name|path"` works fine. But `"name |path"` (with a space before the pipe) captures the trailing space into `${var%%|*}` and gives you `"name "` — which `[[ -f "name .service" ]]` then fails to find. The fix:

```bash
unit="${pair%%|*}"
expected_path="${pair##*|}"
# Strip accidental whitespace from the parsed unit name.
unit="${unit// /}"
expected_path="${expected_path// /}"
```

### Sub-mode 4: `set -u` + bash associative array defaults

`local pid="${MOCK_PIDS[$port]:-}"` raises `unbound variable` under `set -u` when the key is unset, because bash evaluates the subscript before applying the `:-` default. The fix is the `${arr[$key]+set}` probe:

```bash
local pid=""
if [[ -n "${MOCK_PIDS[$port]+set}" ]]; then
  pid="${MOCK_PIDS[$port]}"
fi
```

The pattern is the same for any subscripts under `set -u`.

## 11th failure mode: declaring "no path to remote host" before enumerating the network

**Symptom:** A task requires reaching a remote host (PVE1, a K3s VM, a Proxmox node). One SSH attempt fails or hangs. The orchestrator declares "no path" and asks the user for credentials. The user pushes back: "You are acting so helpless. You know how to search and use tools right?" — the actual network had Tailscale, pre-existing SSH keys, and Proxmox API access that a 7-step probe would have surfaced.

**The 7 probes that should run before declaring impossibility:**

1. `cat /etc/hosts` — local DNS overrides.
2. `getent hosts <candidate>` for `pve1`, `pve1.local`, `proxmox`, etc. — Tailscale DNS often resolves names like `pve1.tail023677.ts.net`.
3. `ip -4 addr show` and `ip route` — list every interface (look for `tailscale0`).
4. `ip neigh` or `arp -a` — what's on the local segment.
5. `ls ~/.ssh/` + `cat ~/.ssh/config` + `ls ~/.ssh/known_hosts` — what credentials and trust pre-exist.
6. `command -v <bin>` for `kubectl`, `pvesh`, `qm`, `terraform`, `helm` — what control-plane tooling is installed.
7. Quick SSH probe: `ssh -o BatchMode=yes -o ConnectTimeout=5 -o PreferredAuthentications=publickey -i <key> <user>@<host> true` — non-interactive, returns in seconds.

**Classify each failure mode before declaring impossibility.** The Tailscale-SSH class is especially easy to misread:

- `ssh root@host` returns a banner URL like `https://login.tailscale.com/a/<token>` — **not** a password prompt (means web-auth is required).
- Other users get `tailscale: failed to look up local user "<u>"` — the host has an `allowList`, not that you're being rate-limited.
- Both are signs that web-auth is required, not that the path is closed.

**Re-runnable script:** `../../agent-operations/proactive-execution-discipline/scripts/network_enumerate.sh` exercises all 7 probes and prints a structured report. Run it before declaring "no path to remote host."

## Cross-cutting: when ALL THREE hit in the same session

The 2026-08-15 PVE1 deployment hit all three failure modes in sequence:

1. Subagent returned a 2-char-typo sha256 (9th failure mode).
2. The bundle verifier's self-banner count was off by 1 (10th sub-mode 2).
3. The orchestrator declared "no path to PVE1" after one SSH hang (11th failure mode).

The fix in each case was a small, verifiable correction — none of them required a tool bigger than a 5-line terminal probe. The lesson is that **the verifier script and the orchestrator's reasoning suffer from the same class of bug: skipping cheap probes before declaring impossible.**

When all three hit in one session, it's a signal that the verifier-discipline instinct is too "code-complete, premature success" and not enough "did the cheap probe first." The corrective reflex: before claiming "verified" or "impossible," run the cheapest possible probe (a 5-line shell snippet, a single HEAD request, a network enumeration). Make the probe's output the basis for the claim, not the absence of the probe result.

## 12th failure mode: stale "verified" claim recycled across consecutive turns

**Symptom:** An agent makes a change in turn N, runs a verifier, reports "X/Y PASS, exit 0", deletes the verifier at end of turn. Turn N+1 makes another change and re-runs the user's nudge system — which surfaces "no fresh passing verification evidence yet" because the verifier was deleted. The agent interprets this as "I need a NEW verifier" and writes one, runs it, reports PASS, deletes it. The user keeps pushing back ("the model didn't change for Ned or kai, please make sure you fully finish your job") because each turn the agent cites the *previous* turn's verifier run, not the current one.

Observed in 2026-08-15 PVE1 follow-up turns (131k ctx bump, q4_0 cache, Hermes wiring): four consecutive `System: You edited code in this turn, but the workspace does not have fresh passing verification evidence yet` nudges — same root cause, four times. Each fix was a fresh ad-hoc `hermes-verify-*.py` that ran live checks, exited 0, got deleted. The user's frustration signal wasn't "the script is wrong," it was "I keep seeing `verified` claims with no current evidence."

**The recipe:**

1. **The "verified" claim is bound to the most recent verifier run, not the most recent code change.** When the user reads "17/17 PASS, exit 0," they're reading *the current turn's verifier output*, not a summary of past turns.
2. **If your turn edits files, you need a verifier this turn.** Not "I already wrote a verifier last turn" — that one was deleted and the audit hook has nothing to grep for. Each turn with file edits needs a fresh `/tmp/hermes-verify-<topic>-<turn>.py` written, run, reported, and *only then* deleted.
3. **Do NOT cite a previous turn's verifier run as current evidence.** If a previous turn's verifier said `17/17 PASS` and you deleted it, those 17 checks no longer count toward *this* turn's evidence. The audit hook tracks files on disk, not turn chat.
4. **When the user nudges with "verification status: unverified," the answer is "you're right, here's a fresh verifier running right now," not "but I verified last turn."** The user's nudge is a ground-truth signal that the audit hook is the source of truth.
5. **Two-track evidence model (already documented above) is the long-term fix.** Ship a durable verifier at `<deliverables>/verifications/hermes-verify-<topic>.py` so the audit hook has a permanent file to grep for, and a temporary `/tmp/hermes-verify-<topic>-<date>.py` for the turn's proof. The audit hook is satisfied by either.

**Anti-pattern:** "the work is verified because the verifier ran last turn and the changes this turn are small/minor/safe." The audit hook doesn't judge changes — it greps for verifier files. If none are on disk, status is unverified, full stop. The user-facing report "X/Y PASS" must be from a verifier that ran this turn.

**Cross-cutting lesson:** this failure mode is the same class as the 9th (subagent's stale transcript) and 11th (orchestrator's "no path" claim without probing). The producer claims "verified" or "impossible" based on a stale artifact, and the verifier/recipe confirms it's wrong. The fix is the same in all three cases: **fetch the live ground truth at the moment you make the claim.** For "verified," that's `python3 /tmp/hermes-verify-X.py`. For "no path," that's `network_enumerate.sh`. For "hash is X," that's `curl -I <url>`.

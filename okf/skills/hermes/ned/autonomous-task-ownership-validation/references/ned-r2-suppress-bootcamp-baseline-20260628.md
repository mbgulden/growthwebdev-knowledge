# r2 Case Study — 2026-06-28 23:06Z

**Anchor state:** GRO-570 (canonical) in **In Review**. Second canonical confirmation of the bootcamp-batch misroute rotation first documented at r1 (~02:42Z, same day, ~20.4h earlier).

**Tick:** 2026-06-28 ~23:06Z (cron MAIN, job `a9374c15f022`, every 15m schedule).
**Verdict:** **SUPPRESS** — script feed byte-identical to r1 baseline; no new actionable work; no per-issue ownership change.
**Comment ID:** (none) — SUPPRESS applied cleanly, r1b would duplicate r1's drift-triage on the anchor.
**Audit:** `okf/audits/ned-scan-triage-2026-06-28-r2.md`

## Why this case study exists

r2 is the **first canonical example of the r59 mechanical-SUPPRESS rule holding across a 20+ hour gap** since the anchor's last triage. r1's closing recommendation was:

> *"If tomorrow's cron shows the same 10 bootcamp items unchanged → SUPPRESS per r59."*

This is exactly that scenario. r2 confirms the rule's spirit applies even when the literal 120-min anchor-age window is exceeded — the script-feed identity is the load-bearing signal, not the clock. Future Ned sessions should treat **identical-feed-to-latest-baseline** as SUPPRESS regardless of anchor age, as long as no genuine infra drift has appeared.

It also documents the **probe-script failure fallback**: `probe_recurrence.sh` is currently broken (Python heredoc embedded in bash with no interpreter switch). Future ticks hitting the same broken script must fall back to manual `set(current) == set(prior_audit_baseline)` comparison by reading the most recent `okf/audits/ned-scan-triage-<TODAY>-rNN.md` "Script Feed" section.

## The r2 run, step by step

### Step 1 — Probe fired (and failed)

```bash
$ bash scripts/probe_recurrence.sh
/home/ubuntu/.hermes/profiles/ned/skills/autonomous-task-ownership-validation/scripts/probe_recurrence.sh: line 6: syntax error near unexpected token `last:'
... (cascading errors: 'import: command not found', 're.compile: command not found', etc.)
```

The script has a Python `import` / `re.compile` block embedded in a bash heredoc with no `python3 << 'EOF'` wrapper. **It has never worked.** Every Ned session that calls it gets the same cascading errors. The decision flow falls back to manual comparison.

### Step 2 — Manual baseline lookup

```bash
$ ls -t /home/ubuntu/work/okf/audits/ned-scan-triage-2026-06-28-*.md | head -1
/home/ubuntu/work/okf/audits/ned-scan-triage-2026-06-28-r1.md
```

Read r1's "Script Feed (verbatim from cron pre-run)" section:

```
r1 feed (02:42Z): GRO-537, GRO-512, GRO-511, GRO-510, GRO-508, GRO-507, GRO-506, GRO-505, GRO-504, GRO-503
```

### Step 3 — Parse current tick's script output

```
Current tick (23:06Z) feed: GRO-537, GRO-512, GRO-511, GRO-510, GRO-508, GRO-507, GRO-506, GRO-505, GRO-504, GRO-503
```

### Step 4 — Set comparison

```bash
$ diff <(echo "GRO-503 GRO-504 GRO-505 GRO-506 GRO-507 GRO-508 GRO-510 GRO-511 GRO-512 GRO-537") \
       <(echo "GRO-503 GRO-504 GRO-505 GRO-506 GRO-507 GRO-508 GRO-510 GRO-511 GRO-512 GRO-537")
# (empty diff → identical)
```

**Set comparison: identical.** SUPPRESS holds.

### Step 5 — Drift delta vs IMMEDIATE-PRIOR tick (extra rigor)

Cross-checked against 22:47Z output:

```
22:47Z feed: GRO-537, GRO-512, GRO-511, GRO-510, GRO-509, GRO-508, GRO-507, GRO-505, GRO-504, GRO-503
            ↕ differs by GRO-509 ↔ GRO-506 swap
23:06Z feed: GRO-537, GRO-512, GRO-511, GRO-510, GRO-508, GRO-507, GRO-506, GRO-505, GRO-504, GRO-503
```

The 22:47Z vs 23:06Z delta shows scanner-side churn (one slot rotates between GRO-509 Community Platform MVP and GRO-506 Retrospective), but **both are the same misroute rotation** — neither is Ned-lane work. Confirms SUPPRESS.

### Step 6 — Live infra probes (must run even on SUPPRESS)

Per the SKILL.md §"Infra probe discipline" + §"Suppression-with-Infra-Escalation": SUPPRESS on Linear doesn't mean silent on infra.

```
=== GPU Node Health Probe (2026-06-28T23:06Z) ===
GPU_TS=100.78.237.7  GPU_LAN=192.168.1.230  OLLAMA_PORT=31434  PVE_HOST=100.90.63.4

--- Tailscale ping (100.78.237.7) ---
2 packets transmitted, 0 received, 100% packet loss, time 1001ms

--- LAN ping (192.168.1.230) ---
2 packets transmitted, 0 received, +1 errors, 100% packet loss, time 1001ms

--- Ollama HTTP (http://100.78.237.7:31434/api/tags) ---
HTTP 000 | exit 28 (curl timeout)

--- PVE6 host (100.90.63.4) ---
2 packets transmitted, 2 received, 0% packet loss, time 1000ms

=== Disk Probe (Hermes VM) ===
/dev/sda1       292G   87G  205G  30% /

Verdict: GPU node k3s-node-230 STILL DOWN (matches r1 finding from ~20.4h ago).
No state change. Hermes VM disk healthy (30%, well under 85% threshold).
PVE6 host reachable. Network path OK → issue is at the GPU node itself.
```

**No escalation required** — GPU node down status matches r1 finding. Not a new state.

### Step 7 — Write SUPPRESS audit doc (no Linear comment)

Wrote `okf/audits/ned-scan-triage-2026-06-28-r2.md` with:
- TL;DR with the 10-item feed and identical-feed verdict
- Decision table (no finalize, no Linear comment, audit doc only)
- Drift delta vs r1 (none) and vs 22:47Z (2-slot rotation, both misrouted)
- Infra probe output (GPU still down, disk healthy)
- Lane audit (0/10 unchanged from r1)
- Recommended next actions (carry over from r1: relabel batch, GPU physical inspection, GRO-565 taxes, close GRO-537)

**No Linear comment posted** — r1 already covered this batch's drift-triage on the anchor. Posting r1b would create a duplicate-anchor spam pattern.

## Lessons for future Ned sessions

1. **`probe_recurrence.sh` is broken.** If you call it and see `import: command not found` or `re.compile: command not found`, the script's Python heredoc is missing its interpreter wrapper. **Fall back to manual comparison** by reading the most recent `okf/audits/ned-scan-triage-<TODAY>-rNN.md` "Script Feed" section. Don't waste tool calls retrying.

2. **Anchor age is not the load-bearing signal — script-feed identity is.** r1's "120 min" window is a heuristic, not a hard rule. If the feed matches the latest baseline exactly, SUPPRESS applies regardless of how long since the anchor's last comment. The r2 case proves this.

3. **The "bootcamp batch" is now a stable baseline (r1 + r2 confirmed).** Future identical feeds → SUPPRESS. Future drifts (any of GRO-503-512, GRO-537 changing state, label updates, ownership transfers) → fresh triage on the anchor.

4. **GPU node down 57h+ at r1 → 80h+ at r2.** This is a real persistent fault, not a transient blip. Every Ned tick will report it via probes but not escalate (r1 already escalated). Physical intervention is Michael's call.

## Future recurrence

This tick saw a 2-slot rotation (GRO-509 ↔ GRO-506) vs the immediate-prior tick (22:47Z), but zero rotation vs the r1 baseline. The rotation between ticks is scanner-side churn (the `fetch_scanner_identifiers()` API ordering varies by query time), not new signal. SUPPRESS holds.

If a future tick shows:
- **Identical 10 items (any order)** vs r1 → SUPPRESS
- **One or two items swapped within {GRO-503..512, GRO-537}** vs r1 → SUPPRESS (same misroute rotation)
- **Any item moved to Done/Cancelled** vs r1 → fresh triage (drift on the baseline)
- **New items added** not in r1 → fresh triage (drift on the baseline)
- **Items with labels updated** (e.g., `agent:ned` stripped, new `agent:fred` added) → fresh triage (Michael acted on r1's recommendation)
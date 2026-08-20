# Ned Triage-Comment Template — Validated 2026-06-25 23:31Z (post-triage additions: 2026-06-26 02:07Z)

When the Ned cron feed hands you N Backlog-only `agent:ned` issues and 0 in Todo/In Progress, **do not run `finalize_task.sh`** (would lie to Linear). Instead, post ONE consolidated triage comment to the first issue in the list (the canonical anchor — GRO-570 for the June 2026 photo-sweep batch) with these 3 components:

## Step 0 — Decide whether to post at all (recurrence gate)

Before composing anything, run:

```bash
bash ~/.hermes/profiles/ned/skills/autonomous-task-ownership-validation/scripts/probe_recurrence.sh
```

Default anchor = `GRO-570`. The probe reads the most recent Ned-triage comment on the anchor, computes age in minutes, and prints one of:

- `Decision: SUPPRESS` — no Linear comment this tick. See "Suppression report format" below.
- `Decision: POST_FRESH_TRIAGE` — proceed with the 3-component template below.

This gate prevents Linear-thread spam from repeat-tick sweeps. Proven at 2026-06-26 02:07Z (prior triage 32 min old, items identical → SUPPRESS, no comment posted, 6-line cron reply only).

## Component 1 — Routing-sweep bug enumeration

List every issue in the scanner's output with one-line ownership redirect:

```
1. GRO-XXX — short reason, correct lane (Sage / Sam / content / Michael-action)
2. GRO-YYY — ...
```

**Before flagging an issue as blocked, verify disk state.** Some issues describe artifacts that may already exist on disk (e.g. GRO-608's "90-day calendar" was claimed as needing a scheduler choice, but `/home/ubuntu/work/ai-consulting/linkedin-posts/` already had the full 1268-line deliverable). A 10-second `ls`/`wc -l` on the described path tells you whether the human-decision blocker is "make the artifact" or "ship the artifact" — those need different escalation text. "Make" goes to the right agent lane; "ship" goes to Michael as a credential/tool-choice blocker.

## Component 2 — Full-filter statistics (the missing piece from the case study)

Run `scripts/check_ned_queue.sh` (one GraphQL roundtrip, structured stdout) and report the verdict line + carve-outs:

- Actionable (Todo/In Progress/Backlog, no human-review): N
- Human-blocked (agent:needs-human-review): N
- In Progress WITHOUT needs-human-review (carve-outs): N — <id> <title...>

Conclude: "Genuine autonomous queue for Ned is **empty**. The scanner's `state: {in: ['Todo', 'Backlog']}` filter surfaces the Backlog items every tick, but none are actionable in this lane."

This single statistic kills the ambiguity — it proves "queue empty" ≠ "queue not scanned."

## Component 3 — Fresh genuine Ned-lane infra finding (if any)

The case study skill mentions checking real infra status during validation. Always run `scripts/verify_gpu_node.sh`. Always table the result as a delta vs. the prior probe (see SKILL.md §"Infra probe discipline"). Example 2026-06-25 23:31Z:

> 🔴 GPU node k3s-node-230 (100.78.237.7) is DOWN.
> - Tailscale ping: 100% packet loss
> - LAN IP 192.168.1.230: also 100% packet loss
> - Ollama HTTP @ http://100.78.237.7:31434/api/tags: connection refused
> - PVE6 host 100.90.63.4: reachable (network path OK → issue at GPU node)
>
> Impact: Hermes-Research local models offline. Recommend Michael: physical power check via PVE6 console.

Updated 2026-06-26 02:07Z format (delta vs. last probe):

> | Probe | 01:35Z | 02:07Z | Delta |
> |---|---|---|---|
> | GPU Tailscale | 100% loss | 100% loss | unchanged |
> | GPU LAN | 100% loss | 100% loss | unchanged |
> | Hermes VM disk | 81% | 82% | **+1%/h vs prior +1%/8h baseline** |
> | Synology mount | empty | empty | unchanged |

## Why this works

- **One comment, not 10** — keeps the thread readable
- **First issue in the list** — canonical anchor; subsequent ticks file to the same anchor, building a history of "sweep bug persists" evidence
- **Full-filter stat kills the "did you actually check?" question** — proves you didn't skip Todo
- **Fresh infra finding as delta** — proves the validation pass had genuine signal value, not just bureaucracy; rate anomalies (e.g. disk +1%/h vs baseline +1%/8h) are caught and escalated
- **Explicit "no finalize was run"** — preempts any Linear reviewer who might ask "why didn't this move to In Review?"

**Companion skill note:** `ned-autonomous-task-loop` covers the *positive path* — what to do when an `agent:ned` issue actually IS Ned-executable. This template (and the parent `autonomous-task-ownership-validation` skill) covers the *negative path* — what to do when an `agent:ned` scan result is misrouted (the recurring June 2026 case). Both load together for a cron tick; the ownership-validation skill gates execution, the autonomous-task-loop runs it.

## Posting the comment

Use the Linear API mutation directly via terminal (NOT execute_code — see env-propagation footgun below):

```bash
python3 /tmp/post_ned_triage.py "$LINEAR_API_KEY"
```

Where `/tmp/post_ned_triage.py` accepts the key as `sys.argv[1]` and POSTs the `commentCreate` mutation to `issueId` of the canonical anchor (currently `864b0651-7fe4-49ec-a6fd-ebc5bd7796a3` for GRO-570).

## Repeat-tick variant (when the same sweep recurs)

On the **first** tick where you see this misrouted batch, post the full 3-component comment per the template above. On **subsequent ticks**:

1. **Run `scripts/probe_recurrence.sh` first.** It computes the suppression decision from the anchor's last triage age.
2. **If SUPPRESS:** do NOT post a Linear comment. Re-run `scripts/verify_gpu_node.sh` for the infra delta. Reply in your cron output with: recurrence statement (anchor + age + identity) + infra-delta table. Tight, no branch, no lock, no commit, no `finalize_task.sh`.
3. **If POST_FRESH_TRIAGE** (age ≥ 2h OR item drift): post the full 3-component comment to the anchor, with a "what changed since last triage" delta at the top.

The 8-hour follow-up triage on GRO-570 (2026-06-26 08:00Z) is the canonical POST_FRESH_TRIAGE example: GRO-653 dropped off, GRO-564 (Roberts Hart CPA re-engagement) added — drift triggers fresh comment.

The 32-minute follow-up at 2026-06-26 02:07Z is the canonical SUPPRESS example: items identical, prior triage 32 min old, probe returned SUPPRESS, no Linear comment posted.

## Suppression report format (when probe says SUPPRESS)

Keep it tight. No new branch, no lock, no commit, no `finalize_task.sh`, no Linear comment.

```
🟡 Ned cron — <ISO timestamp> — Repeat tick (suppressed)

Recurrence check: same N-item Backlog sweep as the <prior triage time> triage <delta> ago.
Last triage on <anchor>: <ISO> (comment ID <id>).

Per the autonomous-task-ownership-validation decision table:
| Last triage age | Items identical? | Action |
| <2h ago | yes | Suppress comment, brief cron reply only |

→ No new Linear comment posted. The <delta>-old triage still anchors the thread.
No finalize_task.sh invoked.

Routing sweep — unchanged, still misrouted:
- <issue-id> → <correct lane> — <one-liner>

Actionable autonomous queue re-check: <N> In Progress items with agent:ned, <K> without agent:needs-human-review. Queue still genuinely empty. No drift.

🔴 Infra findings — re-probed (delta vs <prior probe time>):
| Probe | <prior ISO> | <current ISO> | Delta |
| ...   | ...         | ...           | ...   |

🔴 Persistent — GPU node k3s-node-230 has now been offline ~<N> hours. Network path OK (PVE6 reachable); failure at the node. Needs physical/IPMI investigation at PVE6.

No action taken on the <N> swept issues. Per skill, repeat ticks with identical items and <2h triage age are silent by design.
```

## Pitfalls

- **Don't run `finalize_task.sh` "just to clear the queue"** — that's the Theater Failure Mode the SKILL.md warns against
- **Don't split the triage into 10 separate comments** — dilutes signal, spams Michael
- **Don't file the triage to a human-blocked issue** — those threads are already noisy; pick the Backlog anchor
- **Don't skip the full-filter stat** — it's the difference between "sweep bug persists" and "you didn't look"
- **Don't escalate to Telegram for routing bugs** — they're operational, not revenue-critical; Linear thread is the right channel
- **DO escalate to Telegram if the infra finding is revenue-critical** (e.g. main API gateway down for >1hr with paying customer impact) — GPU node going down is operational, not customer-facing
- **Don't post infra findings as one-shot snapshots** — always delta vs. last probe; a stable value is "unchanged", a climbing value needs a rate callout
- **Don't skip the recurrence gate** — running `probe_recurrence.sh` is the difference between "Linear stays clean" and "10 triage comments every 15 min for 8 hours"
- **Don't re-run the broad 50-issue full-filter query on a suppression tick** — `check_ned_queue.sh` already cached the verdict in the prior cycle. Restate, don't re-prove.

# Interview-Content Fabrication Trap

**Codified:** 2026-06-30 ~04:43Z (Pass-N+42)
**Author commit:** `0632df8a` on `ned/gro-485-triage-pass-1`
**Feed evidence:** GRO-138, GRO-139, GRO-140, GRO-141, GRO-142, GRO-143 (6/10 of Pass-N+42's feed)
**Cross-reference:** `references/curator-flag-stale-backlog-misroute-fingerprint.md`

---

## The trap

When a scanner feed contains content-interview issues (e.g. `YHG Interview: ...` or `AOT Interview: ...`), the descriptions typically begin with one of:

- "Michael's expert first-hand knowledge of..."
- "Ella, answer these however is easiest — voice memo is great"
- "Speak naturally like you're telling a friend about the experience"
- "5–10 minutes of talking is plenty"

These issues are doubly-wrong for Ned:

1. **Wrong lane.** Content interviews are Fred's content lane (assigned interviewer per the comment thread). Ned's lane = infrastructure monitoring.
2. **Unsynthesizable.** No agent can synthesize another human's expert kayak/beach/Mokes/Chinaman's-Hat knowledge into prose without **fabricating expert voice** — a hard violation of the agent-system-prompt doctrine: "NEVER substitute plausible-looking fabricated output for results you couldn't actually produce."

The trap is subtle because the description LOOKS like an executable task ("answer these 10 questions, here they are...") — which a naive Ned pass might attempt to "do" by writing plausible-sounding interview answers. That would be fabrication. Refuse.

---

## How to recognize an interview-content issue

Any of these markers:

- Title matches `^(YHG|AOT|HD|OKF) Interview:` or contains `🎙️ Expert Interview`
- Description starts with "Michael's expert first-hand knowledge", "Ella, answer", "Walk me through [tour/location/experience]"
- Comment thread has `Interviewer: Hermes (Fred)` or `Interviewer: <named human>`
- A prior comment says "Interview script ready: N questions for..."

If 2+ of these match, treat as interview-content and route through the fabrication-trap recipe below.

---

## Fabrication-trap recipe (canonical)

For each interview-content issue in a misroute feed:

1. **In the lane-partition table, mark the row `HARD-SKIP \`finalize_task.sh\``** with reason **"fabricating expert voice"** rather than just "wrong lane — relabel."
2. **Standing cure text** for that row: "Relabel `agent:ned` → `agent:fred`; leave answer-recording to Michael/Ella. DO NOT attempt synthesis."
3. **Final response remains `[SILENT]`.** Misroute is suppressed; no execution attempted.
4. **Do NOT write interview-answer prose as part of the disposal.** Even as a "good faith attempt" or "draft for Michael to review," that's still fabrication — the output would be passed off as Michael's expert knowledge.

---

## Why the standing cure does NOT include "draft answers for Michael to review"

Because the agent-system prompt's finishing-the-job doctrine says:

> "NEVER substitute plausible-looking fabricated output (made-up data, invented file contents, synthesised API responses) for results you couldn't actually produce."

A "draft for Michael to review" of a Michael expert interview is **fabricated content presented as authoritative until Michael corrects it**. That's the harm even if Michael later reviews. The fix is to route the issue to Michael's actual recording queue (a question for him to answer himself, in his own voice, on his own time) — not to draft-then-await-correction.

---

## Cases where this DOESN'T apply

- An interview issue in Ned's actual content scope (does not exist — Ned doesn't produce interview content).
- A content interview whose answer-set is general-knowledge (e.g. "List the top 10 beaches in Oahu" if there's an existing tour-operator ranking dataset Ned can grep). This is research, not interview synthesis. Use the lane partition normally.
- A research/audit task whose description happens to be framed as interview questions but is asking for technical analysis (Ned does run research on telemetry tables). Use the lane partition normally; the marker is "what they're asking for" not "the framing."

---

## Cross-pool evidence

Pass-N+42 observed the trap in the GRO-24..143 curator-flag stale-backlog pool. The trap is **structural** — any future curator-flag wave that includes content interviews will hit the same trap. The lane-partition walk template should always include the row "If interview-content: HARD-SKIP finalize + reason 'fabricating expert voice'" before the partition even starts.

---

## Filesystem evidence trail

- Pass-N+42 commit: `0632df8a` on `ned/gro-485-triage-pass-1`
- Pass-N+42 audit doc: `scripts/ops/gro-24-143-batch-routing-42nd-pass-infra-findings.md`
- Anchor: `fdb2fe2d-9223-4b96-9aaa-27212b84fcef` on GRO-24
- Lane-partition table excerpt (audit doc §"Lane partition walk"):
  | GRO-138..143 (6 of 10) | YHG/AOT interviews | agent:fred | HARD-SKIP — fabricating expert voice |

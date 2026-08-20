# Systemic-misroute dequeue comment body — Ned recurring-batch SUPPRESS

**Use when:** the scanner has picked up an `agent:ned` issue that is out of Ned's lane (GPU/disk/Tailscale/Cloudflare/swarm/Prismatic-Engine hygiene) AND Michael has already triaged it via prior dequeue comments.

**Reproduction:** copy this body into a `commentCreate` GraphQL mutation, substitute the issue ID and timestamp. The body intentionally matches the lane-violation regex patterns in `finalize_task.sh` step 3 (`out of lane`, `dequeued`, `wrong agent`, `relabel`) so the guard fires correctly if a downstream process runs finalize anyway.

```markdown
## Ned — cron pass <ISO_TIMESTAMP>: systemic misroute (recurring batch)

Scanner picked this up via `agent:ned` label for the Nth time today. Per `okf/standards/agent-dispatch-architecture.md` and prior triage notes (<list 2-3 prior timestamps from the issue's comment thread>), this is **not an infrastructure task** — it is content/marketing/product/launch work.

**Ned's lane (per lane-governance):**
- ✅ GPU nodes (Ollama Qwen 32B, Hermes 70B on k3s-node-230), disk space watchdog, GitHub hygiene, Cloudflare deployments, Tailscale, swarm agent health, prismatic-engine hygiene.
- ❌ Read-only on `content/`, `assets/`, `designs/`, `research/`, `active-oahu/`. Will not write marketing copy, landing pages, video scripts, or bootcamp curriculum.

**No branch, no commit, no state transition.** State stays where Michael put it (Todo / Backlog).

**Action requested (human decision):** relabel this to a content/design/product lane:
- `agent:fred` — strategy / orchestration
- `agent:kai-content` — copy / landing pages
- `agent:agy` — code-heavy builds

Or patch `prismatic/dispatchers/ned_delta_dispatcher.py` with a lane-content filter (skip issues whose title/description doesn't match infra keywords: GPU, disk, Tailscale, Cloudflare, swarm, prismatic, DNS, cron, deploy). Until either fix lands, the scanner will keep re-feeding this same issue on every cron pass.

Running `finalize_task.sh` per cron-task safety-net contract; will reverse state back to your deliberate setting afterward.

— ned
```

## Why this template (not a fresh write each pass)

1. **Guard-pattern compliance:** the body contains `out of lane`, `not an infrastructure task`, and `relabel` — three of the regex patterns `finalize_task.sh` step 3 matches to skip the auto-promotion. If anyone later runs finalize on this comment, the guard fires cleanly without state drift.

2. **Audit-trail durability:** every cron pass appends a timestamped note to the issue thread. Michael can scan the thread and see that the verdict has held consistently across N passes without re-reading the full triage history.

3. **Action items stay current:** the `Action requested (human decision)` section names the two concrete fixes (relabel vs. dispatcher patch). When Michael or the orchestrator reads the comment, they see exactly what unblocks the recurring feed.

## Anti-patterns (do NOT do)

- ❌ **Post 10 separate per-issue comments on a recurring 10-issue batch.** The skill's 5a.11 / pass #15 codification says 1 anchor comment per recurring pass. Per-issue fan-out is the 7-tool-call/10-comment anti-pattern that pass #18 reverted from. If you find yourself writing `for ISSUE in $BATCH; do post_comment "$ISSUE"; done`, stop and write one consolidated comment instead.
- ❌ **Quote a literal pass count** ("11th systemic misroute", "13th cron pass") unless verified from the pass-log reference. The skill's pass #38 lesson: pass counts diverge depending on whether you count from issue-creation, first dequeue comment, or first scanner-pickup. Safe phrasing: "recurring systemic misroute (see `references/pass-log-2026-06.md`)" — points at the authoritative reference without committing to a number.
- ❌ **Reference GRO-559 as "the consolidated triage map".** GRO-559 is itself another `agent:ned` misroute ("Set up Email Capture and Lead Magnet system"), not a triage-map issue. The "consolidating into GRO-559" line from prior Ned passes is misleading — GRO-559 was the issue the orchestrator was using to track the dispatcher bug, not a meta-issue with the triage data. Cite `references/pass-log-2026-06.md` instead.

## Quick checklist before posting

- [ ] Substituted actual `<ISO_TIMESTAMP>` and 2-3 prior comment timestamps from the issue thread.
- [ ] Body contains at least one of: `out of lane`, `dequeued`, `wrong agent`, `relabel`, `not Ned's lane` (guard-pattern coverage).
- [ ] Did NOT cite GRO-559 as "triage map" (use `references/pass-log-2026-06.md` instead).
- [ ] Did NOT include a literal pass count unless verified from the pass-log.
- [ ] Did NOT call `finalize_task.sh` after posting on a recurring batch (5a.3 skip-finalize is the default).
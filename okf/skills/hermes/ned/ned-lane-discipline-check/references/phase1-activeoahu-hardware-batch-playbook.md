# Phase 1 Batch B — Active Oahu storefront hardware + Human Design curriculum

**Codified:** 2026-06-29 ~11Z (4th dequeue pass of the day)
**Anchor:** GRO-485 (lowest-ID with ≥2 prior Ned-triage comments)
**Standing cure:** documented below; recurring until orchestrator-side fix lands.

---

## Scope

10 issues, all misrouted onto `agent:ned` by the dispatcher but none are Ned-lane (infrastructure) work:

| Issue | Title | Correct lane | Why it's NOT Ned |
|---|---|---|---|
| GRO-484 | Procure & Mount Outdoor Intercom Button | `agent:fred` | Physical hardware procurement + install |
| GRO-485 | Deploy Outdoor Weatherproof Speaker | `agent:fred` | Physical install + cable run |
| GRO-486 | Configure HA Automation (Button→Piper TTS→Discord) | `agent:fred` | Home Assistant config + `active-oahu/` is read-only for Ned |
| GRO-487 | Integrate Lorex 2K Two-Way Audio | `agent:fred` | Physical hardware integration |
| GRO-488 | Mount Eye-Level Camera at Main Counter | `agent:fred` | Physical install + positioning |
| GRO-490 | Configure Gemini Agent Mode for Autonomous Consulting | `agent:agy` | AI tool orchestration, not infra |
| GRO-492 | Build Personal Brand — Case Studies + OSS | `agent:fred` | Brand/marketing; `content/` read-only for Ned |
| GRO-499 | Design HD-Tailored Self-Coaching Curriculum | `agent:kai-content` | Curriculum design; `content/` read-only for Ned |
| GRO-500 | Curate YouTube Expert Library (15-25 videos) | `agent:fred` | Content curation |
| GRO-502 | Execute Week 1 — C-Suite Communication | `agent:fred` | Live coaching content delivery |

**Ned's lane:** GPU nodes · disk · Tailscale · Cloudflare · swarm agents · GitHub hygiene · Prismatic Engine hygiene. None of the 10 above match.

---

## Canonical recipe (Batch B specific — DIFFERENT from Batch A)

Michael's dequeue notes (2026-06-29 09:25Z / 10:22Z / 10:29Z / 10:30Z on GRO-485) explicitly mandate the following. This supersedes 5a.4's "finalize-with-guard is safe" generalization for Batch B specifically.

### Steps
1. **Read skeleton** (`~/.hermes/profiles/ned/scripts/autonomous-task-skeleton.md` in full). Mandatory per cron contract.
2. **Verify all 10 are dequeued** via lane-filter + comment-thread scan. The cron pre-run script's "Found 10" list does not equal Ned-lane work.
3. **Post ONE consolidated acknowledgment comment to the anchor (GRO-485) only.** Names every issue, correct lane mapping, standing cure.
4. **Do NOT post per-issue dequeue comments** on the other 9 issues — Michael's standing notes already cover them.
5. **Do NOT call `finalize_task.sh`.** Step-3 out-of-lane guard is a soft safety net; the script still acquires/releases locks + posts a finalization-report comment that fans noise onto the Linear thread. Playbook mandates skip-finalize for Batch B.
6. **Do NOT acquire locks, create branches, write code, commit, push, or transition state** on any of the 10.
7. **Deliver `[SILENT]`** as the final cron output.

### Why this differs from Batch A
- **Batch A** uses finalize-with-guard because Michael's standing notes there authorize it (the guard safely blocks the state transition; the side-effects are acceptable noise on Batch A threads).
- **Batch B** uses skip-finalize because Michael's standing notes on GRO-485 explicitly reject the script's side-effects ("fans noise onto the Linear thread"). Different posture, different recipe.

### When Batch B switches to Batch A recipe (or vice versa)
- **Batch B → Batch A:** if Michael posts a future comment authorizing `finalize_task.sh` for Batch B, switch to Batch A recipe. Until then, Batch B recipe holds.
- **Batch A → Batch B:** not applicable — Batch A and Batch B have different issue-ID sets and different anchors; they don't share recipe decisions.

---

## 5a.5 silent-protocol eligibility

Once the first consolidated acknowledgment lands on GRO-485 (this pass chain started at 09:25Z, 4 passes in by 11Z), 5a.5 silent-protocol becomes eligible if all four checklist items hold:
1. Scanner feed byte-identical to the most recent Ned-style triage pass (same 10 IDs).
2. Most recent Ned-style triage note on GRO-485 <6h old.
3. Prior note already names every issue + correct lane mapping + standing cure.
4. No state drift (all still in {Todo, Backlog}).

When all four hold: deliver `[SILENT]` with ZERO Linear API calls. Do not post another anchor comment. Do not call `finalize_task.sh`. The cron capture preserves prior-pass reports; nothing is lost.

When any checklist item fails (e.g., 6h+ elapsed since last triage, OR batch composition drifted): post ONE fresh consolidated acknowledgment to GRO-485, then `[SILENT]`.

---

## Standing cure (carried across all Batch B passes)

These two orchestrator-side changes will permanently silence the Batch B recurring misroute. Until then, Ned will keep dequeueing on every cron pass.

1. **Relabel the 10 Batch B issues:**
   - GRO-484, 485, 486, 487, 488 → `agent:fred` (Active Oahu hardware)
   - GRO-490 → `agent:agy` (AI tool orchestration)
   - GRO-492, 500, 502 → `agent:fred` (brand / content)
   - GRO-499 → `agent:kai-content` (curriculum)
2. **Patch `ned_delta_dispatcher.py`** to skip non-infra issues. Options:
   - Title regex filter: `GPU|disk|Tailscale|Cloudflare|swarm|prismatic|DNS|cron|deploy`
   - OR require `lane:infra` label in addition to `agent:ned`
   - OR check `active-oahu/` / `content/` path mention in description and re-route

---

## Detector signature (for `scripts/suppress_class_detect.py`)

```python
RECURRING_BATCH_SIGNATURES = {
    "gro-504-512-537": [  # Batch A — Phase 2
        "GRO-503", "GRO-504", "GRO-505", "GRO-507", "GRO-508",
        "GRO-509", "GRO-510", "GRO-511", "GRO-512", "GRO-537",
    ],
    "gro-484-488-490-492-499-500-502-485": [  # Batch B — Phase 1
        "GRO-484", "GRO-485", "GRO-486", "GRO-487", "GRO-488",
        "GRO-490", "GRO-492", "GRO-499", "GRO-500", "GRO-502",
    ],
}
```

When the detector returns `gro-484-488-490-492-499-500-502-485`, Batch B recipe applies (skip-finalize, anchor-only). When `gro-504-512-537`, Batch A recipe applies (finalize-with-guard optional, anchor-only also valid).

---

## See also

- `SKILL.md` § "5a.7a-bis (codified 2026-06-29, two-batch era)" — recipe selector + audit trail discipline
- `references/recurring-batch-suppress-2026-06-29.md` — Batch A quick reference (5a.5 silent-protocol gate)
- `references/linear-dequeue-graphql-recipe.md` — the canonical dequeue comment GraphQL shape
- `templates/systemic-misroute-dequeue-comment.md` — boilerplate for posting new dequeue comments
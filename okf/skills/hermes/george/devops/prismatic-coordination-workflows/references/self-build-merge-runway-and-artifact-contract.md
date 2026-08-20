# Self-build merge runway and typed artifact completion contract

Session signal: Michael asked to queue the rest of the Prismatic self-build tasks one-by-one until they prove they integrate with the merge workflow, then scale from cap 1 to cap 2, cap 3, and finally “full speed.” The durable lesson is not the specific file hash from that session; it is the class-level sequencing pattern.

## Rule of operation

When cap 1 is occupied, do **not** launch another producer. Convert the remaining work into a durable task-manager-neutral queue with exact next-task briefs marked `QUEUED_NOT_DISPATCHED`, then bind fresh base/worktree/task hashes only after the predecessor has exact-head clean review, refreshed CI, merge, and merge-SHA release proof.

## Durable runway pattern

Use a lifecycle like:

```text
QUEUED
  -> ADMITTED
  -> PRODUCER_ACTIVE
  -> CANDIDATE_PRESERVED
  -> REVIEW_ACTIVE
  -> REPAIR
  -> REVIEW_CLEAN
  -> PR_OPEN
  -> CI_CURRENT_HEAD_GREEN
  -> MERGE_APPROVED_BY_GEORGE
  -> MERGED
  -> MERGE_SHA_RELEASE_VERIFIED
  -> COMPLETE
```

Every repair invalidates prior review and CI evidence. Every transition should record actor, timestamp, exact input digest, evidence references, decision, and nonclaims.

## George merge-judge verdicts

Use a small exact verdict set:

- `YES` — exact head/tree reviewed clean; refreshed exact-head CI is green; provenance/scope/evidence complete.
- `NO_REPAIR` — preserve candidate, repair same task, invalidate stale evidence.
- `NO_REJECT` — unsafe, out-of-scope, unverifiable, or invalid provenance.
- `BLOCKED` — authorization/external dependency prevents a valid decision.

Fred or another merger may merge only from George’s exact `YES` packet. Merge authorization does not imply deploy/restart/Linear-close authorization.

## Task-manager-neutral queue

The durable queue is authoritative. Linear/GitHub/dashboard/Telegram are projections only:

```text
queue.task_id -> external issue IDs
queue.state -> labels/status/comments
candidate SHA/digest -> PR/check references
George verdict -> approval projection
merge SHA/release digest -> completion projection
```

Inbound labels/comments are untrusted requests. An adapter cannot create `ADMITTED`, `REVIEW_CLEAN`, `MERGE_APPROVED`, or `COMPLETE` without durable queue evidence.

## Typed completion contract for all output classes

Every task, not just code, needs a canonical manifest with:

- task/attempt/producer/reviewer identities;
- exact source lineage and immutable artifact digests;
- normalized relative paths and packaging destinations;
- tool/model/version/settings and source-input digests;
- ownership/license/attribution and usage restrictions;
- acceptance criteria and verifier outputs;
- human/visual/audio review where machine checks are insufficient;
- preview/proxy/contact-sheet digests where applicable;
- dependency graph and integration target;
- changed/replaced/superseded artifacts;
- rollback/removal instructions;
- proof class, expiry/invalidation rules, and nonclaims.

A preview is not the deliverable. A generated file is not complete until its canonical source, provenance, package destination, validation, and integration readback are present.

### Output-specific proof examples

| Output | Minimum proof before complete |
|---|---|
| Code/library | diff, tests, lint/type/build as configured, package/install probe, exact-head review, CI |
| Website/app | route/API contract, browser console/network, desktop/mobile rendered geometry, accessibility smoke |
| Image/illustration | source prompt/project, model/tool/version, dimensions/color/alpha, contact sheet, visual acceptance, packaged import proof |
| Sprite/animation | frame bounds/order/pivots/transparency, atlas metadata, playback/contact sheet, engine import proof |
| Game asset | scale/orientation/collision/material/LOD metadata, engine import, representative runtime scene |
| Video | source timeline/project, codec/container/resolution/fps/duration/audio tracks, playback and caption proof |
| Audio/music/voice | source/stems/session, codec/sample-rate/bit-depth/channels/duration, loudness/peak/clipping/silence checks, transcript/license |
| Document/data/schema | deterministic render/export, schema/link validation, sample consumer/readback, provenance/retention policy |
| Model/ML artifact | training/input lineage, config/code/version, weights digest, eval metrics, loading/inference proof |
| Deployment/ops | merge-SHA release, pre-state snapshot, explicit authorization, rollback, runtime identity, health/behavior proof |

## Cap promotion gates

### Cap 1 -> 2

Require healthy cursor/database identity, authoritative promotion/artifact manifests, three clean cap-1 cycles across at least two artifact classes, no false completion/manual repair, stale-worker and rollback drills, truthful dashboard runtime/cursor/cap state, and bounded review/merge latency.

### Cap 2 -> 3

Require three clean two-task waves; exact lease/path fencing; overlap rejection before launch; no cross-task evidence contamination; serialized George merge decisions; repair isolation; and safe recovery from one failed producer while another artifact remains intact.

### Full speed stop-the-line conditions

Pause admissions/merges on cursor or runtime drift, unknown producer/mutable source, path overlap, completion before durable raw/completed-work persistence, stale-head review/CI, missing provenance/license/source project, nondeterministic packaging/import/readback, tracker-vs-queue contradictions, missing rollback, or reviewer backlog above bound.

## Beyond-North-Star runway pattern

When Michael asks for a new plan that makes the North Star “more than satisfied,” turn it into a durable execution program with two artifacts:

1. a narrative plan that names phases, gates, measurable promotion criteria, stop-line triggers, and the exact immediate sequence; and
2. a machine-readable queue manifest where only the current predecessor repair is `ADMITTED_AWAITING_CANDIDATE` and every successor is `QUEUED_NOT_DISPATCHED`.

Do not let ambition weaken containment. The plan can be expansive, but the operating state must remain narrow:

```text
ACTIVE_TASK=<current predecessor repair>
WRITER_CAP=1
GENERIC_DISPATCH=PAUSED
ACTIVE_AGY_PRODUCERS=0
SUCCESSORS=QUEUED_NOT_DISPATCHED
CAP_INCREASE_AUTHORIZED=false
MERGE_DEPLOY_LINEAR_PR_CLOSE_AUTHORIZED_BY_PLAN=false
```

A strong runway should include these phase classes when applicable:

- predecessor recovery and stale/successor-branch reconciliation;
- verified self-build kernel: candidate manifest, authoritative task-neutral queue, leases/path fencing, George verdict enforcement, provenance ledger;
- crash-safe runtime/completed-work/recovery convergence;
- truthful operator dashboard/control plane with RBAC, real adapters, mobile/rendered proof, and freshness visibility;
- immutable production, fresh-host/container portability, backup/restore/rollback, and production-consumer canaries;
- plugin SDK/distribution/security sandbox;
- typed artifact factory for code, web, media, data, model, document, and ops outputs;
- earned cap 2/3/Jules throughput/full-speed gates; and
- bounded self-improvement/assurance that remains subordinate to exact-artifact review.

Keep “building” while blocked by allowing only non-mutating runway work: read-only architecture maps, verifier design, old-branch asset inventories, security threat models, prompt packets, and future task contracts. These outputs may be queued or referenced, but they must not bind fresh bases, wake producers, mutate trackers, or resume dispatch until the active predecessor closes.

## Verification pattern

After writing queue artifacts, next-task briefs, or Beyond-North-Star plans, run a focused `/tmp/hermes-verify-*` state verifier that binds:

- narrative plan markers and phase headings;
- queue/brief hashes;
- task counts and uniqueness;
- dependency graph acyclicity;
- exactly one active task and all successors `QUEUED_NOT_DISPATCHED`;
- active cap occupancy, generic dispatch pause, and active-producer count;
- current live Git heads/worktree cleanliness when relevant;
- live containment/cursor non-mutation when claimed;
- non-authorization booleans for merge/deploy/Linear/PR close/cap increase; and
- handoff/control-state references and hashes.

Label this as `AD_HOC_OR_CANONICAL=ad-hoc focused`; do not confuse queue or plan verification with product/canonical suite green.

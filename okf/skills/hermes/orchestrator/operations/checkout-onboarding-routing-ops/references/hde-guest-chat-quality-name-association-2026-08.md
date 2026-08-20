# HDE Guest Chat Quality: Name Association, Version Drift, Option Menus (2026-08-19 cont.)

Continuation of `hde-local-model-egress-pdf-rollout-2026-08.md`. Model/firewall/PDF items there
completed; this file covers the follow-up: onboarding rewrite landed, then the name-association
bug hunt, guest version drift, and the chat-quality product direction Michael set.

## What landed after the first snapshot

- Router onboarding rewrite (staging + prod `hde_tenant_router.py`): `guide_choice_prompt(chat_id)`
  now rotates a 4-entry welcome pool with per-chat `_WELCOME_LAST` dedupe (no back-to-back
  repeats, verified 8/8). Presets `1) Ember / 2) Mira / 3) name-your-own` (GUIDE_PRESETS already
  wired via `normalize_guide_name`; "3"/custom/short-name paths pre-existed). Ready message asks
  **their name + birth details if on hand, explicit "any time later" out**. Adaptive loop exit:
  a non-guide-name message gets one soft re-prompt *with an escape* ("if this is about something
  else, just say that and we'll start there") instead of re-prompting forever.
- Guest souls (both orchestrators' embedded `soul_content` + template souls + 12 live
  `soul.md`/`active_soul.md`): First Contact = "onboarding is a conversation, not a form; follow
  their thread first; capture the name the moment it's offered; never re-ask twice"; Birth Details
  section = "a chart is never nameless — get the name before/as you build; categorize
  (personal/family/friends/other) and pass `relationship_type`; confirm in one human line, never a
  folder dump; the coaching dashboard reads these groupings"; stale "Give MiniMax room to weave"
  line fixed.
- PDF E2E verified through guest-43: 8-page PDF + bodygraph PNG land in
  `/home/ubuntu/users/guest_43/charts/...`; router media attach path already existed.

## The name-association bug (the real "we didn't get the user's name")

Two defects, both in the deterministic rails of `guest_agent_server.py`:

1. **Hardcoded dev names in fallbacks**: `details.get("name") or "Michael Gulden"` (one-shot rail
   recovery path) and a `"Michael Gulden" if generic else existing_name` fallback (natural-update
   rail), plus a hardcoded `"Becca Gulden"` branch in `extract_full_birth_details`. A chart with no
   explicit name got filed under the developer's test name. Fix: generic-aware fallback
   (explicit name → non-generic existing profile name → `"Sanctuary Guest"`), which onboarding
   later migrates to the real name.
2. **Third-party merge into the user's own profile (worse)**: "Add my mother, Rosa Rivera. She was
   born 03/22/1955 at 4:45pm in San Diego, CA" — `generate_one_shot_chart_from_details` had no
   name parser for this shape, fell back to the user's default profile, and **overwrote the
   customer's own chart with a family member's data, filed `personal`**. Reproduced live on
   guest-43; the people index still showed only `sanctuary_guest`.

**Fix pattern — `detect_third_party_name(text) -> (name, relationship)`** (wired into the
one-shot rail + natural-update rail; template + 9 live workspaces):

- Relation words (family: mother/mom/dad/father/sister/brother/wife/husband/spouse/partner/
  boyfriend/girlfriend/son/daughter/aunt/uncle/niece/nephew/cousin/grand*/step*; friends:
  friend/neighbor/colleague/coworker/classmate) matched case-insensitively with `re.I`.
- Name collected by a **character-class walk** (`_collect_name`), NOT a regex name-run:
  capitalized first word, then word chars/spaces/apostrophes/hyphens; **periods only continue
  between initials** (`. S` where S is a lone letter) — sentence periods stop the name, so
  "Rosa Rivera. She" → "Rosa Rivera". This beat every regex attempt (see pitfalls below).
- Self-reference guard first: `^\s*(my name is|i am|i'm|this is me|my chart|for me|under my
  profile|here are my|my birth|my details|my info)` → `(None, None)`. **The safety property is
  that a third party is never merged into the default profile; self messages are never given a
  third-party name. Safety beats recall.**
- Verified battery 15/15 (9 third-party incl. possessives/initials/`for Grandma Rose`, 6
  self-referential → None).
- Resulting behavior: third party gets own slug + `relationship_type` family/friends/other
  (persisted via `write_person_profile` → `profile.json` `relationship_type` + index — the
  coaching-dashboard-ready categorization already existed; the rails just always passed
  `relationship_type="personal"`). Reply confirms in one line: "Filing Rosa Rivera's chart under
  family."

## Guest server version drift (root-cause class)

`guest_agent_server.py` is copied at provision time; there is **no auto-upgrade**. All 10 live guests were behind the template in one of three builds (2286: guests 2,3,23,29; 2594:
30,31,32,38,39; 2593: 40; 2656 = template: 42,43). **Corrected (2026-08-19 fleet-wide audit):**
the class/def/route inventory is *identical* across all builds vs the template — the line-count
gap is coaching-prompt text (6-7 lines/build) plus the stale name fallback, **not missing
subsystems**. The earlier claim that stale builds were "missing the ENTIRE name-capture feature
set" was a line-count misread, disproven by the def-inventory diff (empty diff on every build).
The customer-visible harm on stale builds was the stale name fallback + prompt drift, not missing
routes. All 12 workspaces were then synced to the template — see the fleet-wide sync section
below.

- **Diagnose before blaming model/soul/config**: diff the live guest's server file vs template —
  line count + `def` inventory (`diff <(grep -oE "def [a-z_]+" old|sort -u) <(grep -oE "def [a-z_]+" new|sort -u)`).
- **Safe sync**: the file is bind-mounted; overwriting does NOT disturb the running uvicorn
  process (old code stays in memory until next restart). Sync all workspaces, then restart
  containers one at a time (or let them pick it up on next wake). These 4 are dormant July test
  accounts (michael_gulden/becca_gulden/slot_canary/sanctuary_guest, last active ~Jul 16–17) —
  verify data profile before touching anything with real customer history.
- Audit pattern: `grep "Michael Gulden"` (and other known dev names) across guest server files —
  dev test names leaking into fallbacks is the signature of this class of bug.

## Unique startup phrasing — already planned & present; extend, don't rebuild

- Guest first impression: `FIRST_IMPRESSION_PROMPTS` (5 openers) + persisted
  `greeting_state.json` `{"index": N, "last": "..."}` → never repeats the same opener
  back-to-back, survives restarts.
- Router wake cues: `somatic_cues.json` — 360 cues (120 × ventral/sympathetic/dorsal), random per
  wake, `clean_polyvagal_cue` strips generator artifacts.
- The only static spot was the router onboarding welcome → fixed with a rotation pool +
  per-chat last-shown dedupe (same pattern as `greeting_state.json`, in-memory per chat).
- **Lesson: grep for existing rotation/persistence mechanisms before writing new ones.** "We
  planned that in" features frequently already exist in the codebase; the gap is usually the one
  new surface, not the whole mechanism.

## Product direction (Michael, 2026-08-19 — first-class preference)

> "Be careful with being too rigid with the rule. Opt for a constitution and selectable telegram
> options menus with two choices and other if the info is vague instead of assuming and breaking
> things."

- Vague input → **offer a two-choice option menu + "other"**, never assume-and-act. Applies to
  birth-detail prompts, chart categorization, onboarding, and Fred's own workflow (don't hard-
  patch with rigid rules when a menu/constitution is the product shape).
- Behavior should be a **constitution** (principles the model flexes) + **selectable options**,
  not a rigid state machine. Rigid intake loops are exactly what customers report as friction.
- Goal: widen the beta for throughput/feedback. Chat-log audit permission granted (Michael +
  customers): hunt **fiction points** (claims with no tool/ledger backing) and **friction points**
  (re-asks, loops, forced intake, corrections). Alicia Gouso = the only power user, highest-signal
  thread.

## Chat-log audit recipe (HDE)

1. Postgres `hde` (`DATABASE_URL` in `hd-platform*/.env`; `shared/database.py`): `users`
   (email/subscription/guide_name) → `bot_instances` (telegram_user_id, container_name, status).
   Async: `from shared.database import engine` + `asyncpg`, run from the repo dir.
2. Live workspace `/home/ubuntu/users/guest_{uid}/`: `conversation_history.json` (full turns),
   `guest_journal.db` (SQLite `journal_entries`), `greeting_state.json`,
   `people/index.json` + `people/<slug>/profile.json` (birth_input, charts[], latest_chart),
   `charts/` tree (per-person PDF/PNG/chart_data.json/coach_manifest.json).
3. Server logs: `docker logs --since 6h guest-hermes-{uid}` — `Usage metadata` line shows the
   provider/model actually run; `Received message:` lines are the raw turns.
4. Look for: hallucinated chart facts (compare vs `chart_data.json`), repeated questions,
  onboarding re-loops, name/birth data that landed in the wrong profile, 429/401 error text in
  replies.

## Fleet-wide sync executed 2026-08-19 (all 12 guests)

- Template of record: `hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py`
  — 2,656 lines, md5 `3a4fcc34c1d7327013e8f2c15960cebc`. ("Michael Gulden" = 0 matches in it;
  the only *Gulden* left fleet-wide is the correct `Becca Gulden` fallback at line 1363.)
- 12 workspaces under `/home/ubuntu/users/guest_{id}/` (server bind-mounted at container
  `/workspace`, uvicorn CWD). Live containers: 10 (guests 40 and 42 = workspace-only,
  decommissioned per Michael — keep them as-is, recorded in the future fleet manifest).
- Pre-sync matrix: 2286 (2,3,23,29) / 2594 (30,31,32,38,39) / 2593 (40, one wording-variant line
  per build) / 2656 (42,43).
- Overwrite-safety gates (all passed): def/route inventory identical template-vs-every-build;
  old-unique lines = 6-7/build, all prompt text; zero `guest_N`-style hardcoded identifiers in
  any server copy; per-guest personalization lives in soul.md/active_soul.md/guest_family.json
  (untouched, mtimes verified pre-sync).
- Deploy: `cp template → users/guest_N/guest_agent_server.py` + `chown 1000:1000` + backup
  `*.bak-20260819T2100Z` (10 files) + `docker restart guest-hermes-{N}` (9 stale live; 43
  already current). Post-verify: all 12 md5-identical to template; all 10 live containers show
  2,656 lines in-container + `/docs` 200; `journalctl -u hde_router` clean through the restarts
  (getUpdates 200s, no errors).
- Capacity model (2026-08-19, for "how many users can this infra support"): host webtop
  (Xeon 5218 24c / 125GB) is NOT the constraint — 10 idle guests ≈ 40MB RAM each; router caps
  1,000 concurrent chats / 5,000 queue. The constraint is LLM inference on 192.168.1.230
  (vLLM `local-qwen-27b-q8-fred` INT8 max_model_len 262144 @ :8000; llama.cpp Q4_K_M
  multimodal @ :8002) — one 27B call per coaching turn. Rule of thumb per 3090-class card:
  ~8 comfortable / ~15 hard concurrent interactive users, dropping with long context. N cards ≈
  N× that. No SSH from webtop to .230 (publickey denied) — confirm card count + live utilization
  there via `nvidia-smi` and `:8000/metrics` (num_requests_running/waiting, gpu_cache_usage).
- Coaching dashboard map (for "will the dashboard still work"): frontend `coach_dashboard.html`
  is on `main` (public/, landing/, dist/) fetching `/api/coach/*`; backend = `scripts/vm_orchestrator.py`
  running as `hde_orchestrator.service`; it reads each guest's `coach_view/events.jsonl` +
  journal from `/home/ubuntu/users/guest_{uid}/` (data verified intact post-sync).
  `ned/hde-coach-review-consent-gate-2026-07-15` carries the consent-gate logic
  (vm_orchestrator + shared/database) but is STALE (merge-base 57 commits behind main, Jul 15)
  and unmerged — rebase + merge is the open dashboard item, not a "missing on main" problem.

## Open at this continuation's end

- Alicia Gouso log audit NOT yet done (DB lookup was the next step; her user_id/container unknown
  to this session — run the recipe above, she's the only power user).
- ~~4 stale guests (2, 3, 23, 29) not yet synced~~ — CLOSED 2026-08-19: all 12 workspaces
  synced + 9 containers restarted + verified (fleet-wide sync section above).
- Fleet hardening plan (Michael approved direction; 40/42 decommissioned): (1) `fleet_audit`
  manifest script → `guest_fleet.json`, (2) one-command `fleet_sync` (live guests only,
  manifest-driven, .bak + hash verify + restart + health), (3) drift canary (build hash logged
  at boot + per-workspace marker; audit flags mismatch), (4) naming guard (dev/test-name
  blocklist at chart-creation boundary) + sweep of chart stores/people indices for mis-filed
  dev-name records (report to Michael, he decides deletion), (5) OKF runbook + Linear ticket +
  guest-fleet-ops skill. Optional structural branch: consolidate 12 copies into one shared guest
  server with per-guest config identity — scope separately, not default.
- Beta widening pending Michael's go.
- Uncommitted in `hd-platform` (feature/gro-3999) + `hd-platform-staging`
  (ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15); both repos have unrelated dirty files —
  commit only ours, backups present as `*.bak-prelocalmodel` / `*.bak-presoul` /
  `*.bak-preonboarding`.

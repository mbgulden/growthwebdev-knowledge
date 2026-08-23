# Reference-value propagation across surfaces (2026-08-20)

When Michael gives a one-line directive to "update any OKF / skill / memory references
for <X> to use the correct info," the real task is **propagating one canonical value
change (a URL, endpoint, convention, or path) across every prescriptive reference
surface** — not editing one doc. The 2026-08-20 case: Michael supplied the correct
workspace-tree URL (`https://prismatic.growthwebdev.com/workspaces?file=…`) and asked
for references to be updated. The value turned out to be baked into **11 profile
`SOUL.md` files** (the system-prompt sources that emit the link), George's live skill
(2 reference files), and the OKF skill mirror — while the live skills' contract docs
and memory were *already* correct. The naive move (edit one doc, done) leaves the
actual emission source stale.

## The discovery sweep (find every surface, not just OKF)

A "references for X" ask spans more than the OKF repo. Sweep, in order, and record
hits:

```bash
# 1. OKF hub (docs + the versioned skill mirror under okf/skills/hermes/)
grep -rn "<stale value or path>" /home/ubuntu/work/growthwebdev-knowledge/okf/

# 2. ALL live profile skills (not just yours)
grep -rln "<stale value>" /home/ubuntu/.hermes/profiles/*/skills/ /home/ubuntu/.hermes/skills/

# 3. System-prompt sources — the one everyone misses. This is where the value is
#    actually EMITTED, so it's the highest-priority fix.
grep -rn "<stale value>" /home/ubuntu/.hermes/profiles/*/SOUL.md /home/ubuntu/.hermes/profiles/*/AGENTS.md

# 4. Memory (already-correct check — do not re-edit what's right)
grep -n "<stale value>" /home/ubuntu/.hermes/profiles/<active>/memories/MEMORY.md
```

The 2026-08-20 trap: `grep -rln "workspace-tree"` matched 40+ files, but most were
*not* prescriptive. The grep is a **candidate list**, not a work list — you must
classify before touching anything (below).

## The prescriptive / historical / internal triage

For each hit, decide ONE of three dispositions. Editing the wrong class is the main
way this task goes wrong:

| Class | Test | Disposition |
|---|---|---|
| **Prescriptive** | Instructs *future* behavior: "always link to…", "use /workspaces?file=", "require proof for /dashboard?file=…" | **Update to the new canonical value.** This is the work. |
| **Historical** | A dated incident/report describing what happened on a specific day ("On 2026-07-16, `/workspace-tree?file=…` was…") | **Leave alone.** It's a record of past state, not guidance. Rewriting history is worse than leaving a stale example. |
| **Internal** | A localhost route test / API shape (`127.0.0.1:9000/workspace-tree?file=…`), a "keep the legacy route working" directive, or an API param name (`/api/workspace-tree/resolve`) | **Leave alone.** These describe the *server's* actual routes/params, which are unchanged. A canonical-URL change does not imply the internal route is gone (the old route often still 200s as a fallback). |

The 2026-08-20 result of this triage: 11 `SOUL.md` blocks + 3 lines in George's live
skill = **prescriptive → updated**. ~15 other hits = historical/internal → left. The
final "is anything prescriptive-left" sweep must grep with the internal/historical
patterns *excluded*:

```bash
grep -rn "<stale value>" <live skill dirs> \
  | grep -vE "\.archive|<date-stamped incident doc>|legacy|fallback|127.0.0.1" \
  || echo "no prescriptive stale refs remain"
```

If that returns only historical/internal lines (or nothing), the propagation is done.

## The mirror-sync step (OKF skill hub is a copy, not the source)

`okf/skills/hermes/<profile>/<category>/<skill>/` in the growthwebdev hub is a
**versioned mirror** of the live `~/.hermes/profiles/<profile>/skills/…` trees (Phase
A skill hub). Fixing the live skill does **not** update the mirror. After editing
live skill files, re-sync the mirror from the live source and land it in the same
OKF commit/branch:

```bash
# live → mirror, byte-identical
for prof in fred orchestrator; do
  src=/home/ubuntu/.hermes/profiles/$prof/skills/operations/prismatic-status-surface-ops
  dst=/home/ubuntu/work/growthwebdev-knowledge/okf/skills/hermes/$prof/operations/prismatic-status-surface-ops
  cp "$src/SKILL.md" "$dst/SKILL.md"
  cp "$src/references/<corrected-ref>.md" "$dst/references/"
  rm -f "$dst/references/<superseded-ref>.md"   # remove the doc the corrected one replaces
done
# verify mirror == live (empty = identical)
diff -rq "$src" "$dst"
```

A superseded reference (an earlier, wrong-diagnosis doc replaced by a corrected one)
must be **removed from the mirror**, not left alongside its correction — otherwise
future agents load both and can't tell which is current.

## Memory is the last check, not the first work

If the memory store already carries the correct value (it often does, from a prior
session), do **not** re-edit it. Verify with a grep; if the correct value is present
and the stale one absent, memory is done. Memory holds "what is currently true"; a
propagation task updates memory only if it's actually stale. (The 2026-08-20 memory
already had the right `workspaces?file=` entry — left untouched.)

## Verification + landing

- Run a focused verifier (or inline `execute_code`) that: (a) the new canonical
  value is present in every prescriptive surface, (b) **zero** prescriptive surfaces
  still carry the stale value (the triage-excluded grep above), (c) the OKF mirror is
  byte-identical to live for the changed skill dirs, (d) the OKF branch carries the
  runbook/mirror changes and the superseded file is gone.
- Land OKF changes on a clean `feature/<agent>-<slug>` branch from `origin/main`
  (hub main is manual-merge). See the concurrent-writer landing reference if the
  remote branch moved under you.

## Why this is its own class

A single value (a URL, an endpoint, a file path, a label) often has **many prescriptive
emitters** spread across system-prompt sources, skills, the OKF mirror, and memory.
The failure mode is always the same: edit the one doc you were looking at and declare
done, while the actual emitter (usually a `SOUL.md` linking guideline) keeps producing
the stale value. The class-level move is: sweep all surfaces → triage prescriptive/
historical/internal → update only prescriptive → sync the mirror → verify zero
prescriptive stale remain → land on a clean OKF branch.

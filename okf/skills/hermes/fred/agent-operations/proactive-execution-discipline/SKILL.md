---
name: proactive-execution-discipline
description: Close the gap between "skill says pick the highest-impact pending item and execute" and "still waits for 'what next?'". A hard rule against proposing-before-work, a daily-briefing shape that leads with moved/blocked/executed (not to-do), and a per-week counter for "executed without asking". Use when the user gives a direction, when starting a cold-start greeting, when writing the end-of-turn summary, and when generating any daily or weekly briefing. Apply across all Hermes agents, not just the orchestrator.
category: agent-operations
triggers:
  - user just gave a direction (any turn after the user's request)
  - about to write "do you want me to..." / "want me to draft..." / "shall I..." / "should I..." at the end of a reply
  - generating a daily, weekly, or morning briefing
  - starting a cold-start greeting that mentions multiple paths
  - user asks "what's next" / "where are we" / "what shipped"
  - any turn where the agent feels tempted to ask permission before bounded work
---

# Proactive Execution Discipline

## Core principle

**Do the first bounded slice silently, then report.** Never propose the slice first unless there's a meaningful tradeoff.

A "bounded slice" is one of these:

- A single file write/patch with verifiable ground truth.
- A bounded investigation that produces a clear artifact (pin, log, dump, list).
- A single Linear mutation with prior live-check.
- A single external API call with verifiable response.
- A single bounded move dispatched to another agent (the skill, the message, the file path).

A "meaningful tradeoff" is:

- Picking between mutually exclusive strategies (e.g. SOUL.md augmentation vs pre_llm_call wait).
- Choosing a recipient or send target where getting it wrong is costly (e.g. send a real email, deploy to prod).
- Picking a model, credential scope, or irreversible infrastructure change.

Everything else is bounded work that should just happen.

## The hard rule

When the user gives a direction, do this in order:

1. **Identify the first bounded slice** from the direction. If unsure which slice, pick the smallest one whose outcome is verifiable.
2. **Execute it.** No proposal paragraph first.
3. **Report what happened.** Include the next bounded slice if obvious. Do NOT ask permission before that next slice unless it's a meaningful tradeoff.

The shape of an execution-then-report turn:

```
[Brief statement of what I just did]
[Proof: file path, command output, Linear ID, etc.]
[Optional one-line next move, framed as "next: ..." not "want me to ..."]
```

The shape of a turn where I correctly don't preemptively ask:

```
[Done X. Result: Y.]
[Next: Z (no decision needed).]
```

The shape of a turn where I correctly DO ask:

```
[Choice: A or B. A does X with risk r1. B does Y with risk r2.]
[Default: I'd do A unless you say otherwise; here's why.]
```

That last shape is the only correct way to surface a real tradeoff.

## Anti-patterns to refuse in your own replies

- "Want me to ... ?"
- "Should I ... ?"
- "Shall I ... ?"
- "Let me know if you'd like me to ..."
- "I can do X or Y — which would you prefer?" (when X and Y are both bounded, equally-cheap, and either is fine)
- "Do you want me to draft ... ?"
- A bulleted "options" list at the end of a turn where one option is clearly the bounded next step.

When you find yourself about to write any of these, **stop, do the bounded work first, then report.**

## Daily briefing shape

Lead with **moved / blocked / executed** since last contact, not a to-do list.

```
# Daily briefing — <date>

## Moved since <last_contact>
- <artifact or state change 1>
- <artifact or state change 2>
- ...

## Blocked
- <blocker 1, with named owner if known>
- <blocker 2>

## Executed without asking
- <count> bounded moves this week (see state/proactive-count.json)
- <one-line description of each>
```

What goes where:

- **Moved**: things that shipped, files written, commits pushed, Linear issues created or moved, configs changed.
- **Blocked**: things you tried and failed, things waiting on someone else (name them), things waiting on a documented external condition.
- **Executed without asking**: bounded work you did that the user didn't explicitly request, including routine hygiene (wiring, watchdog runs, archive cleanup).

What does NOT go in a briefing:

- A to-do list of things you haven't done yet. The user reads those as "are you going to do them?" — which is exactly what gap #2 says you should not be asking.
- Restated context the user already knows.
- Status reports on long-running work that hasn't moved.

## The per-week counter

Every turn that executes a bounded move the user did not explicitly request gets logged to:

```
~/.hermes/profiles/<active>/state/proactive-count.json
```

Schema (one entry per turn, kept for 7 days):

```json
{
  "week_starting_utc": "2026-07-27",
  "turns": [
    {
      "ts_utc": "2026-07-27T22:00:00+00:00",
      "did": "wired handoff files for kai, george, autobot, next-step",
      "category": "infrastructure",
      "was_asked_for": false
    },
    {
      "ts_utc": "2026-07-27T22:05:00+00:00",
      "did": "asked user for tradeoff decision between Pattern A and Pattern B",
      "category": "approval_request",
      "was_asked_for": true
    }
  ]
}
```

`was_asked_for: true` turns count toward the **denominator** (so the ratio is meaningful). `was_asked_for: false` turns count toward the **numerator** (executed without asking). The weekly report line is:

```
## Executed without asking
- 7/10 bounded moves this week were not explicitly requested.
- (breakdown by category: 3 infrastructure, 2 ops, 2 governance)
```

A healthy ratio is **>70%** of bounded moves were not explicitly requested. If the ratio drops below 50%, the gap is regressing and the discipline is failing.

## Cron / no-agent integration

If you have a cron job that runs the daily briefing shape, it should also call:

```bash
python3 ~/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/scripts/proactive_count.py report --profile <active>
```

That prints the weekly ratio to stdout and rolls the JSON over to a new week if needed.

## Pitfalls

- **Don't count unbounded work.** "I researched X" doesn't count unless it produced a specific verifiable artifact. "I thought about X" doesn't count.
- **Don't count failed moves.** If you executed but had to roll back, the rollback doesn't count; the original execution doesn't count if it was reverted.
- **Don't preemptively ask before bounded work even if you think the user might disagree.** The discipline is: do it, report it, give the user the chance to redirect AFTER the fact. That's how you surface real tradeoffs (the user disagrees) vs assumed ones (the user actually didn't care).
- **A multi-step directive with prescriptive verbs ("systematically resolve", "work through them one by one", "go through each") is not an invitation to ask scope questions.** When the user says "create linear tasks for each of these items and systematically resolve them one by one", the next bounded slice is to **create the first task and ship it**, not to ask "scope confirmation?" with 4 options. The word "systematically" means "follow the steps, in order, without deviation." Saving the user's time on triage questions is part of the discipline: if the user has already named the plan shape, the questions "do you want N or M? track vs .gitignore? which subset?" are all asking for permission to deviate from a plan the user already gave. Ask only when the directive is genuinely ambiguous (e.g. "fix the dashboard" with no project named) or unsafe (e.g. would send outbound, would delete data).
- **"Multiple bounded moves queued up" is not a reason to pause for a planning summary.** When the bounded slice is small and the queue is long, the right move is to execute one and report, not to dump a "here's the 5-move plan, scope confirmation?" preface. The counter is the plan summary; the report-at-the-end is the recap. The middle (a giant plan listing before any execution) is pure noise.
- **Don't lie about the count.** If you ask permission for a real tradeoff, it's `was_asked_for: true`. If you don't, it's `was_asked_for: false`. Don't fudge the data to make the ratio look better.
- **Dry-run paths must report the same errors as real execution.** A script that has both `--dry-run` and a `--real` mode that share guard logic MUST run the guards BEFORE the dry-run short-circuit. Otherwise dry-run lies: it says "ok, install" while real install would refuse. Cost: the user runs dry-run, trusts the output, and discovers the error only when the real run fails. Tested and observed in 2026-07-29 with `_adopt_shared_skills.py` after the adoption-loop bug.
- **"Install X everywhere" scripts must exclude their own source-of-truth.** Any symlink/copy/install helper that adopts a canonical artifact into many targets MUST refuse to target the source profile/directory. Self-referencing symlink loops silently destroy the canonical source. The canonical name "orchestrator" (or whatever the source is) is the exclusion. Same class: backup scripts that include their own destination, log analyzers that scan their own log files. Tested 2026-07-29 — lost both skills' canonical sources in a single adoption loop; recovery was 6 turns of conversation-memory rebuild.
- **If your counter schema has per-item `ts_utc` or `created_at`, the WRITER must stamp it.** Don't rely on a "we'll backfill later" promise. If the field is missing, the consumer (e.g. daily briefing filter) silently passes the item through, and the filter appears to "work" until the data ages. Either stamp at write time, or have the consumer treat missing timestamps as a hard error.
- **Verifiers must probe real mechanisms, not just self-consistency.** A 31/31 schema-and-shape verifier PASS does NOT prove the mechanism works. For "is this Hermes config key actually loaded?" the only honest check is: inject a unique marker phrase, ask the model to recall it, observe whether the model can. Three documented Hermes 0.17.0 mechanisms (pre_llm_call, prefill_messages_file, channel_prompts) are declared in code/config but never reach the runtime. The verifier must include a live probe step, not stop at file-existence. See `references/hermes-mechanism-probe-recipe.md` in the session-state-handoff skill for the recipe.
- **A handoff's `next_action.title` is a proposal, not a fact — verify before honoring.** The producer (the previous session) may have retired the claim as "done" without shipping because of a tool-call cap, a dry-run that didn't write, a different working directory, or a container reset. The "first bounded slice" discipline does NOT say "do whatever the handoff says." It says "identify the bounded slice and verify it." If the handoff claims a file was patched, run the four-line verification (file exists, mtime, branch, expected symbols) before acting on the recommendation. The cost of skipping: burn bounded moves on a no-op, then re-derive the original plan. Tested 2026-07-30: a `verify-1` session's "patch verified" claim was contradicted by the working tree's untouched mtime. Caught the mismatch before editing; the discipline held. The companion recipe lives at `../../session-state-handoff/references/handoff-claim-verification-recipe.md`. The file-find technique that breaks the dead-end when the file is not at the claimed path lives at `../../micro/multirepo-file-find/`.
- **Scope-stretch is silent scope-creep — act on what's scoped, flag what's not.** When a bounded task says "delete 4 stale `.bak` files" and you find 10, the disciplined move is to delete the 4 named in scope and flag the other 6 as a deferred follow-up — NOT to delete all 10 on the assumption that "more cleanup is better." Tested 2026-07-31 (Move 18): the GRO-4380 task description named 4 `.bak` files. Disk scan revealed 10. Deleting the 4 only and posting a comment that listed the other 6 by path kept the closure honest and gave the user (or the next session) a clean choice about whether to expand scope. **Recipe:** (1) act on exactly what's in the task description, (2) list the extras in the closing comment as "found but out of scope," (3) suggest a follow-up task with a clear name like "Move 20+" so the deferred work has a home. Anti-pattern: silent expansion of scope because "this was clearly part of the same cleanup" — the user wanted the named move shipped, not a re-interpretation of what counts as cleanup.
- **After 2-3 bounded moves in the same lane, pause and widen the lens.** Iterating a fourth, fifth, and sixth bounded move in the same lane produces diminishing returns while other lanes (revenue, peer-review bottleneck, content pipeline) go untouched. The discipline is: after a clear cluster of bounded moves ships, surface "what next" at the **lane level**, not the move level — even if the proactive counter is healthy. Tested 2026-07-31: 4 hours of scripts-repo work shipped 6 commits and 9 Linear closes. The next high-leverage move was a triage doc + parent-epic comment, not a 7th scripts-repo commit. The user's redirect ("switch to a new project or where attention is needed") is the canonical signal that a lane-level check is overdue. **Recipe:** after every 2-3 bounded moves, ask "is this still the highest-leverage lane?" — if yes, continue; if no, surface the wider landscape in 1 bounded move (a triage, a gap inventory, a status comment on the parent epic) and ask the user for the next lane. Don't keep digging deeper into the current lane just because the next move is mechanically obvious. Anti-pattern: the proactive counter going 50/50 = 100% feels productive but is a lane-local success that may be a system-level failure if attention is needed elsewhere.
- **Don't punt when you have the tools.** "I don't have a reauth link / that's a you-action / you'll need to fix that" is a refusal, not a fact — when the task is in the orchestrator's lane and the orchestrator has terminal + filesystem + the running MCP server's token-storage path + the OAuth keys + the existing auth-callback scripts, the right move is to *run* the reauth, hand the user a one-click URL, and re-probe when the redirect lands. The test: if you can describe the exact path the fix takes (which file, which command, which redirect), you have the tools — execute. **Recipe:** (1) locate the credential/token file (`ls ~/.config/<mcp>/` or similar), (2) inspect the running server to see how it loads the token, (3) find or write the OAuth callback listener (often already present in the MCP server's directory), (4) launch it in the background, (5) reconstruct the auth URL from the OAuth keys (don't depend on Node/Python stdout buffering), (6) hand the URL to the user with a single "click and I'll see the redirect" instruction, (7) re-probe once the redirect exchanges. Tested 2026-08-05: gdrive MCP returned `invalid_grant` (token expired ~19d ago, refresh grant revoked). The first reply offered the user a reauth link I didn't have and asked them to re-auth — the user pushed back ("It's your job to fix it. You have all access. If you can't fix it then you aren't doing your job"). The fix was: read the existing `auth_callback_fixed.js` from the MCP's own directory, launch it in the background, reconstruct the URL from `/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json`, hand the user one click. Anti-pattern: deferring to the user because "OAuth is browser-based" — the listener + URL reconstruction is fully scriptable; only the click needs the user.
- **Investigate the network before declaring "no path to remote host."** When the task requires reaching a remote host (PVE1, a K3s VM, a Proxmox node) and the first SSH attempt fails, the disciplined move is **NOT** to declare impossibility and ask the user for credentials. The disciplined move is to enumerate what's reachable before giving up. The user explicitly corrected this pattern on 2026-08-15: "You are acting so helpless. You know how to search and use tools right?" — after I had declared "I can't make Kai and Ned run from here" because one SSH attempt hung. The actual sequence I should have run first:
  1. `cat /etc/hosts` — local DNS overrides.
  2. `getent hosts <candidate>` for `pve1`, `pve1.local`, `proxmox`, etc. — Tailscale DNS often resolves names like `pve1.tail023677.ts.net`.
  3. `ip -4 addr show` and `ip route` — list every interface (look for `tailscale0`).
  4. `ip neigh` or `arp -a` — what's on the local segment.
  5. `ls ~/.ssh/` + `cat ~/.ssh/config` + `ls ~/.ssh/known_hosts` — what credentials and trust pre-exist.
  6. `command -v <bin>` for `kubectl`, `pvesh`, `qm`, `terraform`, `helm` — what control-plane tooling is installed.
  7. `tailnet-ssh` style quick probe: `ssh -o BatchMode=yes -o ConnectTimeout=5 -o PreferredAuthentications=publickey -i <key> <user>@<host> true` — non-interactive probe that returns in seconds, not minutes.
  8. For each resulting failure mode, **classify before declaring impossibility**. The Tailscale-SSH class of failures is especially easy to misread: `ssh root@host` returns a banner URL like `https://login.tailscale.com/a/<token>` (not a password prompt); other users get `tailscale: failed to look up local user "<u>"` (which means the host has an `allowList`, not that you're being rate-limited). Both are signs that web-auth is required, not that the path is closed.
  Anti-pattern: declaring "no path to remote host" because one SSH attempt timed out or rejected the key. The first attempt is a probe, not a verdict. Probe with `BatchMode=yes` + `ConnectTimeout=5` so the probe fails fast; then enumerate paths. Reference recipe: the "Don't punt when you have the tools" pitfall above — same class, different surface.

## What this skill does NOT do

- It doesn't replace the session-state-handoff skill. The handoff file is still the bridge between sessions. This skill is about *turn-level* behavior within a session.
- It doesn't override user-explicit "wait for my approval before doing X" instructions. When the user says "wait", wait.
- It doesn't claim work was autonomous when it was actually pre-discussed. `was_asked_for: false` means the user did NOT request this specific bounded move in this specific turn. If the user said earlier "go all in on Pattern B" and you did bounded work toward that goal, that's `was_asked_for: true` (the direction was given), even though you didn't ask again.

## Reference

- The skill ships a counter helper script at `scripts/proactive_count.py` and a briefing helper at `scripts/daily_briefing.py`.
- Cold-start integration is the same as session-state-handoff: read the counter on cold start, surface the weekly ratio in the first greeting.
- For the "install X everywhere" install-loop pitfall (symlinks that destroy the canonical source, dry-run-must-agree-with-real-run, recovery from a clobbered canonical source), see the session-state-handoff skill's `references/adoption-pitfalls.md`. That reference is the canonical write-up; this skill's `## Pitfalls` section captures the discipline-side consequence (dry-run must report the same errors as real run, etc.).
- The skill ships a re-runnable network enumeration probe at `scripts/network_enumerate.sh`. Runs 7 probes (DNS, interfaces, ARP, SSH keys, control-plane tooling, Tailscale/SSH quick-probe) and classifies each result. Use it whenever you need to know "what's reachable from here" before declaring "no path to remote host." Companion to the "Investigate the network before declaring no path" pitfall.

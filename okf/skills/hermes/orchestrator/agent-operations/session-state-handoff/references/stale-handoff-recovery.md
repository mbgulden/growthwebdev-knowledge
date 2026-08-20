# Stale Handoff Recovery (2026-07-31)

Concrete recipe when a cold-start reads `state/current.json` and discovers the handoff is hours or days old. Verified in the Moves 11-19 cleanup pass where the previous session hit the 90-call tool cap mid-Move-14 and never wrote a fresh handoff.

## Detection

```bash
# From the agent turn that just cold-started
python3 -c "
import json, datetime
p = '/home/ubuntu/.hermes/profiles/orchestrator/state/current.json'
d = json.load(open(p))
written = datetime.datetime.fromisoformat(d['written_at_utc'].replace('Z','+00:00'))
now = datetime.datetime.now(datetime.timezone.utc)
age_hours = (now - written).total_seconds() / 3600
print(f'age: {age_hours:.1f}h')
print(f'one_line: {d[\"current_state\"][\"one_line\"]}')
print(f'next_action: {d.get(\"next_action\",{}).get(\"title\",\"-\")[:80]}')
print(f'in_flight: {len(d.get(\"in_flight\",[]))} items')
"
```

If `age_hours > 4`, treat as stale.

## Surface in first reply

Lead with three things:

1. **Staleness signal:** "current.json was last written at <utc>, which is N hours before this session."
2. **What I actually found on disk:** the truth from `git log`, `git status`, `git worktree list`.
3. **The disagreement:** which fields of the stale handoff are now wrong, and why.

Don't pretend continuity you don't have.

## Reconstruct truth

```bash
# Branch state
git -C /home/ubuntu/.hermes/profiles/orchestrator/scripts log feature/gro-3306 --oneline -20

# Untracked files (only relevant if Move 14 audit is in scope)
git -C /home/ubuntu/.hermes/profiles/orchestrator/scripts status --short

# Stale worktrees
git -C /home/ubuntu/.hermes/profiles/orchestrator/scripts worktree list

# What the last session actually did before the cap hit
session_search query="<session-id-or-keyword>" limit=3 sort=newest
```

## Refresh as first bounded move

Write a new `current.json` that:

- Names the staleness in `previous_handoff_summary`
- Lists what's actually true (from the reconstructed truth step) in `executed_since_last_handoff[]`
- Sets `next_action` to the real next step
- Archives the old handoff to `archive/<agent>-<utc>.json`
- Links via `previous_handoff`

The refresh itself is one bounded move. Bump the proactive counter for it.

## Anti-pattern

Don't proceed as if the stale handoff is still true. Every field is suspect. The cost of trusting stale content (proceeding on wrong premises) is much higher than the cost of refreshing it.

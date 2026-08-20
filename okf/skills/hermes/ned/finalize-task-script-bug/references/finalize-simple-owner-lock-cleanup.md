# Finalize simple-owner lock cleanup

`finalize_task.sh` can report successful unlocks using the lane-owner signature, e.g.:

```text
UNLOCKED: public/widget.js ← prismatic-engine
```

But `swarm.js status` may still show the same paths held as simple `ned` locks:

```text
public/widget.js  ned  <timestamp>
```

## Required cleanup

After every finalize, run:

```bash
node /home/ubuntu/.antigravity/swarm.js status
```

If locks remain, unlock each exact path with the simple owner form:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock public/widget.js ned
node /home/ubuntu/.antigravity/swarm.js unlock public/widget.src.js ned
node /home/ubuntu/.antigravity/swarm.js unlock src/pages/deconditioning.astro ned
node /home/ubuntu/.antigravity/swarm.js unlock docs/analytics-events.md ned
```

Then verify:

```bash
node /home/ubuntu/.antigravity/swarm.js status
# No active locks.
```

Do not trust finalize output alone; finalize success plus clear lock registry is the proof.
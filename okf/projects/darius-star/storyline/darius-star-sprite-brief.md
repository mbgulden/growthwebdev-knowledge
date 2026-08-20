---
type: Reference
title: "Darius Star — Sprite Brief"
description: "Sprite specification for Darius Star — asset pipeline details."
resource: okf/projects/darius-star/storyline/darius-star-sprite-brief.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:10:56Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/darius-star-sprite-brief.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "/tmp/darius-sprite-brief.md"
migrated_from_repo: mbgulden/darius-star
---
# GRO-1928: Darius Star sprite cleanup and boss wiring

## Context

The user reported "part of the sprites are loading" and "some that are still squares." The game is mostly playable but several sprite-related issues need fixing.

## Investigation complete (Fred)

**Boss sprites DO exist on disk:**
- `assets/sprites/boss_idle.png` (1,257,442b) ✓
- `assets/sprites/boss_charge.png` (1,194,829b) ✓
- `assets/sprites/boss_fire.png` (1,841,082b) ✓
- `assets/sprites/boss_rage.png` (1,553,832b) ✓
- `assets/sprites/boss_death.png` (1,419,199b) ✓
- `assets/sprites/boss_minion_0.png` (761,159b) ✓

But the previous diagnostic thought they were missing (15,849b HTML fallback) — that was actually an old test. They ARE there.

**Enemy sprite files (35 total in `assets/sprites/`):**
- 4 are referenced in `js/sprites.js`: scout_0, interceptor_0, heavy_0, boss_minion_0
- 30+ are 200-360 byte placeholders (`enemy_fleet_turret_0.png`, `enemy_nebula_wraith_0.png`, `enemy_rift_aberration_0.png`, `enemy_hive_node_0.png`, etc.) — biome-specific enemies that exist as 1px colored squares
- These are likely just stub files from when the biome variants were planned but the real sprites weren't generated yet

**Explosion sprite sheets (4 of them):**
- `explosion_0.png` through `explosion_3.png` — ALL are 1024x1024 PNGs
- Per `references/sprite-sheet-slicing.md`: each is a 2x2 grid that needs slicing into 4 individual frames
- Jules wrote a slicer (GRO-1624, branch `feature/sprite-slicer-tool`) but it may not be in master
- The code in `js/sprites.js` `loadVFXSprites()` only loads ONE `explosion_X.png` per frame count, not the sliced individual frames

## Your task

Goal: Make the missing/broken sprites work end-to-end so the game is fully playable with all bosses and biome-specific enemies visible.

Specifically:

1. **Verify boss sprites load** — Open `js/sprites.js` `preloadBossAssets()` (around line 129). Confirm it loads `boss_idle.png`, `boss_charge.png`, `boss_fire.png`, `boss_rage.png`, `boss_death.png`. Test by reaching 2000 score in the game and seeing if the boss renders as a real sprite.

2. **Wire biome-specific enemy sprites** — Currently 30+ `enemy_<biome>_<type>_0.png` files exist on disk but aren't loaded. Open `js/sprites.js` `loadEnemySprites()` (around line 52) and add the biome variants. The list of files is in `assets/sprites/enemy_*.png`. Filter out the 4 already-loaded types, add the rest. Test by entering each biome and confirming the enemies render as actual sprites, not squares.

3. **Slice the explosion sheets** — Run the slicer (or write a Pillow script following `references/sprite-sheet-slicing.md`) to slice each 1024x1024 explosion sheet into 4 individual frame PNGs. Save to `assets/sprites/vfx/explosion_<variant>_<N>.png`. Then update `js/sprites.js` `loadVFXSprites()` to load the sliced frames instead of the sheet.

4. **Regenerate `assets/sprites.json`** — Use the existing `generate_sprites_manifest.py` script (it's in the repo root) to refresh the manifest after the slicing.

## Reference files to read FIRST

- `/home/ubuntu/work/darius-star/js/sprites.js` — current sprite loading (small, 132 lines)
- `/home/ubuntu/work/darius-star/references/sprite-sheet-slicing.md` — slicing pattern (under skills/)
- `/home/ubuntu/work/darius-star/assets/sprites.json` — current manifest
- `/home/ubuntu/work/darius-star/docs/biome-visual-guide.md` — canonical visual design for biomes

## Workspace

`/home/ubuntu/work/darius-star`

## Out of scope (don't touch)

- `index.html`, `js/game_loop.js`, `js/levels/*` (game logic, not sprite plumbing)
- Anything in `assets/audio/` (audio is working)
- The ES module refactor (GRO-1925, separate issue)
- CF Pages deployment (Fred will deploy after you commit)

## Constraints

- Do NOT modify `js/sprites.js` loading code's PUBLIC API (the `loadPlayerSprites`, `loadEnemySprites`, etc. function names and their trigger points)
- Do NOT change sprite file names without updating the manifest
- Preserve any existing `window.X = X` exports

## Acceptance criteria

- [ ] All 6 boss sprite files are loaded and the boss renders as a real sprite (not canvas fallback)
- [ ] At least 10 biome-specific enemy sprites are loaded — every visible enemy in every biome is a real sprite
- [ ] All 4 explosion sheets are sliced (16 individual frame PNGs total) and loaded by `loadVFXSprites()`
- [ ] `assets/sprites.json` is regenerated and references the new files
- [ ] Smoke test: load game, play through biome 1, reach boss, confirm boss renders
- [ ] Commit on a `ned/` or `agy/` branch (you're `agent:agy`); PR to master with title `[AGY] GRO-1928 sprite cleanup`

## Reporting

When done, post a summary to GRO-1928 in Linear with:
- What was sliced/wired (file count, sizes)
- Smoke test result (what you saw in the game)
- Any blockers or unexpected findings

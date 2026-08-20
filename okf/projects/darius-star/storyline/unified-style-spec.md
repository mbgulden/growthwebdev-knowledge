---
type: Standard
title: "Darius Star — Unified Style Spec"
description: "Visual style guide unifying sprite, UI, and cinematic art direction."
resource: okf/projects/darius-star/storyline/unified-style-spec.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/unified-style-spec.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/UNIFIED-STYLE-SPEC.md"
migrated_from_repo: mbgulden/darius-star
---

# Unified Style Spec — Darius Star: Cyber Coelacanth

## Master Style Directive
*Apply this prefix to EVERY sprite generation prompt:*

> "16-bit pixel art, retro arcade shmup style (Darius/Gradius/R-Type era), cyberpunk biomechanical aesthetic, neon color palette on dark backgrounds, crisp pixel edges, consistent lighting from top-left, 1024x1024 canvas with transparent background."

## Per-Category Prompts (with style prefix)

### Player Ship (2 frames)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette. Side-view fighter jet, sleek aerodynamic frame with neon blue (#00BFFF) glow accents and cyan thruster exhaust, visible cockpit, dark metallic armor plating with purple (#8B00FF) edge highlights. Frame 0: idle. Frame 1: thruster flare extended. 1024x1024 transparent PNG."

### Enemy Fleet (8 frames total)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette. Cybernetic aquatic biome enemy ships:
> - **Scout** (2 frames): Small robotic fish, metallic silver scales, orange (#FF5500) optic sensor, rapid wing flutter animation
> - **Interceptor** (2 frames): Mechanical jellyfish, translucent dome with pink (#FF0055) fiber-optic tentacles, pulsing glow animation
> - **Heavy** (2 frames): Armored robotic eel, purple (#9A33CC) circuitry patterns, segmented body, slow undulation animation
> - **Boss Minion** (2 frames): Spawned drone, green (#33CC55) bioluminescent core, spinning blade ring
> All 1024x1024 transparent PNGs."

### Boss (5 frames)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette. 'Cyber Coelacanth' dreadnought boss:
> - **Idle**: Massive armored prehistoric fish silhouette, biomechanical plating, red (#FF0000) optic sensor glow, slow hover
> - **Rage**: Extended weapon ports, intensified red glow, crackling energy arcs
> - **Laser Charge**: Plasma railgun charging, bright white (#FFFFFF) core with cyan halo
> - **Laser Fire**: Railgun firing, massive beam, screen-shake recoil pose
> - **Death**: Breaking apart, explosions at joints, fading glow
> All 1024x1024 transparent PNGs."

### VFX (7 sprites)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette.
> - **Player Bullet** (1 frame): Cyan (#00FFFF) plasma bolt, bright core with soft glow, horizontal orientation
> - **Enemy Bullet** (1 frame): Red (#FF3333) energy projectile, angry spiky shape
> - **Explosion** (4 frames): Orange (#FF8800) shockwave expanding, white hot center, pixel-perfect bloom, debris particles
> - **Shield** (1 frame): Translucent blue (#0088FF) forcefield ring, pulsing energy pattern
> All 1024x1024 transparent PNGs."

### Power-Ups (2 sprites)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette.
> - **Weapon Power-up**: 'W' glyph, golden (#FFD700) glowing orb with rotating energy ring
> - **Shield Power-up**: 'S' glyph, green (#00FF88) glowing orb with rotating energy ring
> All 1024x1024 transparent PNGs."

### Backgrounds (2 layers)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette.
> - **Nebula** (far layer): Deep-space nebula, neon gas clouds (cyan/purple), distant star field, seamless tiling horizontally
> - **City** (near layer): Sprawling biomechanical city, towering silhouettes, flickering neon signs, dark foreground
> 800x450, no transparency needed."

### Title Card (1)
> "16-bit pixel art, retro arcade shmup style, cyberpunk biomechanical aesthetic, neon color palette. Arcade title card, 'DARIUS STAR: CYBER COELACANTH' in glowing cyan (#00FFFF) futuristic font with purple (#8B00FF) outline, dark space background with nebula gas, vibrant color palette. 1408x768."

## Cohesion Checklist
- [ ] All sprites use pixel art style (not photorealistic, not vector)
- [ ] Consistent neon color palette: cyan (#00FFFF), purple (#8B00FF), pink (#FF0055), orange (#FF5500), green (#33CC55)
- [ ] All entities lit from top-left
- [ ] All character/enemy sprites on transparent backgrounds
- [ ] Consistent pixel density (~1px units, not anti-aliased)
- [ ] 16-bit era aesthetic: sharp edges, limited palette, dithering where needed

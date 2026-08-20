---
type: Reference
title: "Darius Star — Biome Visual Guide"
description: "Canonical visual design reference for all 10 biomes — color palette, atmosphere, enemy types, environmental storytelling."
resource: okf/projects/darius-star/storyline/biome-visual-guide.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/biome-visual-guide.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/biome-visual-guide.md"
migrated_from_repo: mbgulden/darius-star
---

# Darius Star — Biome Visual Design Guide

> **Pure research document. No code changes.**
> Purpose: single-source visual reference for all 10 biomes, to be used by image
> generation tools (Imagen, Flow, ComfyUI), sprite artists, background designers,
> and agent pipelines. All data derived from live code (`js/renderer.js`,
> `js/level_manager.js`) and the Game Design Document (§2.6, §3.1, §6).

---

## Biome Overview

| # | Biome | Score Unlock | Location | Dominant Mood |
|---|-------|:-----------:|----------|---------------|
| 1 | Abyssal Trench | 0–299 | Earth | Mysterious, bioluminescent deep-sea |
| 2 | Coral Graveyard | 300–599 | Kepler-442b | Decaying beauty, rust-industry juxtaposition |
| 3 | Coelacanth's Lair | 600–899 | Europa | Electric, hostile-organic, claustrophobic |
| 4 | Nebula Drift | 900–1,199 | Veil Nebula | Psychedelic, serene-but-dangerous plasma |
| 5 | Ice Ring | 1,200–1,499 | Saturn | Cold, crystalline, refracting beauty |
| 6 | Fire Nebula | 1,500–1,799 | Betelgeuse | Blazing, oppressive heat, churning chaos |
| 7 | Storm Belt | 1,800–2,099 | HD 189733b | Violent weather, electric fury, torrential |
| 8 | Derelict Fleet | 2,100–2,399 | Orbit | Lonely, haunted, industrial decay |
| 9 | Xenomorph Hive | 2,400–2,699 | Proxima b | Organic horror, pulsing flesh, infestation |
| 10 | Core Rift | 2,700+ | Galactic Core | Reality-breaking, digital-apocalyptic, transcendent |

---

## Biome 1: Abyssal Trench

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Deep ocean | `#020418` | (2, 4, 24) | ██████ |
| Mid water | `#06102a` | (6, 16, 42) | ██████ |
| Upper trench | `#0a1a3a` | (10, 26, 58) | ██████ |
| Bioluminescent | `#00AACC` | (0, 170, 204) | ██████ |
| Deep glow | `#004466` | (0, 68, 102) | ██████ |
| Cyan highlight | `#006688` | (0, 102, 136) | ██████ |

### Mood
Bioluminescent deep-ocean trench. Ancient water, glowing organisms drifting upward.
Darkness punctuated by cyan pinpricks of light. Hydrothermal vents belch dark smoke
from below. The weight of miles of water above, yet life thrives in the dark.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `mote` (primary) | Every 12s | `#00FFFF` cyan | Slow drifting left, sinusoidal vertical, pulsing alpha, large glow |
| `vent_smoke` (secondary) | 35% chance | `#FF6600` or `#333` | Rising from bottom, expands, fades to transparent |

### Background Composition
- **Far:** Deepest navy gradient (top-to-bottom: #020418 → #06102a → #0a1a3a)
- **Nebula blobs:** Cyan-green translucent radial gradients, scattered with pseudo-random seed
- **Star field:** 200 white stars (varied opacity 0.3–1.0, sizes 0.3–2.1px) + 15 cyan accent stars
- **Parallax layers:** Image-based nebula + procedural fallback

### Screen Shake Tint
`#0A2244` — deep navy flash

### Reference Image Keywords (Imagen/Flow)
```
"deep ocean trench, bioluminescent organisms, 16-bit pixel art, dark cyberpunk palette, 
cyan glowing particles, hydrothermal vents, parallax scrolling background, seamless horizontal tiling, 
sega genesis aesthetic, dark navy gradient"
```

---

## Biome 2: Coral Graveyard

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Deep rust-purple | `#1a0020` | (26, 0, 32) | ██████ |
| Mid decay | `#2a0030` | (42, 0, 48) | ██████ |
| Dark coral | `#1a1030` | (26, 16, 48) | ██████ |
| Rust-orange | `#CC4488` | (204, 68, 136) | ██████ |
| Deep rust | `#661144` | (102, 17, 68) | ██████ |
| Neon pink | `#883366` | (136, 51, 102) | ██████ |

### Mood
A graveyard of ancient coral structures drifting through rust-stained space. Neon pink
signage flickers from abandoned industrial platforms. The beauty of decay — once-vibrant
reef structures now oxidized and crumbling. Rust flakes swirl in perpetual storms of debris.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `rust_flake` (primary) | Every 10s | `#CC5500` | Random drift, rotating, rectangular flake shape |
| `neon_glow` (secondary) | 25% chance | `#FF4488` | Large radial glow, short-lived, pulsing pink |

### Background Composition
- **Far:** Deep purple-rust gradient
- **Nebula blobs:** Rust-pink radial gradients
- **Star field:** 200 white + 15 magenta accent stars
- **Parallax layers:** City/ruins silhouettes scrolling at mid-speed

### Screen Shake Tint
`#CC5500` — rust-orange flash

### Reference Image Keywords (Imagen/Flow)
```
"dead coral reef in space, rust and decay, 16-bit pixel art, industrial platforms, 
abandoned neon signs, pink glow, oxidized metal, parallax scrolling, sega genesis aesthetic, 
dark rust-purple sky, floating debris"
```

---

## Biome 3: Coelacanth's Lair

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Dark teal depth | `#001a10` | (0, 26, 16) | ██████ |
| Mid lair | `#002a18` | (0, 42, 24) | ██████ |
| Upper cavern | `#0a2018` | (10, 32, 24) | ██████ |
| Electric cyan | `#00CC66` | (0, 204, 102) | ██████ |
| Deep green | `#006644` | (0, 102, 68) | ██████ |
| Toxic green | `#008866` | (0, 136, 102) | ██████ |

### Mood
Submerged caverns crackling with electrical energy. Tesla arcs spider across the ceiling.
Coolant drips from ancient machinery. The lair of the Cyber Coelacanth — a fusion of
organic predator and cybernetic horror. Green bioluminescence and arcing blue-white
electricity define the space.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `tesla_bolt` (primary) | Every 14s | `#00CCFF` | Multi-point jagged line, white core, cyan glow, static |
| `coolant_drip` (secondary) | 30% chance | `#33CC55` | Falls top-to-bottom, green oblong droplet |

### Background Composition
- **Far:** Dark teal gradient (green-black depths)
- **Nebula blobs:** Electric green radial gradients
- **Star field:** 200 white + 15 green accent stars
- **Parallax layers:** Cave ceiling silhouettes, distant machinery outlines

### Screen Shake Tint
`#CC0000` — angry red flash (combat intensity)

### Reference Image Keywords (Imagen/Flow)
```
"underwater cybernetic lair, tesla coils arcing, 16-bit pixel art, green bioluminescence, 
cyber coelacanth cave, dripping coolant, electric blue arcs, dark teal cavern, 
sega genesis aesthetic, industrial horror, parallax cave layers"
```

---

## Biome 4: Nebula Drift

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Void purple | `#100020` | (16, 0, 32) | ██████ |
| Nebula deep | `#1a0030` | (26, 0, 48) | ██████ |
| Cosmic edge | `#200840` | (32, 8, 64) | ██████ |
| Plasma violet | `#8844CC` | (136, 68, 204) | ██████ |
| Deep magenta | `#442288` | (68, 34, 136) | ██████ |
| Bright plasma | `#6644AA` | (102, 68, 170) | ██████ |

### Mood
Drifting through vast nebula clouds of ionized plasma. Ribbons of blue and magenta energy
stream past. Lightning flashes illuminate the void. Serene on the surface, but charged
with deadly plasma currents. Psychedelic color shifts between cyan-blue and hot magenta.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `plasma_ribbon` (primary) | Every 10s | `#00BFFF` or `#FF00FF` | Horizontal ribbons, sinusoidal drift, dual-color gradient |
| `storm_flash` (secondary) | 20% chance | `#FFFFFF` | Full-screen white flash, 80ms |

### Background Composition
- **Far:** Deep purple cosmic void gradient
- **Nebula blobs:** Violet-magenta radial gradients
- **Star field:** 200 white + 15 violet accent stars
- **Parallax layers:** Wispy nebula cloud layers at different speeds

### Screen Shake Tint
`#FF00FF` — magenta plasma flash

### Reference Image Keywords (Imagen/Flow)
```
"cosmic nebula drift, plasma ribbons, 16-bit pixel art, blue and magenta energy streams, 
deep purple space, lightning flashes, ethereal clouds, parallax scrolling, 
sega genesis aesthetic, psychedelic space, ionized gas, dark void"
```

---

## Biome 5: Ice Ring

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Deep ice | `#081020` | (8, 16, 32) | ██████ |
| Mid frost | `#0a1830` | (10, 24, 48) | ██████ |
| Sky ice | `#102040` | (16, 32, 64) | ██████ |
| Ice blue | `#88CCFF` | (136, 204, 255) | ██████ |
| Mid crystal | `#4488AA` | (68, 136, 170) | ██████ |
| Bright crystal | `#66AACC` | (102, 170, 204) | ██████ |

### Mood
Saturn's ice rings — a frozen crystalline expanse. Hexagonal ice crystals drift and
sparkle. Prismatic light beams refract through the ice field. Cold, geometric beauty.
The silence of absolute zero, broken only by the glint of light on frozen surfaces.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `ice_crystal` (primary) | Every 12s | `#EEEFFF` | Hexagonal, rotating, sparkles on interval, cyan glow |
| `prism_beam` (secondary) | 18% chance | `#88CCFF` | Long vertical beam, slight angle oscillation, translucent |

### Background Composition
- **Far:** Deep ice-blue gradient
- **Nebula blobs:** Cool cyan-blue radial gradients
- **Star field:** 200 white + 15 ice-blue accent stars
- **Parallax layers:** Ice ring bands, crystal formations, geometric patterns

### Screen Shake Tint
`#88CCFF` — ice-blue flash

### Reference Image Keywords (Imagen/Flow)
```
"saturn ice ring, hexagonal ice crystals, 16-bit pixel art, prismatic light beams, 
frozen geometric landscape, cyan sparkles, parallax scrolling, dark blue void, 
sega genesis aesthetic, diamond dust, crystalline refraction, cold space"
```

---

## Biome 6: Fire Nebula

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Deep ember | `#200802` | (32, 8, 2) | ██████ |
| Mid fire | `#300c04` | (48, 12, 4) | ██████ |
| Smoldering | `#1a0802` | (26, 8, 2) | ██████ |
| Blaze orange | `#FF6600` | (255, 102, 0) | ██████ |
| Deep ember | `#883300` | (136, 51, 0) | ██████ |
| Lava core | `#AA4400` | (170, 68, 0) | ██████ |

### Mood
The blazing inferno of a dying star. Embers rise from below in spiraling columns.
Ash clouds drift across the view. Everything burns — orange, red, amber. The heat
is oppressive, the light blinding. Betelgeuse's final centuries of rage.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `ember` (primary) | Every 13s | `#FF4400` or `#FFAA00` | Rises from bottom, spiral pattern, large glow |
| `ash_cloud` (secondary) | 22% chance | `#443333` | Large slow cloud, drifts left, radial fade |

### Background Composition
- **Far:** Deep red-orange gradient (fire depths)
- **Nebula blobs:** Orange-amber radial gradients
- **Star field:** 200 white + 15 orange accent stars
- **Parallax layers:** Flame columns, smoke layers, heat distortion

### Screen Shake Tint
`#FF4400` — fire-red flash

### Reference Image Keywords (Imagen/Flow)
```
"burning star nebula, fire and ember storm, 16-bit pixel art, orange and red inferno, 
rising embers, ash clouds, parallax scrolling, sega genesis aesthetic, 
betelgeuse dying star, heat waves, volcanic space, molten core"
```

---

## Biome 7: Storm Belt

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Storm dark | `#101018` | (16, 16, 24) | ██████ |
| Mid tempest | `#181828` | (24, 24, 40) | ██████ |
| Cloud edge | `#202038` | (32, 32, 56) | ██████ |
| Lightning blue | `#AAAAAA` | (170, 170, 204) | ██████ |
| Storm steel | `#666688` | (102, 102, 136) | ██████ |
| Static blue | `#8888AA` | (136, 136, 170) | ██████ |

### Mood
The violent atmosphere of HD 189733b — a planet of endless storms. Lightning strikes
crack horizontally across the screen. Rain sheets down. Static bands pulse. The most
hostile weather in the galaxy, a cage of electricity and fury.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `lightning_strike` (primary) | Every 14s | `#FFFFFF` w/ `#4466FF` glow | Jagged horizontal bolt, multi-step, white core + blue glow, 150ms |
| `rain_drop` (secondary) | Every 8s | `#CCDDFF` | Falls top-to-bottom fast, slight rightward drift |
| `static_band` (tertiary) | 15% chance | `#4466FF` | Full-width horizontal band, scrolls downward |

### Background Composition
- **Far:** Dark storm-grey gradient
- **Nebula blobs:** Blue-steel radial gradients
- **Star field:** 200 white + 15 static-blue accent stars
- **Parallax layers:** Storm cloud layers, lightning flash illumination

### Screen Shake Tint
`#CCDDFF` — pale blue-white flash

### Reference Image Keywords (Imagen/Flow)
```
"violent gas giant storm, lightning strikes, 16-bit pixel art, horizontal lightning bolts, 
torrential rain, dark storm clouds, blue static bands, parallax scrolling, 
sega genesis aesthetic, HD 189733b, electric fury, tempest atmosphere"
```

---

## Biome 8: Derelict Fleet

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Space wreck | `#181008` | (24, 16, 8) | ██████ |
| Mid wreckage | `#201410` | (32, 20, 16) | ██████ |
| Hull edge | `#281810` | (40, 24, 16) | ██████ |
| Rust-brown | `#CC8844` | (204, 136, 68) | ██████ |
| Hull steel | `#664422` | (102, 68, 34) | ██████ |
| Rusted edge | `#886633` | (136, 102, 51) | ██████ |

### Mood
Orbiting graveyard of a thousand dead ships. Hull fragments tumble through the void.
Red beacon lights flash from derelict vessels. Coolant gas leaks form drifting clouds.
A monument to a forgotten war. Lonely, haunted, industrial.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `debris` (primary) | Every 9s | `#555566` w/ `#886644` edge | Rectangular hull fragment, rotating, random drift |
| `beacon_flash` (secondary) | 12% chance | `#FF2222` | Red radial pulse, brief (300ms) |
| `coolant_gas` (tertiary) | 20% chance | `#33FF33` | Green expanding cloud, radial fade |

### Background Composition
- **Far:** Dark brown-grey space gradient
- **Nebula blobs:** Rust-brown radial gradients
- **Star field:** 200 white + 15 orange-brown accent stars
- **Parallax layers:** Distant fleet silhouettes, wreckage fields, station outlines

### Screen Shake Tint
`#FF2222` — red beacon flash

### Reference Image Keywords (Imagen/Flow)
```
"derelict spaceship graveyard, orbital debris field, 16-bit pixel art, rust and steel, 
red beacon lights, floating wreckage, green coolant leaks, parallax scrolling, 
sega genesis aesthetic, abandoned fleet, industrial decay, haunted orbit"
```

---

## Biome 9: Xenomorph Hive

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Flesh void | `#050508` | (5, 5, 8) | ██████ |
| Organic dark | `#0a0a10` | (10, 10, 16) | ██████ |
| Pulsing flesh | `#100818` | (16, 8, 24) | ██████ |
| Toxic green | `#44FF44` | (68, 255, 68) | ██████ |
| Flesh vein | `#224422` | (34, 68, 34) | ██████ |
| Organ pink | `#336633` | (51, 102, 51) | ██████ |

### Mood
Living nightmare. The walls are alive — organic membranes pulse and writhe. Acid drips
from organic ducts. Spores drift through the fetid air. Veins throb with alien ichor.
A hive mind's physical manifestation — the ultimate bio-horror.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `spore` (primary) | Every 11s | `#CC6677` | Small floating circles, random gentle drift |
| `acid_drip` (secondary) | 25% chance | `#33FF33` | Falls top-to-bottom, green glow, oblong |
| `vein_pulse` (tertiary) | 30% chance | `#6633AA` or `#CC6677` | Pulsing orb, alpha oscillates, persists |

### Background Composition
- **Far:** Dark organic green-black gradient
- **Nebula blobs:** Toxic green and flesh-pink radial gradients
- **Star field:** 200 white + 15 green accent stars
- **Parallax layers:** Organic membrane walls, ribbed tunnels, vein networks

### Screen Shake Tint
`#33FF33` — toxic green flash

### Reference Image Keywords (Imagen/Flow)
```
"alien organic hive, living walls, 16-bit pixel art, toxic green bioluminescence, 
pulsing veins, drifting spores, acid drips, bio-horror, parallax scrolling, 
sega genesis aesthetic, xenomorph nest, organic membranes, flesh tunnels"
```

---

## Biome 10: Core Rift

### Palette (6 colors)
| Role | Hex | RGB | Swatch |
|------|-----|-----|--------|
| Reality void | `#050508` | (5, 5, 8) | ██████ |
| Rift edge | `#0a0a10` | (10, 10, 16) | ██████ |
| Collapse | `#100818` | (16, 8, 24) | ██████ |
| Digital pink | `#FF44FF` | (255, 68, 255) | ██████ |
| Void purple | `#442244` | (68, 34, 68) | ██████ |
| Rift magenta | `#663366` | (102, 51, 102) | ██████ |

### Mood
The galactic core — where reality itself tears apart. Hexadecimal code streams rain
down as the simulation's source code bleeds through. Rift tears open in the fabric
of space, revealing the raw data beneath. Echo shards of defeated timelines flicker
past. The final frontier between existence and digital oblivion.

### Particle Types
| Type | Spawn | Color | Behavior |
|------|-------|-------|----------|
| `code_stream` (primary) | Every 15s | `#00FF41` | Matrix-style falling hex chars, green, fast |
| `rift_tear` (secondary) | 18% chance | `#FF0088` | Jagged crack line, magenta glow, pulsing alpha |
| `echo_shard` (tertiary, unused in spawner) | — | `#FFFFFF` | White rectangular fragment, slow drift, low alpha |

### Background Composition
- **Far:** Deep purple-black void gradient
- **Nebula blobs:** Magenta-pink radial gradients
- **Star field:** 200 white + 15 pink-magenta accent stars
- **Parallax layers:** Rift seams, data streams, glitch artifacts

### Screen Shake Tint
`#FF0088` — magenta rift flash

### Reference Image Keywords (Imagen/Flow)
```
"reality-bending galactic core, digital matrix rain, 16-bit pixel art, magenta rifts, 
green code streams, space-time tears, glitch aesthetic, parallax scrolling, 
sega genesis aesthetic, simulation collapse, cyberpunk void, final frontier"
```

---

## Cross-Biome Design Rules

### Pixel Art Consistency
- All backgrounds rendered at 16-bit "Sega Genesis" fidelity
- Use dithering for gradients (no smooth blends)
- Dark dominant palettes — bright neon accents only for particles/lighting
- Sprite grid: 32×32 or 64×64 standard, 128×128+ for bosses

### Parallax Layer Standard
Each biome needs 3–5 depth layers:
1. **Far:** Static or very slow scroll (0.1x) — nebula, starfield, deep void
2. **Mid:** Slow scroll (0.3x) — silhouettes, structures, cloud banks
3. **Mid-near:** Medium scroll (0.6x) — environmental features (coral, ice, wreckage)
4. **Near:** Fast scroll (1.0x) — particles, foreground debris

### Image Generation Prompt Template
```
"[biome description], 16-bit pixel art, [palette colors], [dominant mood],
parallax scrolling background layers, seamless horizontal tiling,
sega genesis aesthetic, dark cyberpunk palette, space shmup background,
1024×256 strip format, dithering, neon accents"
```

---

## Source References

| Source | What It Provides |
|--------|-----------------|
| `js/renderer.js` lines 229–240 | Procedural biome palettes (`themes` object) |
| `js/renderer.js` lines 474–744 | Particle type colors and initialization |
| `js/renderer.js` lines 940–1174 | Particle draw routines (visual detail) |
| `js/renderer.js` lines 1181–1184 | Screen shake tint colors |
| `js/level_manager.js` lines 402–449 | Particle spawn configurations per biome |
| `js/level_manager.js` lines 46–49 | Canonical biome names |
| `docs/GAME-DESIGN-DOCUMENT.md` §3.1, §6 | Biome locations, palette overview, parallax spec |
| `docs/foundational-structure-audit.md` §2 | Biome system architecture |

---

*Generated from live code inspection by Ned (GRO-1110). June 2026.*
*For image generation agents: the palettes above are the authoritative reference.*

---
type: Reference
title: "Darius Star — Game Mechanics Design"
description: "Comprehensive game mechanics design for Darius Star (Cyber Coelacanth) — 25KB covering combat, upgrades, enemies, boss design, progression, scoring."
resource: okf/projects/darius-star/storyline/darius-star-game-mechanics.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:10:56Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/darius-star-game-mechanics.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "/home/ubuntu/darius-star-game-mechanics.md"
migrated_from_repo: mbgulden/darius-star
---
# Darius Star: Cyber Coelacanth — Game Mechanics & Systems Design

> **Document:** Mechanics, Specials, and Upgrade Systems  
> **Game:** Horizontal Retro Shoot-'em-Up · HTML5 Canvas  
> **Author:** Hermes Agent (Nous Research)  
> **Date:** 2026-06-09  

---

## Table of Contents

1. [Ship Specials](#1-ship-specials)
2. [Scrap / Upgrade Economy](#2-scrap--upgrade-economy)
3. [Fun Mechanics & Juice](#3-fun-mechanics--juice)
4. [Implementation Priority](#4-implementation-priority)

---

## 1. Ship Specials

Each ship has a unique **Special Ability** mapped to a dedicated key (default: **Spacebar**) with a cooldown bar shown beneath the ship's HP indicator. Specials reward different playstyles and create ship identity beyond stat differences. All ships share the same core weapon leveling (Single → Double → Triple Spread → Heavy Pulsar → Supreme Nova).

### 1.1 STRIKER — *"Shock Lance"*

| Attribute | Detail |
|---|---|
| **Name** | Shock Lance |
| **Trigger** | Tap Special key (instant, no hold) |
| **Cooldown** | 12 seconds |
| **Effect** | Fires a piercing horizontal beam (4× ship length, 3 tiles wide) that passes through all enemies and destructible projectiles. Deals 200% base DPS as instant damage to everything in its path. |
| **Visual** | White-hot energy lance crackles along the firing line for 0.4s. Screen edges flash blue. Enemies hit spark with electrical arcs that chain to nearby foes (cosmetic only). |
| **Sound** | Rising capacitor whine → sharp **CRACK** → low bass rumble decay (0.6s total). |
| **Strategy** | The balanced workhorse special. Excellent for clearing bullet curtains during boss rage phases, deleting interceptor waves in corridors, and emergency screen-clear when cornered. Use reactively — the piercing property means positioning matters less than timing. |

### 1.2 PHANTOM — *"Phase Shift"*

| Attribute | Detail |
|---|---|
| **Name** | Phase Shift |
| **Trigger** | Hold Special key to sustain (max 2.5s), release to end early |
| **Cooldown** | 18 seconds (starts when phase ends) |
| **Effect** | Ship becomes translucent, invulnerable, and gains +60% movement speed. Cannot fire weapons while phased. Passing through enemies deals 50% base DPS as "disruption damage" (one hit per enemy per phase). |
| **Visual** | Ship strobes between 40% and 90% opacity at 8 Hz. Trail leaves ghostly afterimages (4 copies, each at 25% opacity, 80ms stagger). Enemies passed through briefly glitch with horizontal RGB-split effect. |
| **Sound** | Deep whoosh on enter (like passing through a tunnel at speed), muffled ambient loop while sustained, sharp re-materialization *thwip* on exit. |
| **Strategy** | The ultimate repositioning tool. Phase through bullet walls to grab power-ups behind enemy lines. Essential for speed-run routing — phase past slow sections. The no-fire constraint forces a trade-off: pure survival vs. offensive output. Master players chain phase-exit into immediate full-power volleys. |

### 1.3 BASTION — *"Iron Curtain"*

| Attribute | Detail |
|---|---|
| **Name** | Iron Curtain |
| **Trigger** | Tap Special key |
| **Cooldown** | 20 seconds |
| **Effect** | Deploys a stationary energy barrier 3 tiles ahead of the ship. Barrier is 5 tiles wide × 4 tiles tall, absorbs all enemy projectiles (up to 15 hits), and persists for 4 seconds. Allies behind the barrier are also protected. Barrier deals 30% base DPS as contact damage to enemies that touch it. |
| **Visual** | Hexagonal honeycomb shield grid materializes with a ripple effect from center outward. Each absorbed hit creates a white impact flash and shrinks the visible honeycomb by one cell. At 5 hits remaining, barrier pulses red. Shatters into glass-like fragments on expiry/destruction. |
| **Sound** | Heavy mechanical *CLUNK* on deploy, resonant shield-hum loop while active, each hit produces a metallic *PING* that rises in pitch as barrier weakens, glass-break *CRASH* on destruction. |
| **Strategy** | The co-op linchpin. Deploy during boss laser charge phases to protect the entire squad. Stack two Bastions in 4-player for near-continuous coverage. Solo players use it to create safe zones for charging Heavy Pulsar shots. Position aggressively — the contact damage rewards placing the barrier inside enemy formations. |

### 1.4 TEMPEST — *"Overload"*

| Attribute | Detail |
|---|---|
| **Name** | Overload |
| **Trigger** | Tap Special key |
| **Cooldown** | 14 seconds |
| **Effect** | Instantly maxes weapon level to Supreme Nova for 3 seconds, regardless of current level. During overload, fire rate increases +40% and all projectiles gain minor homing (15° tracking arc). After overload ends, weapon reverts to previous level. |
| **Visual** | Ship hull glows from within (orange → white), weapon ports crackle with excess energy. Projectiles leave thicker, brighter trails. A visible heat-distortion shader warps the area around the ship. Small HUD timer counts down 3-2-1 beside weapon icon. |
| **Sound** | Industrial alarm klaxon (0.3s) → intense rising synthesizer arpeggio during overload → power-down *whump* with reverb tail. Weapon fire SFX pitch-shifts up 2 semitones during overload. |
| **Strategy** | Burst-window DPS monster. Pop Overload as bosses enter vulnerable states after laser fire. Combo with scrap-dropped temporary boosts for multiplicative carnage. The +40% fire rate turns Supreme Nova's already-screen-filling spread into an impassable wall of death. Skill ceiling: learn to route so Overload is always off-cooldown when reaching miniboss gates. |

### 1.5 SPECTER — *"Shadow Clone"*

| Attribute | Detail |
|---|---|
| **Name** | Shadow Clone |
| **Trigger** | Tap Special key |
| **Cooldown** | 16 seconds |
| **Effect** | Deploys a decoy at current position that persists for 5 seconds. Decoy draws all enemy fire and has 8 HP (can be destroyed). Ship gains invisibility (30% opacity, enemies ignore) for 3 seconds. Firing breaks invisibility early. Decoy pulses a small EMP on destruction (1-tile radius, stuns minor enemies 1.5s). |
| **Visual** | Decoy materializes as a perfect cyan-tinted hologram of the ship with subtle scanline overlay. On deployment, the real ship flickers out with a horizontal wipe transition. Decoy destruction triggers a blue-white expanding ring EMP. |
| **Sound** | Digital glitch-stutter on clone creation, heartbeat thump (low-pass filtered) during invisibility, EMP burst is a sharp static *BZZZT* with 0.2s digital silence afterward. |
| **Strategy** | The tactical choice. Drop clone before boss rage phases to redirect devastating pattern attacks. In co-op, the clone tanks for the whole party. The 3s invisibility window is precious — use it to reposition behind heavy enemies for rear weak-point shots, or to safely collect scrap in bullet-dense zones. The EMP on destruction rewards deliberately placing the clone inside enemy clusters. |

### Special Cooldown Modifiers (Upgradeable)

| Upgrade Tier | Effect | Scrap Cost |
|---|---|---|
| Tier 1: Cooldown Actuator | -10% cooldown | 150 |
| Tier 2: Thermal Sink | -20% cooldown (replaces T1) | 400 |
| Tier 3: Quantum Capacitor | -30% cooldown + 0.5s longer duration (replaces T2) | 900 |

---

## 2. Scrap / Upgrade Economy

### 2.1 Scrap Drops by Enemy Type

Scrap is the universal currency. It auto-collects in a small radius (2 tiles) around the player ship; beyond that, players must fly over it.

| Enemy | Scrap (Min) | Scrap (Max) | Drop Rate | Notes |
|---|---|---|---|---|
| **Scout** (sine-wave) | 1 | 3 | 70% | Primary early-game income. Low value but numerous. |
| **Interceptor** (speed-charge) | 3 | 7 | 85% | Higher risk → higher reward. Drops in a line along charge path. |
| **Heavy** (shoots back) | 8 | 15 | 100% | Guaranteed drop. Destroying all turrets before main body yields +5 bonus scrap. |
| **Boss Minion** | 5 | 12 | 100% | Spawned during boss fights. Essential for keeping economy flowing in endurance phases. |
| **Mid-boss** (every 10th sub-level) | 30 | 60 | 100% | Major injection point. Also drops 1 guaranteed Power Core (see below). |
| **Cyber Coelacanth (Boss)** | 150 | 300 | 100% (per phase) | Drops scrap on each of its 5 state transitions. Final defeat drops 500 + 3 Power Cores. |
| **Destructible Terrain** | 1 | 5 | 40% | Crystals, cargo containers, and ancient ruins scattered through biomes. |
| **Secret Area Cache** | 25 | 50 | 100% | Hidden behind destructible walls. One per biome. |

### 2.2 Power Cores (Rare Currency)

Power Cores are rare drops used for **permanent meta-progression unlocks** (ship unlocks, alternate weapon skins, gallery items). They do NOT affect in-run power.

| Source | Cores |
|---|---|
| Mid-boss defeat | 1 |
| Cyber Coelacanth final defeat | 3 |
| Daily Challenge completion | 1 |
| Secret area discovery | 1 |
| Achievement milestones | 1–5 |

### 2.3 One-in-a-Million Legendary Scrap System

In addition to standard scrap and Power Cores, every enemy destroyed has a **0.0001% (one-in-a-million)** baseline chance to drop a **Legendary Scrap Component**. These components represent highly advanced or pristine precursor/naval technology salvaged from the wreckage. Collecting a Legendary Scrap Component instantly unlocks a unique, game-changing passive buff or ability for the rest of the run.

| Biome | Legendary Component | Rest-of-Run Active/Passive Effect |
|---|---|---|
| **1: Abyssal Trench** | **Abyssal Heart Core** | +25% scrap multiplier from all deep-sea enemies. |
| **2: Coral Graveyard** | **Precursor Resonance Shard** | Special ability cooldown reduced by 20%. |
| **3: Coelacanth Lair** | **Cryo-Forged Alloy** | Max Hull +200, immune to freezing conditions. |
| **4: Nebula Drift** | **Nebula Essence** | Weapons gain 10% chance to bypass enemy shields entirely. |
| **5: Ice Ring** | **Umbra Stealth Circuit** | Active cloak duration increased by 3 seconds. |
| **6: Fire Nebula** | **Forge-Mind Ember** | Primary weapon gains heat damage-over-time (burns for 5% DPS). |
| **7: Storm Belt** | **Storm-Singer's Tear** | Shield recharge delay reduced by 50%, regen rate +50%. |
| **8: Derelict Fleet** | **Admiral's Cipher** | 15% chance when destroying an enemy drone to hack and convert it to fight for you. |
| **9: Xenomorph Hive** | **Hive Nucleus** | Slowly regenerate 2% Hull per second when remaining stationary for 1.5s. |
| **10: Core Rift** | **Dreamer's Fragment** | Permanent +10% boost to all ship attributes (Hull, Shield, Speed, Damage). Carries over into NG+. |

*Note: In New Game Plus (NG+), the drop rate of these legendary components is enhanced by 0.0001% for each previous Legendary Component found (capped at a cumulative +0.001% bonus drop rate).*

### 2.4 Upgrade Tree

Upgrades are purchased between sub-levels at the **Upgrade Station** (appears every 3 sub-levels). All upgrades are **per-run only** (lost on death/restart).

#### WEAPON BRANCH

```
L1: Recycled Barrel          (50 scrap)   → Projectile speed +10%
L2: Focusing Lens            (120 scrap)  → Projectile size +15%, damage +8%
L3: Plasma Infuser           (250 scrap)  → Projectiles pierce 1 enemy
L4: Overcharged Coils        (500 scrap)  → Fire rate +20%
L5: Dimensional Splitter     (900 scrap)  → Every 5th shot fires 2 extra projectiles
```

#### SHIELD BRANCH

```
L1: Reinforced Hull          (60 scrap)   → Max HP +15%
L2: Nano-Repair Matrix       (150 scrap)  → Regen 1 HP per 8 seconds
L3: Reactive Armor           (300 scrap)  → 0.3s invulnerability on hit (once per 15s)
L4: Ablative Plating         (550 scrap)  → Reduce all damage by 1 (min 1)
L5: Emergency Protocol       (950 scrap)  → On lethal hit, survive at 1 HP (once per run)
```

#### ENGINE BRANCH

```
L1: Thruster Tune-Up         (50 scrap)   → Speed +8%
L2: Gyro Stabilizers         (120 scrap)  → Deceleration 2× faster (responsive stops)
L3: Afterburner Injectors    (250 scrap)  → Hold [Shift] for +40% speed burst (3s fuel, 8s recharge)
L4: Inertial Dampeners       (500 scrap)  → Hitstun reduced by 50%
L5: Phase Drive              (900 scrap)  → Brief dash (1 tile) on double-tap direction (6s cooldown)
```

#### SPECIAL BRANCH

```
L1: Cooldown Actuator        (150 scrap)  → Special cooldown -10%
L2: Thermal Sink             (400 scrap)  → Special cooldown -20%
L3: Quantum Capacitor        (900 scrap)  → Special cooldown -30%, duration +0.5s
```

#### UTILITY BRANCH

```
L1: Scrap Magnet             (80 scrap)   → Auto-collect radius +100%
L2: Lucky Charm              (180 scrap)  → Enemy drop rate +15%
L3: Salvage Specialist       (350 scrap)  → +25% scrap from all sources
L4: Emergency Cache          (600 scrap)  → Start each sub-level with 10 bonus scrap
L5: Black Market Connection  (1000 scrap) → Upgrade Station prices -20% for rest of run
```

### 2.4 Pricing Curve Rationale

The pricing follows a **super-linear curve** (roughly n² scaling) to create meaningful decisions:

- **Tier 1–2 (50–180 scrap):** Affordable in first biome. Lets players establish a build direction early.
- **Tier 3 (250–350 scrap):** Requires saving through a full biome. Forces trade-offs between branches.
- **Tier 4 (500–600 scrap):** A 2-biome commitment. Players typically max 1–2 branches per run.
- **Tier 5 (900–1000 scrap):** Luxury tier. Only achievable with perfect play, Salvage Specialist, and boss bonus scrap.

A skilled player completing all 100 levels with optimal farming can earn approximately **3,200–4,500 scrap** per full run — enough to max 2 branches plus partial investment in a third.

### 2.5 Power-Up Orbs (In-Level)

| Orb | Color | Effect | Stacking |
|---|---|---|---|
| Weapon Upgrade | Red | Advances weapon 1 level (max 5) | Resets to level 1 if hit while at Supreme Nova (risk!) |
| Shield Restore | Green | Restores 2 HP (up to max) | Overheal becomes temporary +2 HP buffer for 15s |
| Scrap Boost | Gold | +25 instant scrap | — |
| Score Multiplier | Blue | 2× score for 20 seconds | Stacks additively with combo multiplier |
| Speed Boost | Cyan | +30% speed for 8 seconds | Refreshes duration |
| Slow Field | Purple | All enemies slow to 50% speed for 6s | Refreshes duration |

---

## 3. Fun Mechanics & Juice

### 3.1 Screen Shake

| Event | Intensity | Duration | Falloff |
|---|---|---|---|
| Player hit | 3px, directional (away from damage source) | 0.15s | Linear |
| Heavy enemy destroyed | 5px, omnidirectional | 0.25s | Eased (ease-out cubic) |
| Mid-boss destroyed | 8px, omnidirectional | 0.5s | Eased, with 0.2s pause before shake |
| Boss phase transition | 6px, horizontal only | 0.4s | Eased, synchronized with screen flash |
| Boss final destruction | 12px, omnidirectional | 1.2s | Parabolic (ramp up → hold → decay) |
| Special ability use | 2px (per ship, varies) | 0.1s | Linear |
| Supreme Nova fire | 1px continuous | Persistent while firing | Subtle, adds "weight" |

**Implementation note:** Screen shake offset is applied to the camera transform, not individual sprites. All gameplay coordinates remain stable — only the viewport shifts.

### 3.2 Hit-Stop (Impact Freeze)

Brief (<100ms) game-pause on significant impacts to sell weight and power:

| Event | Freeze Duration |
|---|---|
| Boss takes damage during vulnerable phase | 80ms |
| Mid-boss destroyed | 120ms |
| Charged shot connecting | 50ms |
| Special ability hitting 5+ enemies simultaneously | 60ms |
| Player death | 200ms (with red vignette fade) |

Hit-stop freezes **enemy movement and projectiles** but allows player input buffering — the next input is queued and executed on frame 1 after freeze. This prevents the freeze from feeling like input lag.

### 3.3 Combo System

**Chain Meter:** Destroying enemies without taking damage builds a visible combo counter (top-right HUD).

| Combo Tier | Kills Required | Score Multiplier | Visual Effect |
|---|---|---|---|
| C-rank | 0–9 | 1.0× | White counter |
| B-rank | 10–24 | 1.5× | Green counter, subtle screen-border glow |
| A-rank | 25–49 | 2.0× | Blue counter, enemy explosions slightly larger |
| S-rank | 50–74 | 3.0× | Purple counter, occasional spark particles from ship |
| SS-rank | 75–99 | 4.0× | Gold counter, background music adds extra percussion layer |
| SSS-rank | 100+ | 5.0× | Rainbow counter, brief slow-motion on each kill (30% speed, 150ms) |

**Combo Break:** Taking damage resets combo to 0. Shield barrier hits (Iron Curtain) do NOT break combo.

**Combo Decay Timer:** 2.5 seconds without a kill drops combo by 1 tier (not to zero). This rewards aggressive play without punishing brief lulls.

### 3.4 Risk/Reward Systems

#### a) Overheat Mechanic (Weapon Level 5)
Supreme Nova fires continuously, but holding fire for >4 seconds triggers **Overheat**: weapon drops to level 1 and ship takes 1 damage. A glowing heat bar appears beside the weapon icon. Risk: do you ride the edge of overheat for maximum damage, or pulse-fire safely?

#### b) Red Orb Roulette
At weapon level 5, collecting a red orb **resets to level 1** instead of upgrading. This creates tension: do you grab that red orb dropping mid-boss-fight, or dodge it? Experienced players learn orb pathing to collect only when intentional.

#### c) Scrap Multiplier Zones
Some sub-levels contain **"Rich Vein"** areas (marked by golden particle effects) where all scrap drops are doubled — but enemy spawns are +50% in density and speed. Optional: enter at your own risk.

#### d) Perfect Level Bonus
Completing a sub-level without taking damage awards +25 bonus scrap and a "Flawless" star on the level-select screen. 10 Flawless stars across a biome unlocks a secret cache.

#### e) Boss Break
Destroy all boss turrets/armor segments before killing the main body to trigger **"Full Dismantle"** — bonus scrap, bonus score, and a special kill animation. This requires precision aiming and rewards mastery over raw DPS.

### 3.5 Juice / Feedback Layers

| Layer | Implementation | Examples |
|---|---|---|
| **Visual** | Sprite squash/stretch on direction change (±15%), muzzle flash sprites (2-frame animation), enemy death particles (color-matched to enemy type), damage number pop-ups (optional, toggleable) | Player ship squashes vertically during upward movement |
| **Audio** | Layered SFX (base sound + pitch variation ±5% per shot), dynamic music intensity (layer in additional instrument tracks as combo rises), positional audio for off-screen threats | Boss music adds choir layer during rage phase |
| **HUD Juice** | Health bar pulses red at <25%, combo counter bounces on increment, scrap count flashes gold on large pickups, weapon icon shakes during overheat warning | — |
| **Environmental** | Background parallax speeds up during afterburner, biome-specific particle weather (sparks in industrial, spores in fungal, data-streams in digital), screen-edge danger indicators (red glow on nearest-danger side) | — |
| **Controller** | Rumble on hit/destroy (gamepad API), dead-zone customization, aim-assist toggle for accessibility | — |

### 3.6 Leaderboard System

**Categories:**
- **Score Attack** — Cumulative score across full 100-level run
- **Speedrun** — Real-time completion time (any%, 100%)
- **Boss Rush** — Time to defeat all 10 biome bosses consecutively
- **Daily Challenge** — Fixed seed, fixed ship, scored against global leaderboard
- **No-Hit** — Furthest level reached without taking damage

**Anti-Cheat:** Server-side validation via replay hash. Client submits inputs + seed → server simulates for verification.

### 3.7 Daily Challenges

| Parameter | Detail |
|---|---|
| **Seed** | Date-derived (YYYY-MM-DD → deterministic RNG seed) |
| **Ship** | Rotates daily (all players use same ship) |
| **Modifiers** | 1–3 random modifiers (see below) |
| **Level Set** | 30 sub-levels (3 biomes) |
| **Leaderboard** | Global + Friends, resets daily at 00:00 UTC |
| **Reward** | 1 Power Core for completion, bonus Core for top 10% |

**Daily Modifier Pool:**
- **Ammo Scarcity:** Weapon upgrades drop 50% less frequently
- **Glass Cannon:** +50% damage dealt, -50% max HP
- **Inverted:** Up/down controls reversed
- **Swarm:** Double enemies, half HP each
- **One Life:** No shield restores, no continues
- **Big Head Mode:** All sprites 2× size (enemies easier to hit, harder to dodge)
- **Gravity:** Constant downward pull (1px/frame)
- **Superhot:** Time moves only when you move
- **Pacifist:** No weapons — must phase/dash/barrier through enemies
- **Turbo:** Game speed 1.5×

---

## 4. Implementation Priority

Ranked by **impact × feasibility**, accounting for an HTML5 Canvas environment (single-threaded, requestAnimationFrame loop, no GPU shaders).

| Rank | System | Rationale | Dependencies | Est. Effort |
|---|---|---|---|---|
| **1** | Core Weapon Leveling (1→5) | THE defining shoot-'em-up mechanic. Everything else builds on this. Must feel good immediately. | None | 3 days |
| **2** | Scrap Drops + Basic Upgrade Station | Core loop: kill → earn → spend. Without economy the game has no progression. Requires UI but minimal integration. | Weapon system (Rank 1) | 3 days |
| **3** | Screen Shake + Basic Juice | Immediate game-feel multiplier. Low implementation cost (viewport offset), massive perceived quality improvement. | Camera system | 1 day |
| **4** | 4 Enemy Types + AI Behaviors | Game is unplayable without enemies. Scout + Interceptor first (easy), Heavy + Minion second (state machines). | Spawning system | 4 days |
| **5** | Ship Specials (5 ships) | High-impact differentiator. Can be prototyped per-ship. BASTION + STRIKER first (simplest), SPECTER + PHANTOM last (stateful). | Weapon system, cooldown timer | 5 days |
| **6** | Combo System | Drives engagement and scoring depth. UI counter + multiplier math is straightforward. Hit-stop deferred to Rank 8. | Score system | 2 days |
| **7** | Full Upgrade Tree (5 branches × 5 tiers) | Build variety and replayability. Many upgrades are numeric modifiers — fast to implement. Exotic T5 upgrades deferred if needed. | Upgrade Station (Rank 2) | 4 days |
| **8** | Hit-Stop System | High juice payoff but tricky in single-threaded JS: requires delta-time manipulation and careful state management. Implement after core loop is stable. | Game loop refactor | 2 days |
| **9** | Daily Challenges + Leaderboard | Drives retention. Requires backend (Firebase or similar). Client-side seed RNG is easy; server validation is the bulk of work. | Full game loop complete | 5 days |
| **10** | Co-op (2–4 player) | Highest complexity. Input multiplexing, network sync or local-only, UI scaling for multiple ships, balance tuning for combined specials. Must ship as post-launch feature. | Entire game stable | 10+ days |

### Dependency Graph

```
Rank 1 (Weapons) ──┬── Rank 2 (Economy) ─── Rank 7 (Upgrade Tree)
                   │
                   ├── Rank 4 (Enemies)
                   │
                   └── Rank 5 (Specials) ──┐
                                           │
Rank 3 (Juice) ────────────────────────────┼── Rank 8 (Hit-Stop)
                                           │
Rank 6 (Combo) ────────────────────────────┘

Rank 9 (Daily/Leaderboard) ─── Requires full loop stable
Rank 10 (Co-op) ────────────── Requires everything
```

### Quick-Win Recommendations

1. **Day 5 milestone:** Single weapon leveling + 1 enemy type + scrap drops = playable prototype loop.
2. **Day 10 milestone:** All 4 enemies + 3 weapon levels + 2 ship specials + screen shake = vertical slice.
3. **Day 20 milestone:** Full upgrade tree + combo + boss AI (5 states) = alpha candidate.
4. **Day 30 milestone:** All 5 ships + Daily Challenges = feature-complete single-player.

---

## Appendix: Boss AI State Machine (Cyber Coelacanth)

For reference — the 5-state boss AI the above systems interact with:

| State | Trigger | Behaviour | Duration |
|---|---|---|---|
| **Intro** | Boss spawns | Descends from top with invulnerability. Roar animation. | 4s |
| **Idle** | After intro / after laser_fire | Patrols top third of screen. Fires pattern A (spiral) every 2s. Spawns 2 minions. | 8–12s |
| **Rage** | HP < 50% or idle timer expires 3× | Speed +40%. Fires pattern B (dense fans) every 1.5s. Charges at player position twice. | 6s |
| **Laser Charge** | After rage ends | Moves to center. Mouth glows. 3-second telegraph (expanding energy orb). Vulnerable during charge! | 3s |
| **Laser Fire** | After charge completes | Sweeping vertical laser beam (full screen height, moves left→right→left over 2.5s). Invulnerable during fire. | 2.5s |

**Loop:** After Laser Fire → returns to Idle (or Rage if HP threshold met). Cycle repeats with decreasing Idle duration as HP drops.

---

*End of deliverable. All systems designed for HTML5 Canvas with requestAnimationFrame loop, single-threaded JavaScript, and progressive implementation.*

---
type: Reference
title: "Darius Star — Naya Warden Ship"
description: "Design doc for the Naya Warden ship — abilities, story role, biome context, balance considerations."
resource: okf/projects/darius-star/storyline/naya-warden-ship.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/naya-warden-ship.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/naya-warden-ship.md"
migrated_from_repo: mbgulden/darius-star
---

# Naya's Warden — Ship Design, Sprite & Backstory
## GRO-948 | NX-07 "Warden" Heavy Escort Fighter

> *"They tried. I said no."* — Naya Star, upon reuniting with Darius post-biome 6

---

## 1. NAYA STAR — CHARACTER PROFILE

### Basic Data

| Field | Value |
|-------|-------|
| **Full Name** | Naya Star (née Thorne) |
| **Age** | 32 |
| **Former Rank** | Lieutenant, Orbital Platform Security Corps |
| **Relation** | Wife of Darius Star, mother of Lyra Star, sister of Commander Jack Thorne |
| **Status** | Active co-protagonist — joins from biome 7 onward |
| **Role** | Tank/Escort pilot in 2-player co-op mode |
| **Voice Type** | Steady, low-register, military cadence with dry humor. Rarely raises her voice — authority doesn't need volume. |

### Backstory

Before marrying Darius, Naya was **Lieutenant Naya Thorne**, a decorated officer in the Orbital Platform Security Corps. She led the defense of Haven-7 during the Ceres Salvage Riots of 2247, earning a commendation for valor. She left active duty when Lyra was born, choosing family over career.

But she never stopped training. The simulators in Haven-7's security wing still recognize her biometrics. She kept her certification current. *"Just in case,"* she told Darius. *"The black never stops being dangerous."*

### The Attack on Haven-7 (Biome 6)

While Darius is cut off in the Fire Nebula, the Navy executes **Operation Silent Cradle** — a surgical strike on Haven-7 to extract Lyra for Project Dream-Weapon. Naya, Captain Valera Cross (secretly defected), and Selene mount a desperate defense.

Naya takes an old, decommissioned security interceptor — a ship she hasn't flown in six years — and leads the Navy gunships on a chase through Haven-7's docking spokes. She downs one gunship with an improvised debris-field ambush. The second gunship gets a lock; her interceptor takes a direct hit to the port engine. She ejects.

### Alone Behind Enemy Lines — 18 Days

Naya survives the crash with a broken arm, three cracked ribs, and a concussion. Her escape pod has emergency rations for two weeks and a distress beacon she can't activate — the Navy is still patrolling.

For **eighteen days**, she lives in the wreckage of the Fire Nebula's debris field:
- Scraps parts from dead ships for survival
- Jury-rigs a pressure shelter from a dead bulkhead
- Fights off scavenger drones with a plasma cutter
- Learns patrol rhythms and safe pockets

On day twelve, she finds the **NX-07 "Warden"** — a Navy prototype heavy fighter abandoned after the cruiser *NSS Eternal Vigil* was destroyed in a containment breach during early Dream-Weapon testing. The Navy never recovered it because the debris field was too hazardous for salvage ops.

Naya spends six days repairing it with salvaged parts. She learns its systems from the onboard technical manual. She powers it up with a jury-rigged fuel cell array pulled from three different dead ships. On day eighteen, she flies it out and limps to Haven-7's fallback coordinates.

### The Reveal (Post-Biome 6)

Darius returns from the Fire Nebula expecting to find his family dead or captured. Instead he finds Naya standing in the doorway of the depot's makeshift hangar, arm in a sling, grease on her face, silhouetted against the docking lights. Behind her: the **Warden**, scorched and patched but unmistakably lethal.

> **DARIUS**: "They said you were dead."
>
> **NAYA**: "They tried. I said no."
>
> **NAYA**: "I'm not staying behind anymore, Darius. I spent eighteen days in that graveyard thinking about you dying alone in the deep while I sat in a med-bay holding our daughter's hand. I'm a better pilot than half the Navy pilots who tried to kill me. I'm coming with you."

---

## 2. THE WARDEN — SHIP SPECIFICATION

### Designation

**NX-07 "Warden"** — Navy Experimental Heavy Fighter / Escort (Prototype Class)

### Origin

Developed under **Project Dream-Weapon** as an escort vessel designed to operate in Dreamer-influenced environments. Prototype systems included experimental psychic shielding and adaptive armor that responds to exotic particulate. Lost when the *NSS Eternal Vigil* was destroyed in a containment breach. Found by Naya in the Fire Nebula debris field, repaired with salvaged parts, and claimed as her personal ship.

### Visual Design

| Attribute | Value |
|-----------|-------|
| **Silhouette** | Bulkier and more angular than the sleek *Nyxa*. Broad-shouldered with reinforced wing roots. |
| **Armor Plating** | Visible patchwork — mismatched alloys from Naya's field repairs. Original Navy dark grey with scorch marks from the *Eternal Vigil* battle worn as scars. |
| **Insignia** | Navy insignia crudely painted over with Haven-7's station logo. |
| **Engine Glow** | **Orange (#FF6600)** — warm, stubborn, industrial. Contrasts with the Nyxa's cyan. |
| **Size** | 256×256 sprite, top-down orientation |
| **Personality** | A tank that looks like it survived — because it did. Not pretty, not fast, but indestructible. |

### Ship Stats

| Attribute | Value | Notes |
|-----------|-------|-------|
| **Class** | Heavy Fighter / Escort | Hybrid role — tank + support |
| **Hull** | 800 HP (upgradable to 1200) | Adaptive armor — 15% damage reduction vs. Dreamer-corrupted enemies |
| **Shields** | 600 SP (upgradable to 1000) | Psychic shielding — 25% resistance to Dream Pulse attacks |
| **Speed** | 6/10 | Slower than the Nyxa (8/10). Designed for escort, not pursuit. |
| **Primary Weapon** | Twin Plasma Drivers | Medium damage, medium range, sustained fire |
| **Secondary Weapon** | Point-Defense Grid | Auto-targets nearby projectiles and small enemies — protects both the Warden AND nearby allies |
| **Special Ability** | **Guardian Protocol** | Deploy a protective shield dome (radius: 200m) that absorbs 500 damage before collapsing. 90-second cooldown. Allies inside the dome receive +15% shield recharge rate. |
| **Passive** | **Scavenger's Instinct** | 20% bonus scrap from destroyed enemies when flying the Warden. Naya's debris field survival pays off. |

### Upgrade Path

| Upgrade | Biome | Effect |
|---------|-------|--------|
| **Phase 1: Debris Field Mods** | Biome 7 | +10% hull, point-defense range increased by 30% |
| **Phase 2: Navy Override Codes** | Biome 8 | Guardian Protocol cooldown reduced to 60 seconds, shield dome HP increased to 800 |
| **Phase 3: Dreamer Resonance** | Biome 9 | Adaptive armor now 25% damage reduction vs. Dreamer enemies. Naya becomes partially resistant to psychic confusion effects. |
| **Final: Mother's Vow** | Biome 10 | When Lyra's life is directly threatened (final boss), all Warden stats increase by 30% for 60 seconds. One-time use per mission. |

---

## 3. SPRITE ASSETS

### Generated Sprites

Both frames generated via **Imagen 3** (GRO-910 ship selection screen batch). Stored in the standard player sprite convention.

| Frame | File | Description |
|-------|------|-------------|
| **Idle** | `assets/sprites/player_warden_0.png` | Base Warden sprite — orange engine glow, patched armor, Haven-7 insignia |
| **Glow** | `assets/sprites/player_warden_1.png` | Glow variant — engine brightened, shield shimmer on hull, armor panels highlighted |

### Sprite Generation Prompts

#### Imagen 3 Prompt (used for existing sprites)

```
A 16-bit pixel art heavy armored escort spaceship sprite for a retro arcade shoot-em-up game.
Broad-shouldered angular design with orange (#ff6600) engine glow.
Visible patchwork armor plates in mismatched alloys — field-repaired look with scorch marks.
Bulkier than a sleek fighter, designed to tank and protect.
Navy insignia crudely painted over with a station logo.
Transparent background, 256x256 pixels, top-down orientation.
Pixel art with metallic shading, limited color palette, crisp edges.
Warm, industrial, stubborn personality.
```

#### Veo 3.1 Prompt (for future re-generation / higher fidelity)

```
16-bit retro sci-fi heavy escort starfighter sprite,
broad-shouldered angular armored bulk,
orange-amber (#ff6600) engine glow along reinforced wing roots,
visible patchwork armor plates in mismatched alloys with scorch marks,
Navy military insignia painted over with civilian station emblem,
point-defense grid turrets visible along hull edges,
warm industrial engine signature — not sleek, stubborn,
pixel art texture, transparent background,
256x256 sprite sheet frame, Darius Star game asset, top-down view,
survivor aesthetic — a ship that took hits and kept flying,
retro arcade shmup style, metallic shading
```

#### Glow Variant Adjustments

- Engine glow intensifies 40% (brighter orange)
- Shield shimmer overlay on hull panels
- Point-defense turret tips glow brighter
- Patchwork weld lines emit faint orange heat

### Color Reference

| Element | Hex | RGB |
|---------|-----|-----|
| Engine Glow | `#FF6600` | (255, 102, 0) |
| Armor Base | `#3a3a4a` | (58, 58, 74) |
| Patchwork Alloy A | `#5a5a6a` | (90, 90, 106) |
| Patchwork Alloy B | `#4a3a2a` | (74, 58, 42) |
| Scorch Marks | `#1a1a1a` | (26, 26, 26) |
| Haven-7 Logo (paint) | `#00cccc` | (0, 204, 204) |

---

## 4. INTEGRATION STATUS

### Existing Integrations ✅

| Integration | Status | Details |
|-------------|--------|---------|
| **Sprite Files** | ✅ Done | `player_warden_0.png`, `player_warden_1.png` in `assets/sprites/` |
| **Manifest** | ✅ Done | `sprites.json` has `player_warden` with 2 frames |
| **Ship Selection** | ✅ Done | `ship_select.html` has Warden card with lock/unlock system |
| **Backstory** | ✅ Done | Full 24-paragraph narrative in PLOT-GAPS-FILLED.md §2 |
| **Stats & Upgrades** | ✅ Done | Full stat table + 4-phase upgrade path in PLOT-GAPS-FILLED.md §2 |
| **Design Doc** | ✅ This File | Comprehensive standalone reference document |

### Pending Integrations

| Integration | Status | Notes |
|-------------|--------|-------|
| **Game index.html** | 🔲 Pending | Warden needs `playerWardenSprites` mapping and co-op player 2 slot |
| **Co-op mode** | 🔲 Pending | P2 ship selection, shared-screen Guardian Protocol overlay |
| **Naya dialogue system** | 🔲 Pending | Post-biome 6 reveal, biome 7-10 banter, Mother's Vow trigger dialogue |
| **Guardian Protocol VFX** | 🔲 Pending | Shield dome visual effect — 200m radius semi-transparent orange dome |
| **Point-Defense Grid VFX** | 🔲 Pending | Auto-targeting laser grid that shoots down nearby projectiles |

### Ship ID Convention

For game code references:
```
Ship ID:            'warden'
Sprite prefix:      'player_warden'
Manifest key:       'player_warden'
Unlock flag:        'dariusStar_forceUnlockWarden'
Unlock condition:   Complete biome 6 (Naya joins the crew)
```

---

## 5. GAMEPLAY DESIGN NOTES

### Co-op Role: Tank / Escort

In 2-player mode, Naya (P2) flies the Warden as a **tank/escort**. Her job is to protect Darius (P1 / Nyxa) while he does the heavy damage.

**Synergies with Nyxa:**
- Warden tanks aggro — draws enemy fire with Guardian Protocol
- Point-Defense Grid clears projectiles that would hit Nyxa
- Scavenger's Instinct benefits BOTH players (20% bonus scrap)
- Guardian Protocol's +15% shield recharge boosts Nyxa's regeneration
- Mother's Vow triggers when Lyra (the navigator) is threatened — both pilots feel the stakes

**Weaknesses:**
- Slow (6/10 speed) — can't outrun fast enemies or chase runners
- Lower DPS than Nyxa — relies on Darius for boss damage
- Guardian Protocol has long cooldown (90s) until Phase 2 upgrade

### Solo Mode

In solo mode, Naya can be selected as the player's ship instead of the Nyxa. The Warden trades speed and firepower for survivability and scrap income — a different playstyle that rewards methodical, thorough players.

### NG+ Carries Over

The Warden carries over to NG+ if unlocked in the previous run. Ship retains base stats but upgrades reset. NG+ scrap multiplier applies to Warden scrap collection as well.

---

## 6. DIALOGUE SAMPLES

### Post-Biome 6 — Joining the Crew

> **NAYA**: "I found something in the debris field. Navy prototype. They left it to rot. I fixed it."
>
> **DARIUS**: "Of course you did."
>
> **NAYA**: "I'm not staying behind anymore, Darius. I spent eighteen days in that graveyard thinking about you dying alone in the deep while I sat in a med-bay holding our daughter's hand. I'm a better pilot than half the Navy pilots who tried to kill me. I'm coming with you."
>
> **DARIUS**: "Welcome aboard, Lieutenant."

### During Combat (Guardian Protocol Activation)

> **NAYA**: "Dome up. Stay inside."

### During Combat (Warden Takes Heavy Fire)

> **NAYA**: "That all you've got? I've been hit harder by debris."

### To Lyra (Post-Biome 9 Reunion)

> **NAYA**: "You scared me, starlight. Don't do that again."
>
> **LYRA**: "I had to go deep, Mommy. But I came back."
>
> **NAYA**: "You always do. You're a Star."

### Mother's Vow Activation (Final Boss)

> **NAYA**: "You do NOT touch my daughter. Warden, override safeties — everything to weapons and shields. Now."

---

*Design document for GRO-948: Naya's Warden Ship — Design, Sprite & Backstory*
*Built from PLOT-GAPS-FILLED.md §2, ship-generation-prompts.md conventions, and existing sprite assets*
*Commit: GRO-947 was the prior doc (Lyra Navigator System)*

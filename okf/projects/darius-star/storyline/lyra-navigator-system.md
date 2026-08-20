---
type: Reference
title: "Darius Star — Lyra Navigator System"
description: "Detailed design doc for Lyra, the player's navigator character — dialogue system, contextual banter, story integration."
resource: okf/projects/darius-star/storyline/lyra-navigator-system.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/lyra-navigator-system.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/lyra-navigator-system.md"
migrated_from_repo: mbgulden/darius-star
---

# LYRA NAVIGATOR SYSTEM — Design Document

> **Status:** Design Complete — Awaiting Level System + Dialogue Engine
> **Source:** PLOT-GAPS-FILLED.md §1
> **Game:** Darius Star: Cyber Coelacanth (HTML5 Canvas)
> **Architecture:** Single-file index.html → will need module extraction
> **Date:** 2026-06-09

---

## 1. SYSTEM OVERVIEW

Lyra Star operates from the *Nyxa's* co-pilot seat via a neural-link chair. Her Dreamer attunement grants intuitive perception of safe routes through corrupted space. She provides three types of callouts during gameplay:

| Callout Type | Trigger | Player Impact |
|---|---|---|
| **Pathfinding** | Branching corridors, maze sections | Alternate route suggestion (often superior) |
| **Hazard Warning** | Incoming environmental danger | Preemptive dodge window (+1.5s warning) |
| **Alternate Route** | Hidden passages, Dreamer-tunnels | Secret paths — risk/reward (no radar, pure voice) |

### Core Mechanics

1. **Route Guidance UI**: Lyra's portrait appears in bottom-left HUD with reactive expression (neutral → urgent → relieved). Callout text appears as subtitle-style overlay beneath portrait.

2. **Trust Meter** (hidden stat, 0–100): Tracks how many times the player follows Lyra's advice vs. ignoring it. Affects:
   - Scene 3 (Ice Ring) tunnel accuracy — below 40 trust = foggy tunnel, more hazards
   - Scene 5 (Return) voice quality — below 50 trust = static interference on comms
   - Post-game narrative epilogue

3. **Coma State** (biomes 7–8): Lyra's portrait is greyed out with "NO SIGNAL" overlay. All callout systems disabled. HUD shows empty co-pilot chair icon. Gameplay difficulty spikes — no route guidance, no hazard warnings.

4. **Return State** (biome 9+): Portrait returns with blue Dreamer-vein glow. Voice has harmonic underlay (audio post-processing: +20% resonance, +10ms reverb). Navigation precision upgraded — callouts are 95% accurate (was 75%).

---

## 2. TECHNICAL ARCHITECTURE

### 2.1 Module Extraction Plan

Current game is single-file `index.html` (1233 lines). Navigator system requires extraction into:

```
darius-star/
├── index.html              # Game entry point (minimal harness)
├── js/
│   ├── game.js             # Core game loop, state machine
│   ├── player.js           # Player ship, weapons, shields
│   ├── enemies.js          # Enemy types, spawn patterns
│   ├── levels.js           # Biome definitions, wave sequencing
│   ├── navigator.js        # Lyra system (NEW)
│   ├── dialogue.js         # Dialogue engine (NEW)
│   ├── hud.js              # HUD rendering (portrait, callouts, trust)
│   └── audio.js            # Web Audio synthesis + voice stubs
├── data/
│   └── scenes/
│       ├── lyra-scene-1-abyssal-trench.json
│       ├── lyra-scene-2-coral-graveyard.json
│       ├── lyra-scene-3-ice-ring.json
│       ├── lyra-scene-4-storm-belt.json
│       └── lyra-scene-5-xenomorph-hive.json
└── docs/
    └── lyra-navigator-system.md  # This file
```

### 2.2 Navigator.js API

```javascript
// Core class
class LyraNavigator {
  constructor() {
    this.trust = 50;           // 0-100, starts neutral
    this.active = true;        // false during coma (biomes 7-8)
    this.returned = false;     // true after biome 9 awakening
    this.portraitState = 'neutral'; // neutral | urgent | relieved | coma | returned
    this.currentScene = null;
    this.sceneQueue = [];
    this.calloutCooldown = 0;  // prevents spam
  }

  // Call each frame
  update(dt, playerPos, biomeId, levelProgress) {
    if (!this.active) return;
    this.calloutCooldown -= dt;
    this.checkSceneTriggers(biomeId, levelProgress);
    this.checkHazardTriggers(playerPos, biomeId);
  }

  // Trigger a scene (cutscene mode — pauses gameplay)
  triggerScene(sceneId) { /* loads from data/scenes/lyra-scene-*.json */ }

  // Issue a callout (non-cutscene gameplay callout)
  issueCallout(type, text, routeData) { /* displays subtitle + triggers audio stub */ }

  // Trust adjustments
  followLyra()  { this.trust = Math.min(100, this.trust + 5); }
  ignoreLyra()  { this.trust = Math.max(0, this.trust - 3); }

  // State transitions
  enterComa()   { this.active = false; this.portraitState = 'coma'; }
  awaken()      { this.active = true; this.returned = true; this.portraitState = 'returned'; }
}
```

### 2.3 Dialogue Engine

```javascript
class DialogueEngine {
  constructor() {
    this.active = false;
    this.queue = [];
    this.currentLine = null;
    this.charIndex = 0;       // typewriter effect
    this.portraits = {};      // character portrait map
    this.onComplete = null;
  }

  loadScene(sceneJson) { /* populate this.queue from JSON */ }
  advance() { /* next line or close dialogue */ }
  render(ctx) { /* draw dialogue box + portrait + typewriter text */ }
}
```

### 2.4 Scene JSON Format

Each scene file is a JSON array of dialogue beats with trigger conditions:

```json
{
  "sceneId": "lyra-scene-1-abyssal-trench",
  "biomeId": 1,
  "title": "First Trust — Abyssal Trench",
  "triggerAt": "mid-level",           // "opening" | "mid-level" | "late-level" | "boss-defeated" | "chase"
  "triggerCondition": "player_enters_thermal_vents",
  "gameplayPause": true,              // freeze game during dialogue
  "beats": [
    {
      "speaker": "lyra",
      "portrait": "lyra_neutral",
      "text": "Daddy... don't go left. The vents — they're going to blow in sequence.",
      "duration": 4000,
      "audioStub": "proc_lyra_scene1_line1"
    },
    {
      "speaker": "thorne",
      "portrait": "thorne_comms",
      "text": "Darius, our thermal readings show the left channel is stable. Stay on course.",
      "duration": 3500,
      "audioStub": null
    }
    // ... more beats
  ],
  "choicePoint": {
    "afterBeat": 3,
    "options": [
      { "label": "Follow Thorne (left channel)", "outcome": "ignore_lyra", "trustDelta": -3 },
      { "label": "Trust Lyra (center channel)", "outcome": "follow_lyra", "trustDelta": +5 }
    ]
  },
  "routeData": {
    "safeRoute": "center",
    "hazardRoute": "left",
    "visualReward": "vent_blowout_background_spectacle"
  }
}
```

---

## 3. THE 5 SCENES — FULL DIALOGUE SCRIPTS

### 3.1 Scene 1: First Trust — Abyssal Trench (Biome 1, Mid-Level)

**Context:** Darius navigating thermal vent field. Conventional sonar scrambled. Thorne feeding standard Navy protocol.

**Characters:** DARIUS, LYRA, THORNE (comms)

**Pre-Scene Setup:**
- Player enters branching corridor: left channel (standard route), center channel (narrow, looks blocked)
- Thorne's HUD overlay says "STAY LEFT — THERMAL STABILITY"
- Lyra's portrait appears, expression: uncertain, small

**Dialogue Beats:**

```
BEAT 1 — Lyra's Warning
LYRA (lyra_neutral): "Daddy... don't go left. The vents — they're going to blow in sequence.
                     Left channel first, then right, then the center. If you go left
                     you'll be in the middle of it."

BEAT 2 — Thorne Counters
THORNE (thorne_comms): "Darius, our thermal readings show the left channel is stable.
                       Stay on course."

BEAT 3 — Choice Point
[GAMEPLAY UNPAUSES — Player chooses left or center channel]

IF PLAYER GOES LEFT:
  - Trust -3
  - Vent blowout triggers: screen shakes, damage (20HP), forced rightward dodge
  - THORNE: "Vent cascade! I'm reading five more — Darius, get clear!"
  - Player must dodge through 5 sequential vent eruptions
  - After surviving: DARIUS (to self): "Should have listened..."
  - Lyra's portrait: sad, silent
  - Scene ends. No reward.

IF PLAYER GOES CENTER:
  - Trust +5
  - Tight squeeze through basalt pillars — 15-second precision flying section
  - Behind player: left channel erupts in cascading vent blowout (visual spectacle)
  - LYRA (lyra_relieved): "The center opens up in about forty meters. There's a hidden
                          cave — precursor construction. You can slip through. I can...
                          I can feel the shape of it."
  - DARIUS (quietly): "Now what?"
  - LYRA: "Follow the blue glow. Not the bright one — the dim one, way down low.
           It's not trying to trick you."
  - Hidden cave opens, safe passage, bonus scrap pickup (+30 scrap)
  - Scene ends. DARIUS (to self): "She was right..."
```

**Design Notes:**
- First moment player understands Lyra is a mechanical navigator, not flavor
- Center route = harder flying but rewarded with spectacle + scrap
- Sets pattern: trusting Lyra = harder path, better rewards

---

### 3.2 Scene 2: The Impossible Route — Coral Graveyard (Biome 2, Late-Level)

**Context:** Memory Wraith boss defeated. Coral maze collapsing. 2-minute escape timer. All primary routes blocked.

**Characters:** DARIUS, LYRA, THORNE (comms)

**Pre-Scene Setup:**
- Boss defeated, screen shakes, "EVACUATE" warning flashes
- 120-second countdown starts
- Thorne's HUD: "CALCULATING ESCAPE VECTORS..." → "ALL ROUTES BLOCKED" (red)

**Dialogue Beats:**

```
BEAT 1 — Dead End
THORNE (thorne_comms): "All primary routes are sealed. I'm calculating secondary — "

BEAT 2 — The Impossible Call
LYRA (lyra_urgent): "Go down."
THORNE: "Negative, Lyra. Down is the substrate layer. Solid bedrock for three kilometers.
        There's nothing down there."
LYRA: "Not solid. Not anymore. The Dreamer... it dreamed through it. There's a vein.
       A hollow vein. Like a crack in a tooth. You can fit."
THORNE: "Darius, that's suicide. Our geological scans — "

BEAT 3 — Choice Point
DARIUS: "Lyra. How sure are you?"
LYRA (pause): "I can feel the water moving through it. It's real, Daddy. I promise."
[Player chooses: dive down / try lateral escape]

IF PLAYER GOES LATERAL:
  - Trust -5
  - 45 seconds of dodging collapsing coral — all dead ends
  - Timer runs to 30s, Lyra repeats: "Daddy, please. Go down."
  - Player forced to dive — but with less time and more debris

IF PLAYER DIVES:
  - Trust +5
  - Ship plunges toward solid rock → passes through Dreamer-membrane (visual: static shimmer)
  - Black tunnel with blue Dreamer-vein walls, 20-second guided flight (no enemies)
  - Ship bursts out into open water beyond collapse zone
  - DARIUS: "We're clear. Lyra... good call."
  - LYRA (small, proud): "I told you. I can feel the shape of things."
```

**Design Notes:**
- Establishes Lyra can perceive IMPOSSIBLE routes no instrument detects
- Player learns: when Lyra sounds insane, she's right
- Timer pressure makes trust decision mechanically tense
- Dreamer-membrane visual — key art moment for trailer

---

### 3.3 Scene 3: The Rescue — Ice Ring (Biome 5, Chase Sequence)

**Context:** Captain Cross + Squadron Umbra hunting Darius through Saturn's ice ring. Nyxa damaged (shields 30%). Cross herding him into a kill box.

**Characters:** DARIUS, LYRA, CROSS (enemy comms), THORNE (comms — panicked)

**Pre-Scene Setup:**
- Chase mode: forced rightward scroll at 1.3× speed
- 3 enemy squadrons converging (HUD shows converging triangles)
- Cross on open comms, taunting
- Thorne shouting intercept vectors (all lead to kill box)

**Dialogue Beats:**

```
BEAT 1 — Boxed In
CROSS (enemy comms, cold): "You're boxed, Star. Three squadrons converging on your
                            position. Surrender the components and I'll let you walk."

BEAT 2 — The Ice Shard
LYRA (urgent, cutting through): "Daddy — the ice shard at bearing 217. The big one,
                                 the one that looks like a broken tooth. Fly INTO it."
DARIUS: "Lyra, that's a solid ice mass. I'll pancake."
LYRA: "No. It's hollow. The Dreamer was here before — it dreamed a cavity inside.
       There's a tunnel network. It goes all the way through to the far side of the ring.
       I can see the whole path in my head, Daddy. Please."

BEAT 3 — The Dive
[Player must steer toward the ice shard — enemy fire intensifies as they approach]
[Trust < 40: tunnel is foggy, 3 environmental hazards inside]
[Trust >= 40: tunnel is clear, pure navigation sequence]

Darius banks hard. Cross's squadron opens fire. At the last moment — hidden fissure
opens, bioluminescent Dreamer-matter pulsing at its edges. Nyxa slides through.
Fissure seals behind. Torpedoes detonate harmlessly against ice.

BEAT 4 — The Tunnel (Pure Audio Navigation)
[Pitch black except faint blue Dreamer-veins. Player navigates by Lyra's voice alone.]

LYRA: "Left fork in twenty meters... now. Slow down for the next chamber — there's
       something resting in there, it's not awake yet, don't wake it up... okay,
       you're past. Right turn. Surface exit in three hundred meters. Cross is waiting
       on the far side but she doesn't know which exit you'll take. Pick the northern one."

DARIUS: "How many exits are there?"
LYRA: "Seven. She's covering three. I'll tell you which one she's not watching."

BEAT 5 — Emergence
[Player chooses exit — LYRA calls the unguarded one]
[Ship bursts out far side of ice ring. Cross's squadron visible in distance — wrong exit.]
DARIUS: "...You just outsmarted a Navy tactician."
LYRA (quiet, fierce): "She was going to hurt you."
```

**Design Notes:**
- Peak of Lyra-as-active-agent — she's outmaneuvering a military tactician
- Tunnel sequence: PURE audio navigation, zero visibility (showcase moment)
- Trust meter affects tunnel clarity — rewards players who trusted Lyra earlier
- 7-exit choice with Lyra's guidance — mechanical expression of trust arc

---

### 3.4 Scene 4: Silence — Storm Belt (Biome 7, Opening)

**Context:** Lyra unconscious after Navy attack. Selene's voice strained: "She's stable, but she's... not here, Darius." Storm Belt biome: gas giant, 5,000 mph winds, continuous lightning, 50m visibility.

**Characters:** DARIUS, THORNE (comms), SELENE (comms — brief)

**Pre-Scene Setup:**
- Briefing screen: no Lyra portrait. Dark neural-link station.
- HUD changes: co-pilot icon greyed out, "NO SIGNAL" text
- Thorne's briefing is grim and tactical

**Dialogue Beats:**

```
BEAT 1 — The Empty Chair
[Pre-mission. Cockpit view. Co-pilot chair is empty. Neural link station dark.]
DARIUS (reaches out, touches the dark console): "..."
[Brief flashback audio: Lyra's voice echoing faintly — "I can feel the shape of things"]
DARIUS (quietly): "Wake up soon, starlight. I don't know how to do this without you."

BEAT 2 — Thorne's Briefing
THORNE (comms, grim): "Without Lyra's navigation, we're flying standard instruments
                      through an environment where standard instruments are useless.
                      Wind shear will throw off your vector by hundreds of meters per
                      second. Lightning will fry your guidance systems. I can give you
                      waypoints, but between them... you're on your own, Darius."

BEAT 3 — The Silence Begins
[Mission starts. Differences from normal gameplay:]
- No route guidance callouts
- No hazard warnings (enemies appear without warning)
- Compass bearing only — no suggested path
- Enemy encounters 40% harder to predict
- Environmental hazards (lightning strikes, wind shear) come without warning

BEAT 4 — The Habit
[At 3 random points during biome 7, triggered by near-miss hazards:]
DARIUS (muttering, half-habit): "Which way, Lyra?"
[No response. Static. Wind howl.]
[Dialogue box stays empty for 3 seconds — the silence IS the beat.]

BEAT 5 — A Glimmer
[At biome 7 midpoint, passing through a rare calm pocket:]
[Lyra's portrait flickers for 0.5s — eyes closed, face peaceful — then gone]
SELENE (comms, briefly): "Darius — I saw a spike on Lyra's neural monitor. Just for a
                         second. She's still in there. She's fighting."
```

**Design Notes:**
- "Show don't tell" for how essential Lyra has become
- Mechanical difficulty spike = emotional loss
- The silence IS the content — Lyra's absence is the scene
- Flicker at midpoint gives hope without resolution
- Storm Belt environmental hazards: lightning strike (instant 30HP), wind shear (forced drift), zero-visibility pockets

---

### 3.5 Scene 5: Return — Xenomorph Hive (Biome 9, Opening)

**Context:** Lyra awakens. Her voice has changed — harmonic underlay, Dreamer resonance. Navigation upgraded to near-prescient. But her voice sometimes speaks in rhythms that aren't quite human.

**Characters:** DARIUS, LYRA (returned), SELENE (comms — brief)

**Pre-Scene Setup:**
- Biome 9 briefing screen: Lyra's portrait BACK — but different. Blue Dreamer-vein glow at temples. Expression: calm, distant, powerful.
- HUD: co-pilot icon active, blue glow aura
- Selene explains: "She fought her way back herself. Her connection to the Dreamer is stronger than ever. She's... more than she was."

**Dialogue Beats:**

```
BEAT 1 — The Voice
[Static crackle. Then — a voice. Layered, resonant, the old Lyra with something beneath.]
LYRA (returned): "...Daddy?"
DARIUS (sharp breath): "Lyra. You're awake."
LYRA: "I had to go deep to come back. I saw... I saw everything. The Dreamer isn't
       trying to hurt us. It's trapped in a loop of its own fear. Like... like a whale
       tangled in a net, thrashing, and we're the plankton caught in the current."
DARIUS: "Are you... are you okay?"
LYRA (pause): "I'm different. But I'm still me. I promise."

BEAT 2 — The Warning
LYRA: "I can still see the paths, Daddy. Better than before. The Hive is... it's going
       to try to confuse you. It'll show you routes that look safe. They're traps.
       Let me guide you. Please."

BEAT 3 — No Hesitation
[No choice point. No pause. Darius doesn't even breathe before answering.]
DARIUS: "Tell me where to go."
[Trust meter instantly locks at 100 — no further trust adjustments for rest of game]

BEAT 4 — The First Return Callout
[Mission starts. Lyra's first callout — her voice has changed audio treatment:]
LYRA (returned, layered): "The left passage is a lie. The Hive wants you to take it.
                           Go right — through the acid-weeping wall. It'll burn your
                           shields but it won't kill you. The left passage will."

BEAT 5 — The Rhythm
[At a quiet moment mid-level:]
DARIUS: "Your voice sounds different."
LYRA: "I hear things differently now. The Dreamer's... song. It's not a song, exactly.
       More like... the sound of continents thinking. I can filter it. Most of the time."
DARIUS: "And when you can't?"
LYRA (pause): "Then I'll tell you. I promise I'll tell you."
```

**Design Notes:**
- Trust arc completion: no hesitation, no choice point — earned through 5 biomes of bonding
- Voice audio treatment changes: +20% resonance, +10ms pre-delay reverb, subtle harmonic layer
- Returned navigation: 95% accuracy (was 75%), callouts arrive BEFORE hazard visual cues
- The biome-boss fight (Xenomorph Queen) features Lyra calling weak points in real-time

---

## 4. COMA MECHANIC SPEC (Biomes 7–8)

### 4.1 Trigger

- End of biome 6 (Fire Nebula): Navy attacks Haven-7
- Cutscene: Lyra exposed to experimental attunement accelerator
- Selene: "She's stable, but she's... not here, Darius. Whatever that device did, it pushed her too deep."
- Lyra's portrait fades to grey. "NO SIGNAL" overlay appears.

### 4.2 Gameplay Changes (Biomes 7–8)

| System | Normal (Biomes 1–6) | Coma (Biomes 7–8) |
|---|---|---|
| Route callouts | Active (Lyra suggests routes) | Disabled (compass only) |
| Hazard warnings | +1.5s preemptive alert | Disabled (no warning) |
| HUD portrait | Lyra neutral/urgent/relieved | Greyed out + "NO SIGNAL" |
| Enemy predictability | Normal spawn patterns | +40% random spawn variance |
| Environmental hazards | Telegraph before hit | No telegraph — instant |
| Trust meter | Adjusts with choices | Frozen (no Lyra to trust) |

### 4.3 Emotional Design Beats

- **Empty chair visual**: Co-pilot icon replaced with empty chair silhouette
- **Habit lines**: Darius mutters "Which way, Lyra?" at hazard points — silence answers
- **Midpoint flicker** (biome 7 midpoint): Portrait flickers 0.5s, Selene reports neural spike
- **End of biome 8**: Faint static crackle on comms — first sign of return

### 4.4 Recovery Trigger

- Beginning of biome 9: Lyra awakens
- Full cutscene (Scene 5 above)
- Portrait returns with blue glow
- Trust meter unlocked and set to 100 (no more trust tracking)
- Navigation upgrades to "Returned" stats

---

## 5. IMPLEMENTATION PHASES

### Phase 1: Foundation (current architecture → modular)
- [ ] Extract `index.html` into `js/` modules (game.js, player.js, enemies.js, hud.js)
- [ ] Add HUD portrait rendering (bottom-left position, 64×64px, reactive expressions)
- [ ] Add subtitle overlay system beneath portrait (max 2 lines, typewriter effect)
- [ ] Define `LyraNavigator` class skeleton and `DialogueEngine` class skeleton

### Phase 2: Navigator Core
- [ ] Implement callout system (pathfinding, hazard, alternate route types)
- [ ] Implement trust meter (hidden, 0–100, adjustments on follow/ignore)
- [ ] Implement portrait state machine (neutral, urgent, relieved, coma, returned)
- [ ] Implement coma state (biomes 7–8 trigger, all systems disabled, empty chair icon)
- [ ] Implement return state (biome 9+, blue glow, upgraded accuracy)

### Phase 3: Scenes
- [ ] Build 5 scene JSON files (data/scenes/lyra-scene-*.json)
- [ ] Implement scene trigger system (proximity, progress, boss-defeat triggers)
- [ ] Implement dialogue engine (typewriter text, portrait switching, audio stubs)
- [ ] Implement choice points (Scene 1: left vs. center, Scene 2: dive vs. lateral, Scene 3: tunnel path)

### Phase 4: Integration
- [ ] Wire scenes into level progression (biome 1 mid, biome 2 late, biome 5 chase, biome 7 open, biome 9 open)
- [ ] Implement Scene 3 audio-only tunnel sequence
- [ ] Implement Scene 4 silence mechanics (no callouts, random habit lines, midpoint flicker)
- [ ] Audio treatment for returned Lyra voice (resonance + reverb + harmonic underlay)
- [ ] Playtest all 5 scenes for timing, difficulty balance, emotional impact

### Phase 5: Polish
- [ ] Trust meter visual feedback (subtle HUD element — maybe visible on pause screen only)
- [ ] Lyra portrait animation (blinking, expression transitions)
- [ ] Dreamer-vein visual effects on returned portrait
- [ ] Audio stubs for all Lyra lines (placeholder TTS → voice actor)

---

## 6. RISKS & DEPENDENCIES

| Risk | Mitigation |
|---|---|
| Single-file architecture can't support dialogue system | Phase 1 extraction must happen first — OR build navigator as inline module within index.html |
| No level/biome system exists yet | Navigator system designed to work with ANY level implementation — callouts are trigger-based, not level-system-dependent |
| Voice acting not available | All dialogue designed as text-first, audio stubs for placeholder TTS (Gemini TTS Pipeline — see GRO-951) |
| Scene 3 tunnel sequence (audio-only) needs precise level design | Tunnel is a straight corridor with audio cues — minimal level geometry, maximum atmospheric impact |

---

## 7. RELATED LINEAR ISSUES

| Issue | Title | Relationship |
|---|---|---|
| GRO-947 | Lyra Navigator System (this doc) | Design spec |
| GRO-948 | Naya's Warden Ship | Sister character arc |
| GRO-949 | Biome 3 Embryo Fix | Boss-lure alignment with Lyra's Dreamer perception |
| GRO-950 | Scrap Narrative | Father-daughter emotional stakes |
| GRO-951 | Gemini TTS Voice Pipeline | Voice generation for Lyra callouts |
| GRO-952 | Voice Post-Processing | Fighter-pilot FX chain — applies to returned Lyra voice treatment |
| GRO-956 | HUD Chrome & UI Design System | Portrait + subtitle rendering |
| GRO-957 | Banter System | Lyra's context-aware callouts integrate with banter engine |

---

*Document complete. Ready for implementation when level system and dialogue engine are built. Scene JSON files can be generated directly from the dialogue scripts in Section 3.*

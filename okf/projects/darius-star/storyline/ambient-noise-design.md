---
type: Reference
title: "Darius Star — Ambient Noise Design"
description: "Comprehensive ambient sound design — biome-specific atmospheres, dynamic layering, adaptive mixing."
resource: okf/projects/darius-star/storyline/ambient-noise-design.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/ambient-noise-design.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/ambient-noise-design.md"
migrated_from_repo: mbgulden/darius-star
---

# Ambient Noise Design — Story-Driven Environmental Sound
## Darius Star: Cyber Coelacanth — 20 Layers (2 per Biome)

> "Show, don't tell" — environmental noise should tell the story.
> Each layer reveals something about what happened here.
> Mixed under music at 15% per SFX Cohesion Strategy.

---

## Mixing Guidelines

Per `docs/sfx-cohesion-strategy.md`:

| Layer | Volume | Purpose |
|-------|--------|---------|
| Music | 40% | Primary emotional driver |
| SFX | 70% | Gameplay feedback |
| Ambient A (Atmosphere) | 15% | Environmental immersion |
| Ambient B (Narrative) | 15% | Story told through sound |

Both ambient layers duck -3dB when music intensity peaks or critical SFX play.

---

## Biome 1: ABYSSAL TRENCH — "Peaceful Deep Ocean Until You Notice the Machinery"

**Story Context:** Darius descends to his grandfather's final dive site. The Guardian Coelacanth waits — mostly dead, but it recognizes Aldric's genetic signature and speaks in his voice.

### Layer A — atmosphere_b1_abyssal (`ambient_b1_atmosphere.wav`)
**Role:** Base immersion — the crushing dark.
**Sound:** Ultra-low frequency pressure drone (40-80 Hz), distant hydrothermal vent rumbles, water column silence with occasional bioluminescent crackle. Feels vast, ancient, indifferent. Low-pass filtered at 800 Hz — this layer lives entirely in the sub/mid range.
**Duration:** 60s seamless loop

### Layer B — narrative_b1_machinery (`ambient_b1_narrative.wav`)
**Role:** Show-don't-tell: something ancient is still active down here.
**Sound:** Starts as peaceful deep ocean silence. At 15s, a faint mechanical heartbeat becomes audible — the Guardian Coelacanth's dormant systems. At 30s, ghostly neural static flickers (Aldric's recorded voice patterns, fragmented beyond recognition — just the *texture* of a human voice trying to speak through machine decay). At 45s, a single clear mechanical groan — the Guardian shifting in its sleep. Then back to apparent silence… but now the listener knows the machinery is there.
**Duration:** 60s loop (the "reveal" happens once per loop; on repeat plays the machinery is audible from the start — mirroring the player's knowledge)

---

## Biome 2: CORAL GRAVEYARD — "The Ghosts of an Extinct Reef"

**Story Context:** A precursor colony deliberately destroyed to hide something. Darius discovers a memory-vault and experiences the precursors' grief.

### Layer A — atmosphere_b2_coral (`ambient_b2_atmosphere.wav`)
**Role:** Base immersion — warm, shallow, dead.
**Sound:** Gentle water movement through hollow coral structures, occasional creak of ossified reef, marine silence where there should be life. Mid-frequency resonance from water moving through maze-like coral architecture. No biological sounds — the absence IS the sound.
**Duration:** 60s seamless loop

### Layer B — narrative_b2_memories (`ambient_b2_narrative.wav`)
**Role:** The reef remembers what it lost.
**Sound:** Fragments of extinct species calls — half-material memory-echoes rendered as distorted chime-like tones. At 20s, a swell of overlapping precursor voices (filtered to sound like coral resonance, not speech — think whale song processed through crystal). At 40s, a sharp coral collapse sound — the reef still crumbling, still dying. Between events: eerie reef silence with subtle harmonic overtones (the memory-vault's residual energy).
**Duration:** 60s loop

---

## Biome 3: COELACANTH LAIR — "Unhatched Things in the Ice"

**Story Context:** A birthing ground for Coelacanth entities. One was killed from the inside by something that shouldn't exist in a biosynthetic entity. Ophion's hidden laboratory.

### Layer A — atmosphere_b3_lair (`ambient_b3_atmosphere.wav`)
**Role:** Base immersion — near-freezing, claustrophobic, wet.
**Sound:** Cryo-volcanic vent hissing, ice cracking under pressure, water dripping in cavernous space. The acoustics of ice caves — every sound has a sharp, brittle reverb. Temperature feels audible: cold that makes metal contract.
**Duration:** 60s seamless loop

### Layer B — narrative_b3_embryos (`ambient_b3_narrative.wav`)
**Role:** Something was born here that shouldn't exist.
**Sound:** Wet, organic pulsing — embryonic fragments twitching in stasis. At 15s, a distorted Coelacanth birthing cry (pitched down, reversed, layered with static — sounds wrong, biological-but-mechanical). At 35s, Ophion's laboratory equipment hum — ancient precursor tech still running, its power cycling in irregular patterns (the sabotage). At 50s, a single clear heartbeat from within a sealed containment unit — something is still alive in here.
**Duration:** 60s loop

---

## Biome 4: NEBULA DRIFT — "The Dreamer's Idle Thoughts"

**Story Context:** A sentient nebula. The Dreamer makes first contact — not as attack, but as communication attempt. It shows Darius his own memories.

### Layer A — atmosphere_b4_nebula (`ambient_b4_atmosphere.wav`)
**Role:** Base immersion — disorienting, vast, thought-responsive.
**Sound:** Shifting ionized gas tones, subtle spatial audio panning (sounds that seem to move when you're not paying attention), gravitational waves as low-frequency sweeps. The nebula's diffuse consciousness manifests as harmonic drones that shift key unpredictably — stable enough to be ambient, unstable enough to feel alien.
**Duration:** 60s seamless loop

### Layer B — narrative_b4_thoughts (`ambient_b4_narrative.wav`)
**Role:** The Dreamer is curious about Darius. It's showing him his own past.
**Sound:** Memory fragments rendered as sound — a child's laughter (Lyra, filtered through nebula acoustics — recognizable as human but distorted as if heard through gas), a woman's voice saying his name (Naya, just the one word, echoing), the sound of a pressure seal closing (Aldric's dive suit). At 30s, the Dreamer's "voice" attempts speech — not words, but tones that *almost* resolve into language, like a radio scanning for a station. At 50s, a deep, resonant note of loneliness — the Dreamer expressing its isolation in a frequency humans can feel but not hear consciously.
**Duration:** 60s loop

---

## Biome 5: ICE RING — "Frozen Silence Broken by Cracking Ice"

**Story Context:** A shattered ice moon in Saturn's rings. Squadron Umbra intercepts Darius. Captain Cross delivers her ultimatum.

### Layer A — atmosphere_b5_ice (`ambient_b5_atmosphere.wav`)
**Role:** Base immersion — frozen, vacuum-edged, crystalline.
**Sound:** Near-total silence punctuated by sharp ice cracks. Zero-G acoustics — sounds transmit through physical contact more than air (thin, brittle, close-mic'd texture). Occasional ice shard collisions create glassy harmonic rings. The "silence" here is different from biome 1 — it's cold silence, not pressure silence.
**Duration:** 60s seamless loop

### Layer B — narrative_b5_pursuit (`ambient_b5_narrative.wav`)
**Role:** The Navy is here. Trust is breaking.
**Sound:** Fragmented Navy comms — encrypted bursts of static that almost form words (military chatter, unreadable but urgent). At 15s, a ship's engine scream cutting through the ice field. At 25s, Cross's voice — a single clear line: "Stand down, Star." (filtered through comms static, authoritative but not cruel). At 40s, ice shattering under weapons fire — the fight is happening somewhere nearby. At 55s, a moment of tense silence — then a single ice crack, closer this time.
**Duration:** 60s loop

---

## Biome 6: FIRE NEBULA — "She's Speaking in the Dreamer's Voice"

**Story Context:** The Forge-Mind broadcasts the Dreamer's signal. Lyra begins to change. The midpoint crisis.

### Layer A — atmosphere_b6_inferno (`ambient_b6_atmosphere.wav`)
**Role:** Base immersion — superheated, molten, consuming.
**Sound:** Plasma flow rumble (low-mid continuous), superheated gas hissing, furnace-like ambience. Occasional flare bursts — sharp sizzle as new plasma jets ignite. The sound of an environment that would kill you instantly without protection. Heat distortion in audio form — slight pitch waver from thermal turbulence.
**Duration:** 60s seamless loop

### Layer B — narrative_b6_lyra (`ambient_b6_narrative.wav`)
**Role:** The daughter is becoming the bridge.
**Sound:** Lyra's voice, distorted — a child speaking words she didn't learn from humans. At 10s: "Daddy…" (clear, scared, young). At 25s: "…the thing in the dark isn't angry. It's scared." (her voice layered with a deeper resonance — the Dreamer's undertone). At 40s: "It's been alone for so long." (her voice now doubled — Lyra AND something vast speaking the same words). At 55s: a heartbeat — human rhythm but impossibly deep, felt more than heard. Between these: plasma crackle, the Forge-Mind's broadcast signal pulsing like a second heartbeat.
**Duration:** 60s loop

---

## Biome 7: STORM BELT — "The Storm-Singer Weeps as It Fights"

**Story Context:** A Coelacanth driven mad by centuries alone in the storm. It achieves clarity at the end, transfers Ophion's AI construct, and chooses death with dignity.

### Layer A — atmosphere_b7_storm (`ambient_b7_atmosphere.wav`)
**Role:** Base immersion — eternal hurricane, lightning-chained.
**Sound:** Continuous wind roar (layered — high whistle + low howl), lightning strikes in chains (crack → rumble → crack → rumble without gap), atmospheric pressure shifts as sub-bass fluctuations. The eye of the hurricane provides occasional moments of eerie calm within the loop. 5,000 mph winds rendered as white noise with tonal peaks.
**Duration:** 60s seamless loop

### Layer B — narrative_b7_singer (`ambient_b7_narrative.wav`)
**Role:** Madness, grief, and the choice to die sane.
**Sound:** The Storm-Singer's weeping — not human crying, but a Coelacanth's distress call, processed through hurricane acoustics (pitched wail, rising and falling with wind gusts). At 15s, fragments of its broken speech: "He was right… Ophion was right… the Dreamer only wants… only wants someone to listen…" (words barely audible through storm noise — the player strains to hear them). At 35s, the eye-of-the-storm moment: sudden near-silence, a single clear tone of lucidity. At 45s, the Storm-Singer's final transmission — a data burst rendered as ascending chime sequence (Ophion's AI being transferred). At 55s, the Singer goes silent. The storm continues without it.
**Duration:** 60s loop

---

## Biome 8: DERELICT FLEET — "Ghost Ship Creaks That Sound Like Voices"

**Story Context:** Abandoned Navy armada. Project Dream-Weapon's origin. Admiral Crane's psychic echo still haunts the flagship. Darius learns his bloodline was engineered.

### Layer A — atmosphere_b8_derelict (`ambient_b8_atmosphere.wav`)
**Role:** Base immersion — military graveyard, haunted by hardware.
**Sound:** Metal groaning in vacuum — hulls contracting, bulkheads settling, the slow death of warships. Occasional automated system beeps (still running after decades — life support failing, navigation computers stuck in loops). Distant impacts — debris colliding with derelict hulls. No engine sounds. No voices. Just the machines, slowly dying.
**Duration:** 60s seamless loop

### Layer B — narrative_b8_ghosts (`ambient_b8_narrative.wav`)
**Role:** The crew never fully left.
**Sound:** Psychic echoes — voices that sound almost human. At 10s, a faint ship-wide alarm from decades ago (the containment breach — muffled, like hearing it through water). At 20s, crew voices bleeding through — not words, just the *texture* of panic and confusion, layered and reverbed until it sounds like wind through a hull breach. At 35s, Admiral Crane's echo — a deep, resonant whisper: "The sacrifice… was necessary…" (spoken with the conviction of a patriot, not a villain). At 50s, a sharp metallic SCREAM — a ship's frame finally giving way after decades, but the timing makes it sound like a voice. The line between creak and scream is deliberately blurred.
**Duration:** 60s loop

---

## Biome 9: XENOMORPH HIVE — "The Temptation of Peace"

**Story Context:** A fully Dreamed world. The Hive offers Darius everything: Lyra alive, transformed but happy. An end to all struggle. He nearly accepts.

### Layer A — atmosphere_b9_hive (`ambient_b9_atmosphere.wav`)
**Role:** Base immersion — alive, aware, welcoming.
**Sound:** Organic breathing — the Hive itself respiring (slow, wet, warm — unsettling but not threatening). Flesh surfaces shifting with soft, sticky sounds. The environment hums with a biological resonance — like standing inside a giant sleeping creature. Impossible geometry represented by sounds that don't quite localize correctly (spatial audio tricks — drones that seem to come from everywhere and nowhere simultaneously).
**Duration:** 60s seamless loop

### Layer B — narrative_b9_temptation (`ambient_b9_narrative.wav`)
**Role:** Give up. It's so easy. She'll be safe.
**Sound:** The Hive's seductive voice — not words, but a harmonic choir that feels like warmth spreading through your chest. At 15s, Lyra's laughter — healthy, happy, echoing through the Hive (the promise: she lives here, transformed but joyful). At 30s, Naya's voice: "Darius… we can stop running…" (tender, exhausted, hopeful). At 45s, the Dreamer's chorus swells — dozens of absorbed consciousnesses singing in unity, offering peace. At 55s, a single dissonant note — the memory of Marcus's warning: "The easy path is always a trap" (not spoken — rendered as a sharp, clarifying tone that cuts through the warmth). The temptation is beautiful. Rejecting it hurts.
**Duration:** 60s loop

---

## Biome 10: CORE RIFT — "The Dreamer Speaks"

**Story Context:** The final threshold. The Prime Coelacanth at the event horizon. The Dreamer speaks directly for the first time. The Choice.

### Layer A — atmosphere_b10_core (`ambient_b10_atmosphere.wav`)
**Role:** Base immersion — reality's edge, existence as suggestion.
**Sound:** Gravitational waves as sub-bass sweeps (40 Hz descending to 20 Hz — felt, not heard), space-time distortion rendered as microtonal pitch bends, the event horizon's "sound" — a constant low hum that seems to come from inside your own skull. Occasional reality "tears" — brief moments where audio inverts or phases in impossible ways (the Dreamer's proximity warping physics). The most alien of all the atmospheres — this is not a place humans were meant to perceive.
**Duration:** 60s seamless loop

### Layer B — narrative_b10_dreamer (`ambient_b10_narrative.wav`)
**Role:** The god speaks. The choice crystallizes.
**Sound:** The Dreamer's voice — the sound of continental drift, of deep ocean currents, of the slow breathing of worlds. Not a voice in any human sense — a deep, resonant pulse that your bones interpret as language. At 15s: "I do not wish to destroy." (rendered as a harmonic convergence — tones aligning into meaning). At 30s: "I wish to no longer be alone." (the loneliness in its voice is overwhelming — a sound so sad it makes the Core Rift feel small). At 45s: the Prime Coelacanth's dying algorithm — a rapid sequence of machine-language clicks and tones (its final transmission, delivering the last compound data). At 55s: silence. Just the event horizon hum. The Choice hangs in that silence.
**Duration:** 60s loop

---

## File Naming & Organization

```
assets/audio/ambient/
├── ambient_b1_atmosphere.wav    # Biome 1: Abyssal Trench — base
├── ambient_b1_narrative.wav     # Biome 1: Abyssal Trench — story
├── ambient_b2_atmosphere.wav    # Biome 2: Coral Graveyard — base
├── ambient_b2_narrative.wav     # Biome 2: Coral Graveyard — story
├── ambient_b3_atmosphere.wav    # Biome 3: Coelacanth Lair — base
├── ambient_b3_narrative.wav     # Biome 3: Coelacanth Lair — story
├── ambient_b4_atmosphere.wav    # Biome 4: Nebula Drift — base
├── ambient_b4_narrative.wav     # Biome 4: Nebula Drift — story
├── ambient_b5_atmosphere.wav    # Biome 5: Ice Ring — base
├── ambient_b5_narrative.wav     # Biome 5: Ice Ring — story
├── ambient_b6_atmosphere.wav    # Biome 6: Fire Nebula — base
├── ambient_b6_narrative.wav     # Biome 6: Fire Nebula — story
├── ambient_b7_atmosphere.wav    # Biome 7: Storm Belt — base
├── ambient_b7_narrative.wav     # Biome 7: Storm Belt — story
├── ambient_b8_atmosphere.wav    # Biome 8: Derelict Fleet — base
├── ambient_b8_narrative.wav     # Biome 8: Derelict Fleet — story
├── ambient_b9_atmosphere.wav    # Biome 9: Xenomorph Hive — base
├── ambient_b9_narrative.wav     # Biome 9: Xenomorph Hive — story
├── ambient_b10_atmosphere.wav   # Biome 10: Core Rift — base
└── ambient_b10_narrative.wav    # Biome 10: Core Rift — story
```

---

## SFX Cohesion Compliance

All 20 layers follow `docs/sfx-cohesion-strategy.md`:

- **Palette**: 16-bit Sega Genesis retro arcade aesthetic — synthesized/chip-timbre where possible, warm low-end, bright 3-8kHz presence
- **No sub-bass below 60Hz** — highpass at 60Hz for period-appropriate sound
- **No long reverb tails** — space has no "room"
- **No cinematic braaams or orchestral elements**
- **Post-processing chain**: highpass(60Hz) → peak limit(-3dB) → normalize(-16 LUFS) → fade out(5ms)
- **In-game mixing**: ambient layers at 15% volume, duck -3dB when music peaks

## Regeneration Notes

These WAV files are **procedurally generated placeholders**. They establish the structure, duration, and sonic concept. For production quality, regenerate each layer via:

1. **Veo 3.1** (with synchronized audio prompts) — best for layers with specific event timing (narrative layers)
2. **Lyria 2/3** — best for sustained atmospheric drones (atmosphere layers)
3. **Procedural synthesis** (Pydub/Wave) — acceptable for simple drone layers

Regeneration prompts are cataloged in `veo_client.py` under the `VEO_ASSET_CATALOG` dictionary with prefix `ambient_b*_`.

---

*End of Ambient Noise Design — 20 Layers for 10 Biomes*
*Designed per SFX Cohesion Strategy v1. Mixed at 15% under music.*

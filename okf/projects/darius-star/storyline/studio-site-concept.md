---
type: Reference
title: "Darius Star — Studio Site Concept"
description: "Concept for the public-facing studio site — branding, content strategy, player community features."
resource: okf/projects/darius-star/storyline/studio-site-concept.md
tags: [darius-star, storyline, game-design, narrative, world-building]
timestamp: 2026-06-19T12:18:41Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/studio-site-concept.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "darius-star/docs/studio-site-concept.md"
migrated_from_repo: mbgulden/darius-star
---

# What An Adventure Games — Studio Site Concept

**Version:** 1.0  
**Domain:** whatanadventure.games  
**Status:** Design Research — zero code  
**Author:** Ned (Executor Agent)  
**Date:** June 2026  
**Source:** GRO-1114 — Studio site concept brief

---

## Table of Contents
1. [Brand DNA](#1-brand-dna)
2. [Site Structure](#2-site-structure)
3. [Visual Direction](#3-visual-direction)
4. [Content Strategy](#4-content-strategy)
5. [Call-to-Action Flow](#5-call-to-action-flow)
6. [Technical Notes](#6-technical-notes)

---

## 1. Brand DNA

### Studio Identity
**What An Adventure Games** is an indie retro-game studio built around a single ethos: *find the value in the wreckage*. The studio's name evokes the wide-eyed thrill of discovery — the moment you push through a door, descend into the deep, or power up a derelict console and find something extraordinary waiting.

### Core Pillars
| Pillar | Meaning |
|---|---|
| **Scrapper Spirit** | Resourceful, resilient, making something from nothing. The studio ships games, not promises. |
| **Deep Narrative** | Every game has a story worth telling — characters with arcs, worlds with history. |
| **Retro Craft** | 16-bit pixel art, chiptune audio, scanlines and CRT glow. Earnest homage, not irony. |
| **Accessible Challenge** | Tough but fair. The Pull-Out Mechanic (no death, just setback) embodies this. |

### Tone of Voice
- **Earnest**, never cynical
- **Direct**, like a crew briefing over comms
- **Warm**, like someone who's been in the trenches and has your back
- **Hopeful**, even in the dark — 75% positive, 25% urgent
- PG-rated. No profanity, no sarcasm, no cruelty.

### Key Phrases
- *"One-in-a-million."* — the scrapper's philosophy
- *"Push. Move. Go."* — Darius Star action verbs
- *"What An Adventure."* — the studio name is its own tagline
- *"Find what's waiting in the deep."* — thematic anchor

---

## 2. Site Structure

The site is a **single-page experience with anchor sections** plus one sub-page for the game detail. Think of it as a scrolling "transmission log" — each section is a distinct screen you scroll through, like flipping channels on a scrapper's console.

### Page Map

```
whatanadventure.games/
├── /                    → Studio landing (single-page scroll)
│   ├── Hero / Splash
│   ├── The Game        → Darius Star: Cyber Coelacanth overview
│   ├── The World       → Biomes, characters, lore teaser
│   ├── The Crew        → About the studio (Michael + team)
│   ├── Transmissions   → Devlog / news / patch notes
│   └── Dock            → Footer: socials, newsletter, legal
│
└── /darius-star/       → The game itself (existing, live)
```

### Section Details

#### 2.1 Hero / Splash (`#hero`)
- **What it is**: The first thing a visitor sees. Instant vibe-establishment.
- **Content**: Studio logo mark, title "WHAT AN ADVENTURE GAMES", subtitle "Independent Retro Arcade Studio", parallax background of stars/debris/salvage drifting slowly.
- **CTA**: "DIVE IN" button scrolls to The Game section.
- **Mood**: Dark void, faint scanlines, a single cyan glow pulsing — like a distress beacon in the black.

#### 2.2 The Game (`#the-game`)
- **What it is**: Darius Star showcase. The flagship — this is why you're here.
- **Content**:
  - Game title lockup: "DARIUS STAR: CYBER COELACANTH"
  - Tagline: *"Push. Move. Go."*
  - 3-4 gameplay screenshots in a "scanner" carousel (scanline overlay, glitch transitions)
  - Elevator pitch paragraph
  - Feature bullets: 10 biomes × 10 levels, 5 playable ships, 4-player local co-op, Web Audio synth engine, scrap economy, NG+
  - Mini ship showcase — the 5 ship silhouettes with callsigns
- **CTA**: "PLAY NOW" → links to /darius-star/

#### 2.3 The World (`#the-world`)
- **What it is**: Lore and universe teaser. Sell the depth.
- **Content**:
  - Biome map visual (10 nodes connected by a dive path, each pulsing with its signature color)
  - Character portrait grid: Darius Star, Naya Warden, Lyra Navigator — each with 1-line bio
  - Quote pull: a standout banter line ("*One-in-a-million, starlight.*")
  - "Explore the deep" — narrative hook copy
- **CTA**: Newsletter signup for lore drops

#### 2.4 The Crew (`#the-crew`)
- **What it is**: About the studio. Personal, scrappy, real.
- **Content**:
  - Studio origin story (2-3 paragraphs — the scrappy indie dev narrative)
  - Michael's role: Founder, Designer, Developer
  - "Built with" tech stack nod (Canvas API, Web Audio, Cloudflare, vanilla JS)
  - Photo/avatar of Michael (optional, use the scrapper helmet silhouette as placeholder)
- **CTA**: "Follow the build" → social links

#### 2.5 Transmissions (`#transmissions`)
- **What it is**: Devlog / news feed. Think "incoming comms."
- **Content**:
  - 3-5 latest entries (manual updates, patch notes, behind-the-scenes)
  - Each entry: date, title, short excerpt, "READ" link
  - Styled as terminal log entries with timestamp prefix
- **CTA**: "All transmissions" → either scroll to load more or a dedicated /log page later

#### 2.6 Dock (`#dock`)
- **What it is**: Footer. Where to find the studio elsewhere.
- **Content**:
  - Social icons: Twitter/X, Discord, YouTube, GitHub, itch.io (as applicable)
  - Newsletter embed (single email field + "HAIL" submit button)
  - Copyright: "© 2026 What An Adventure Games. Salvaged with care."
  - Tiny credit: "Built on scrap and coffee."

---

## 3. Visual Direction

### 3.1 Design System Name
**"Scrapper Console"** — a gritty, functional terminal aesthetic filtered through a 16-bit arcade lens. Think: the interface of a salvaged deep-sea nav computer, repurposed to browse the web.

### 3.2 Color Palette

| Token | Hex | Role |
|---|---|---|
| **Void Black** | `#050510` | Page background, deepest layer |
| **Abyss Navy** | `#0A1128` | Section backgrounds, cards |
| **Hull Steel** | `#1A1A2E` | Borders, dividers, inactive elements |
| **Trench Teal** | `#004466` | Secondary accent, hover states |
| **Neon Cyan** | `#00FFFF` | Primary accent, headings, links, glow |
| **Scrapper Orange** | `#FF6600` | CTAs, highlights, urgency indicators |
| **Salvage Pink** | `#FF0055` | Studio credit, secondary CTA, danger/warning |
| **Rust Red** | `#CC5500` | Subtle accents, biome reference |
| **Static Gray** | `#8A8A9F` | Body text, muted elements |

**Usage rule**: 80% dark (Void/Abyss/Hull), 15% neon accent (Cyan/Orange/Pink), 5% utility (Steel/Gray). Never more than two neon colors active on screen at once — this isn't a rave.

### 3.3 Typography

| Role | Font | Style |
|---|---|---|
| **Headings** | `'Courier New', Courier, monospace` | Uppercase, letter-spacing: 3px, cyan glow |
| **Body** | `'Courier New', Courier, monospace` | Regular weight, 14-16px, Static Gray |
| **UI / Labels** | `'Courier New', Courier, monospace` | Uppercase, smaller, tracking |
| **Accent / Log** | `'Courier New', Courier, monospace` | Italic where needed, orange/pink |

**Monospace-only rule**: The entire site uses Courier New. This is non-negotiable — it's a scrapper's terminal, not a design portfolio. Variable-width fonts kill the aesthetic.

### 3.4 Visual Elements

#### Backgrounds
- **Global**: Deep starfield with slow parallax drift. Tiny particles (1-3px) at varying depths.
- **Section transitions**: Horizontal scanline wipe or glitch-distortion transition (CSS clip-path or canvas effect)
- **Ambient animation**: Faint CRT phosphor glow at edges, occasional random static flicker (opacity 0.02-0.05, very subtle)

#### UI Components
- **Buttons**: Outlined rectangles (2px border), monospace text, hover fills with glow. Two variants: Primary (Cyan border, Cyan glow on hover) and Action (Orange border/fill).
- **Cards**: Dark panels (#0A1128) with Hull Steel borders (1px), subtle inner shadow. No rounded corners — sharp edges only.
- **Dividers**: Horizontal rules styled as `[================]` ASCII-art line or thin (#1A1A2E) rule with center diamond `♦`.
- **Scrollbar**: Custom thin scrollbar in Hull Steel, thumb in Trench Teal.

#### Iconography
- Pixel-art icons at 16×16 or 32×32
- Common symbols: ⬡ (hex for "tech"), ◆ (diamond for "rare"), ▸ (play/proceed), ✦ (special)
- Avoid emoji as primary UI — use pixel sprites where possible

#### Imagery
- Gameplay screenshots with a scanline overlay and subtle vignette
- Sprite artifacts (individual enemy/boss sprites) as decorative elements between sections
- The "coelacanth silhouette" as a recurring brand mark — the ancient fish in the deep

### 3.5 Mood References
- **CRT terminal interfaces** (Fallout terminals, Alien nostromo screens)
- **Sega Genesis/Mega Drive** box art and cartridge labels
- **Deep-sea exploration consoles** (submarine instrument panels)
- **Retro game magazine layouts** (EGM, GamePro — grid-based, bold)
- **Cyberpunk 2.0** dataterms and netrunning interfaces

### 3.6 Motion Design
- **Scroll behavior**: Sections snap into view (CSS scroll-snap or light JS). Each section feels like "tuning into a channel."
- **Hover effects**: Glow expansion on interactive elements (text-shadow: 0 0 Xpx #00FFFF)
- **Page load**: Brief terminal "boot sequence" animation (text typing out `WHATANADVENTURE.GAMES v1.0 // CONNECTION ESTABLISHED...` then fading to Hero)
- **Glitch transitions**: Section changes have a subtle 2-frame glitch (CSS animation, no heavy JS)
- **Keep it fast**: No 5-second loading animations. The boot sequence is 1-1.5 seconds max.

---

## 4. Content Strategy

### 4.1 Content Hierarchy
1. **Game first.** Darius Star is the star. Everything orbits it.
2. **World second.** Sell the depth — literal and narrative.
3. **Studio last.** People care about the game, then they care about who made it.

### 4.2 Page Content Map

#### Hero
```
[Studio Logo Mark]
WHAT AN ADVENTURE GAMES
Independent Retro Arcade Studio
[DIVE IN ↓]
```

#### The Game
```
DARIUS STAR: CYBER COELACANTH
"Push. Move. Go."

A retro arcade shoot-'em-up. 10 biomes. 100 levels. 
One scrapper against the deep.

[Gameplay Carousel: 3-4 screenshots]
[Feature Grid: Biomes | Ships | Co-op | Scrap Economy]
[Ship Silhouettes: X-1 Scout · Y-2 Interceptor · Z-3 Dreadnought · Phantom · Specter]

[PLAY NOW →]
```

#### The World
```
THE DEEP AWAITS

[Biome Map: 10 nodes pulsing with biome-specific colors]
From Earth's Abyssal Trench to the Galactic Core — 
every descent reveals something darker.

[Character Cards]
Darius Star — Salvage mercenary. Father. "One-in-a-million."
Naya Warden — Tactical pilot. Partner. "Solid copy."
Lyra Navigator — Navigator. Daughter. "I can feel it shifting."

"One-in-a-million, starlight."
— Darius Star, Biome 3

[Newsletter CTA: "GET TRANSMISSIONS FROM THE DEEP"]
```

#### The Crew
```
WHO WE ARE

What An Adventure Games is one developer, 
a salvaged laptop, and an obsession with 
the games that shaped us.

[Origin story: 2-3 paragraphs about building Darius Star]
[Tech stack nod: Canvas · Web Audio · Cloudflare · Vanilla JS]

[FOLLOW THE BUILD →]
```

#### Transmissions
```
INCOMING TRANSMISSIONS

> [2026.06.01] — Biome 4 Visual Pass Complete
> [2026.05.15] — Co-op Mode Enters Testing
> [2026.04.28] — The Banter Engine Ships

[ALL TRANSMISSIONS →]
```

#### Dock
```
[Social Icons]
[Join the crew: email field + "HAIL" button]
© 2026 What An Adventure Games. Salvaged with care.
```

### 4.3 Content Principles
- **Show, don't tell.** Screenshots and sprite art carry the weight. Copy is lean.
- **One idea per section.** Don't cram — the scroll handles pacing.
- **Brevity is the scrapper's way.** Cut words. Then cut more. If Darius wouldn't say it, it doesn't belong.
- **No marketing-speak.** No "revolutionary," no "cutting-edge," no "immersive experience." This is a scrapper's console, not a VC pitch deck.
- **Update cadence**: Transmissions updated every 1-2 weeks with real dev progress. A stale blog kills credibility faster than no blog.

---

## 5. Call-to-Action Flow

### 5.1 Primary Conversion Path
```
Visitor lands
  → Hero (vibe)
  → Scroll to The Game (discovery)
  → "PLAY NOW" → /darius-star/ (primary conversion)
```

The primary conversion is **playing the game**. Everything else is secondary.

### 5.2 Secondary Flows

#### Newsletter Signup
```
The World section
  → "GET TRANSMISSIONS FROM THE DEEP"
  → Email field + "HAIL"
  → Confirmation: "Transmission link established. Stand by."
```
- **Goal**: Build a launch/wishlist audience
- **Incentive**: Lore drops, early access, dev behind-the-scenes
- **Frequency target**: 1-2 emails/month

#### Social Follow
```
Dock section
  → Social icons (Twitter, Discord, YouTube)
  → "FOLLOW THE BUILD" in Crew section
```
- **Goal**: Community building
- **Priority platforms**: Discord (community hub) > Twitter (announcements) > YouTube (devlogs/trailers)

#### Wishlist / Platform
```
The Game section
  → Steam / itch.io widget (when available)
  → "WISHLIST ON STEAM" CTA
```
- **Goal**: Pre-launch interest signals
- **Placement**: Below "PLAY NOW," secondary but visible

### 5.3 CTA Priority Order
1. **PLAY NOW** (immediate — game is live)
2. **Newsletter** (medium-term — audience building)
3. **Social Follow** (ongoing — community)
4. **Wishlist** (future — when on platforms)

### 5.4 Design Rules for CTAs
- Primary CTA (PLAY NOW): Orange fill (#FF6600), Cyan glow on hover, large button
- Secondary CTAs (Newsletter, Follow): Outlined Cyan border, fills on hover
- Never more than 2 CTAs visible simultaneously
- Every CTA has a verb: PLAY, GET, FOLLOW, WISHLIST, HAIL
- No passive CTAs ("Learn More," "Click Here") — scrapper verbs only

---

## 6. Technical Notes

### 6.1 Deployment
- **Platform**: Cloudflare Pages (same as darius-star)
- **Domain**: whatanadventure.games
- **Sub-path**: `/darius-star/` serves the existing game

### 6.2 Implementation Philosophy
- **Static HTML/CSS/JS** — no framework. Vanilla everything (consistent with the darius-star approach).
- **Single HTML file** for the landing page is acceptable for v1.
- **Performance**: Target < 100KB total page weight (excluding game screenshots). No external fonts (Courier New is a web-safe system font). No JavaScript frameworks.
- **Canvas for backgrounds**: Use a lightweight canvas element for the starfield/particle background — this is already proven in darius-star's renderer.

### 6.3 Responsive Strategy
- **Desktop-first** design (matching darius-star's internal 800×450 16:9 ratio mindset)
- **Mobile**: Stack sections vertically, increase tap targets to 44×44px, simplify the starfield particle count
- **Touch**: Scroll snap works natively on mobile
- **Breakpoints**: Single column below 768px, two-column where appropriate above

### 6.4 Accessibility Considerations
- High contrast between text and background (Static Gray on Void Black = ~7:1 ratio)
- Focus states visible (Cyan glow ring on focused elements)
- Skip-to-content link hidden until focused
- Alt text on all screenshots and sprite art
- Respect `prefers-reduced-motion` — disable glitch/particle animations

### 6.5 SEO Notes
- `<title>`: "What An Adventure Games — Retro Arcade Studio"
- `<meta description>`: "Home of Darius Star: Cyber Coelacanth. Independent retro arcade games built with grit and pixel art."
- Structured data: `VideoGame` schema for Darius Star
- OG tags: Studio logo, game screenshot, site URL
- `/darius-star/` already has OG tags — maintain consistency

---

## Appendix A: Brand Assets Needed

| Asset | Format | Priority |
|---|---|---|
| Studio logo mark (pixel art) | PNG, 128×128 + 512×512 | Critical |
| Darius Star title lockup | PNG, 800×200 | Critical |
| Gameplay screenshots (3-4) | PNG, 800×450 | Critical |
| Ship silhouette set (5 ships) | PNG/SVG, 64×64 each | High |
| Biome map illustration | PNG/SVG, 600×400 | High |
| Character portraits (3) | PNG, 128×128 each | Medium |
| Favicon (16×16 pixel coelacanth) | ICO/PNG | Medium |
| Social share image | PNG, 1200×630 | Medium |

## Appendix B: Content To Write

| Content Piece | Length | Priority |
|---|---|---|
| Studio origin story | 2-3 paragraphs | High |
| Darius Star elevator pitch | 1 paragraph | High |
| Feature bullet copy | 6-8 bullets | High |
| Character 1-line bios | 3 × 1 sentence | Medium |
| Biome teaser copy | 1 paragraph | Medium |
| Newsletter welcome email | 1 email | Low |

---

*Generated by Ned for What An Adventure Games. Design only — no code written.*

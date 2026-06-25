---
type: Reference
title: Google Audio Capabilities Research
description: Research notes on Google audio products (TTS, speech-to-text, audio generation).
resource: /home/ubuntu/google_audio_research.md
tags: [research, google, audio, tts]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/research/google-audio-capabilities.md
last_verified: 2026-06-25
verified_by: kai
status: current
migrated_from: /home/ubuntu/google_audio_research.md
---

# Google Flow Music & Lyria 3 – Research for Game Audio Generation

## Executive Summary

**Google Flow Music** and **Lyria 3** are NOT the same thing, but they are closely related:

| | Google Flow Music | Lyria 3 (Gemini API) |
|---|---|---|
| **What it is** | Consumer platform for music creation | Developer API for programmatic music generation |
| **URL** | `flowmusic.app` | `ai.google.dev/gemini-api/docs/music-generation` |
| **Target user** | Musicians, creators, consumers | Developers building applications |
| **Pricing** | Free to start (credit-based) | $0.04/clip (30s), $0.08/full song |
| **API Access** | No public API | Yes — Gemini API (REST + SDKs) |
| **Integration** | Web app only | Python, JS/TS, Go, Java, C#, REST |

Both are powered by the same underlying model family: **Lyria 3** by Google DeepMind.

---

## 1. Google Flow Music (`flowmusic.app`)

### Overview
- A **generative AI platform** for creating, remixing, and sharing studio-quality songs
- Tagline: *"Built with, and for, musicians"*
- Uses Google DeepMind's **Lyria 3** for music generation and **Veo** for AI music video generation
- Free to start, no credit card required (daily-credit model)

### Capabilities
- **Text-to-Music**: Describe a track in natural language; get a full-length song
- **Image-to-Music**: Upload an image to inspire a custom track
- **Music Videos**: Generate AI music videos using Veo
- **Instruments & Plugins**: Build custom audio plugins, music games, virtual instruments, custom DAWs in "your space"
- **Remixing**: Remix audio, apply effects
- **Personalization**: Learns your musical style over time
- **Community**: Create playlists, publish songs, follow artists, discover new music
- **Export**: Professional-grade audio export

### Audio Quality
- 44.1 kHz high-fidelity stereo
- Studio-quality output ("crisp, clear tracks ready for your projects")

### Output Formats
- Not explicitly documented, but derived from Lyria 3: MP3 (default), WAV available

### Can It Generate Music Scores AND Sound Effects?
- **Music scores**: YES — Cinematic orchestral pieces, ambient tracks, any genre
- **Sound effects (SFX)**: NOT designed for discrete SFX. It generates musical compositions (30s clips to multi-minute songs). You could prompt for "ambient background atmosphere" but not "laser blast" or "explosion"
- **Loops**: YES — The Clip model is specifically designed for "short clips, loops, previews"

### Integration Methods
- **No public API** — This is a consumer web platform at `flowmusic.app`
- For programmatic integration, use the Lyria 3 API directly (see below)

### Limitations
- Credit-based (free daily credits, details not public)
- No API access
- Web-only interface
- Not suitable for SFX generation

---

## 2. Lyria 3 (Gemini API)

### Overview
- Google DeepMind's family of **music generation models**
- Available via the **Gemini API** for developers
- Two model variants optimized for different use cases

### Model Variants

| Model | ID | Best For | Duration | Output | Price (paid tier) |
|---|---|---|---|---|---|
| **Lyria 3 Clip** | `lyria-3-clip-preview` | Short clips, loops, previews | 30 seconds | MP3 | **$0.04 per song** |
| **Lyria 3 Pro** | `lyria-3-pro-preview` | Full-length songs with structure | ~2 minutes (promptable) | MP3 (WAV optional) | **$0.08 per song** |

### Audio Quality & Output Formats
- **Quality**: 44.1 kHz high-fidelity stereo
- **Default format**: MP3
- **Optional format**: WAV (set `responseFormat` → `audio/wav` in `generationConfig`)
- Response includes: audio bytes (via `inlineData`), generated lyrics (text), song structure JSON

### Capabilities
- **Text-to-Music**: Full prompt-based generation with detailed control
- **Image-to-Music**: Upload images to inspire compositions
- **Genre versatility**: Pop, funk, Motown, electronic, orchestral, ambient, cinematic, folk, and more
- **Instrumental arrangements**: Full band/orchestral compositions
- **Vocals + Lyrics**: Generates lyrics automatically; realistic vocal synthesis
- **Multilingual vocals**: Supports different languages
- **Musical structure**: Verses, choruses, bridges, dynamic builds
- **Real-time variant**: Lyria RealTime (`lyria-realtime-exp`) for streaming, interactive music generation via WebSockets

### API Access & Integration

```
Endpoint: POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent
Auth: API key (x-goog-api-key header) or OAuth
```

**SDKs available**: Python (`google-genai`), JavaScript/TypeScript (`@google/genai`), Go (`google.golang.org/genai`), Java, C#, REST

**Example (Python)**:
```python
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="lyria-3-pro-preview",
    contents="An epic cinematic orchestral piece about a journey home. "
             "Starts with a solo piano intro, builds through sweeping "
             "strings, and climaxes with a massive wall of sound."
)
for part in response.parts:
    if part.inline_data is not None:
        with open("output.mp3", "wb") as f:
            f.write(part.inline_data.data)
```

### Can It Generate Music Scores AND Sound Effects?
- **Music scores**: YES — excels at this. Cinematic orchestral scores, ambient backgrounds, thematic pieces, battle music, exploration music
- **Sound effects (SFX)**: **NO** — Lyria 3 is a *music* generation model, not a sound effect generator. It creates musical compositions, not discrete SFX like footsteps, gunshots, UI clicks, etc.
- **Ambient backgrounds**: YES — "atmospheric ambient track" is explicitly shown in docs

### Limitations (from official docs)
1. **Safety filters**: All prompts checked; copyrighted lyrics/artist voices blocked
2. **SynthID watermarking**: All generated audio has imperceptible digital watermark
3. **Single-turn only**: No multi-turn editing. Cannot iteratively refine a track
4. **Fixed durations**: Clip = always 30s; Pro = ~2 minutes
5. **Non-deterministic**: Same prompt may produce different results
6. **Preview status**: Both models are **preview** (may change, restrictive rate limits)
7. **Rate limits**: Dynamic, viewable in AI Studio; preview models have tighter limits
8. **No SFX**: Designed for music, not sound effects
9. **No stem separation**: Cannot export individual instrument tracks

### Free Tier
- Free tier available for experimentation (same models, rate-limited)
- Usage "may be used to improve Google's products" on free tier
- Paid tier has no such data usage clause

---

## 3. Lyra (Speech Codec) — NOT Music Generation

> ⚠️ **Important distinction**: The user mentioned "Google Cloud Lyra 3" — this likely refers to **Lyria 3** (above), NOT the Lyra speech codec.

**Lyra** (no "i") is a completely different Google technology:

| | Lyra (Speech Codec) | Lyria 3 (Music Model) |
|---|---|---|
| **Type** | Low-bitrate speech codec | AI music generation model |
| **Purpose** | Compress/decompress voice audio | Generate new music from prompts |
| **Output** | Compressed speech at 3.2–9.2 kbps | 44.1 kHz stereo music (MP3/WAV) |
| **Availability** | Open-source on GitHub (`google/lyra`) | Gemini API (paid, preview) |
| **Google Cloud** | NOT a Cloud API product | Part of Gemini API on Google Cloud |
| **Use case** | VoIP, voice calls on slow networks | Music creation, game scores |

Lyra is a **codec** (encoder/decoder), NOT a generator. It compresses existing speech audio to very low bitrates using generative AI. It cannot create music or sound effects.

---

## 4. Recommendations for Darius Star: Cyber Coelacanth

### For Game Music Scores:
✅ **Lyria 3 Pro (via Gemini API)** is the best fit:
- Generate cinematic orchestral pieces programmatically
- $0.08 per ~2-minute track
- Direct API integration for build-time or runtime generation
- Prompt examples: "Dark synthwave boss battle theme", "Underwater ambient exploration music", "Retro arcade victory fanfare"

### For Sound Effects:
❌ **Lyria 3 is NOT suitable for SFX**
- Consider alternatives:
  - Google's **TTS models** (for UI speech)
  - Traditional SFX libraries (e.g., `jsfxr`/`sfxr` for retro 8-bit effects)
  - Procedural SFX generation (Web Audio API, FM synthesis)

### Integration Pattern for Game Dev:
```
1. Developer creates prompts for each game scene/mood
2. Pre-generate tracks via Gemini API (build time)
3. Cache generated MP3s in game assets
4. Use traditional SFX library for sound effects
5. Optionally use Lyria RealTime for dynamic/interactive music
```

### Cost Estimate:
- 20 game tracks × $0.08 = **$1.60 total** for full game OST
- Plus free-tier experimentation before committing

---

## 5. Key Links

| Resource | URL |
|---|---|
| Google Flow Music | `https://www.flowmusic.app/` |
| Lyria 3 API Docs | `https://ai.google.dev/gemini-api/docs/music-generation` |
| Lyria RealTime Docs | `https://ai.google.dev/gemini-api/docs/realtime-music-generation` |
| Gemini API Pricing | `https://ai.google.dev/pricing` |
| Lyra Speech Codec (GitHub) | `https://github.com/google/lyra` |
| AI Studio (try Lyria 3) | `https://aistudio.google.com/` |

---

*Research compiled June 8, 2026. Lyria 3 models are in preview and pricing/features may change.*

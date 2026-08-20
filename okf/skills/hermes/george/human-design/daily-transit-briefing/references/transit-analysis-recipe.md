# Transit Analysis Recipe — Find the Headline First

The headline of a daily briefing anchors on **transit geometry, not on the planets**. A quote that names a specific channel completing today + a specific natal gate it touches will feel like insight; one that lists "Sun in Gate 4" will feel like weather.

## The Three-Step Analysis (run BEFORE writing any prose)

### Step 1: Which channels fully light today?

A channel lights when BOTH gates are occupied by any transit body.

```python
CHANNEL_NAMES = {
    (1,8): "1-8 Inspiration",
    (2,14): "2-14 The Beat",
    (3,60): "3-60 Mutation",
    (4,63): "4-63 Logic",
    (5,15): "5-15 Rhythm",
    (6,59): "6-59 Mating",
    (7,31): "7-31 Alpha",
    (9,52): "9-52 Concentration",
    (10,20): "10-20 Awakening",
    (10,34): "10-34 Exploration",
    (10,57): "10-57 Perfected Form",
    (11,56): "11-56 Curiosity",
    (12,22): "12-22 Openness",
    (13,33): "13-33 The Prodigal",
    (16,48): "16-48 Wavelength",
    (17,62): "17-62 Acceptance",
    (18,58): "18-58 Judgment",
    (19,49): "19-49 Synthesis",
    (20,34): "20-34 Charisma",
    (20,57): "20-57 Brainwave",
    (21,45): "21-45 Money",
    (23,43): "23-43 Structuring",
    (24,61): "24-61 Awareness",
    (25,51): "25-51 Initiation",
    (26,44): "26-44 Surrender",
    (27,50): "27-50 Preservation",
    (28,38): "28-38 Struggle",
    (29,46): "29-46 Discovery",
    (30,41): "30-41 Recognition",
    (32,54): "32-54 Transformation",
    (35,36): "35-36 Crisis",
    (37,40): "37-40 Community",
    (39,55): "39-55 Emoting",
    (42,53): "42-53 Maturation",
    (47,64): "47-64 Abstraction",
    (57,10): "57-10 Perfected Form",
    (57,20): "57-20 Brainwave",
    (58,18): "58-18 Judgment",
    (59,6): "59-6 Mating",
    (60,3): "60-3 Mutation",
    (61,24): "61-24 Awareness",
    (62,17): "62-17 Acceptance",
    (63,4): "63-4 Logic",
}

transit_gates = set(d['gate'] for d in transits.values() if isinstance(d, dict))
lit = [(a,b,name) for (a,b),name in CHANNEL_NAMES.items() if a in transit_gates and b in transit_gates]
```

If 0 channels fully light, the headline is the **single strongest natal hit** (Step 3 below). If 1+ light, this is the candidate pool.

### Step 2: Which transit gates touch this person's natal gates?

```python
# CRITICAL: use cosmic_calculator.calculate_natal_chart from the MCP server
import sys
sys.path.insert(0, os.environ.get("PRISMATIC_HOME", "/home/ubuntu") + "/work/OpenHumanDesignMCP/hd-mcp-server/src")
from cosmic_calculator import calculate_natal_chart
import pytz

# birth_dt_utc must be a timezone-aware UTC datetime
chart = calculate_natal_chart(name="Michael", birth_dt=dt_utc, lat=34.2694, lon=-118.7815, timezone="UTC")
natal_gate_set = set(chart["all_active_gates"])  # list[int]
defined_chans = [(c["name"], tuple(sorted(c["gates"]))) for c in chart["defined_channels"]]
defined_centers = chart["defined_centers"]
open_centers   = chart["undefined_centers"]

hits = natal_gate_set & transit_gates
for g in sorted(hits):
    natal_planets = [b for b,v in chart["personality_planets"].items() if v.get("gate")==g]
    transit_planets = [b for b,d in transits.items() if isinstance(d,dict) and d.get("gate")==g]
    print(f"Gate {g}: natal={natal_planets} | transit={transit_planets}")
```

### Step 3: Match — does a lit channel pair with a natal hit?

This is the **golden match**. The quote anchors on the strongest match:

1. **Best**: a fully lit transit channel where one of the two gates is natal for the subject (e.g., transit lit 18-58, subject has natal Gate 58 → they're being asked to complete their potential into channel form).
2. **Strong**: a transit channel that matches one of the subject's defined natal channels (e.g., subject has defined 26-44, transit lights 26-44 — the channel gets amplified).
3. **Fallback**: a generic transit hit on a natal gate that doesn't complete anything (just lists "Sun hits gate 4 today"). Use this only as fallback.

### Worked example — 2026-08-14

- Transit channels lit that day: 18-58 (Judgment), 30-41 (Recognition).
- Michael's natal gates: {1, 7, 8, 13, 14, 23, 26, 28, 38, 44, 45, 52, 58, 60}.
- **Match**: Michael has natal Gate 58. Transit lights 18-58 via Venus (18) + True Lilith (58). → **Golden match**. Headline anchored on this: "Channel 58-18 (Judgment) is being asked to form inside you today — your open Gate 58 is receiving the call."

### Worked example — 2026-08-15

- Transit channels lit that day: 18-58 (Judgment), 29-46 (Discovery), 30-41 (Recognition).
- Michael's natal gates (verified via `chart["all_active_gates"]`): {1, 6, 7, 8, 10, 13, 14, 22, 26, 29, 30, 38, 44, 45, 47, 48, 50, 52, 58, 60}.
- **Match #1 (Golden)**: Michael has natal Gate 58. Transit lights 18-58 → "Judgment being asked to form inside him through his Heart center (58 is in Heart/Ego)."
- **Match #2 (Golden)**: Michael has natal Gate 30. Transit lights 30-41 → "Recognition completing through his Solar Plexus gate (30 sits in Solar Plexus)."
- **Center conditioning (use `transits[planet]['center']` to verify, not the gate→center map below)**: Gate 30 = Solar Plexus per the engine output → Michael's Solar Plexus is **undefined**, so 30-41 conditions his emotional wave. Gate 58 = Heart center per the engine output → his Heart is **defined**, so 18-58 amplifies existing voice rather than conditioning a wave.

If no golden match exists, drop to the next strongest transit signature and let the prose breathe around it rather than force the "channel completion" framing.

## Gate → Center map (for "open center conditioning" notes)

> **WARNING**: this map has known inaccuracies. Gate 21 is listed in both Head and Heart here — per the canonical Ra mapping, gate 21 sits in the **Head Center** only (not Heart). Gate 38 is listed under Root but the channel 28-38 ("Struggle") is conventionally classified as **Spleen/Root-bridge**, and gate 38 sits in the Spleen Center per most modern BodyGraph renders. **Always cross-check against `transits[planet]['center']` returned by the engine** rather than trusting this map alone. The reliable path: `for p,d in transits.items(): d['center']` gives the engine's authoritative assignment.

```python
GATE_CENTER = {
    # Ajna
    4:'Ajna', 11:'Ajna', 17:'Ajna', 24:'Ajna', 43:'Ajna', 47:'Ajna',
    # Head
    20:'Head', 21:'Head', 50:'Head', 64:'Head',
    # Root
    19:'Root', 39:'Root', 41:'Root', 53:'Root', 54:'Root',
    # Solar Plexus
    6:'Solar Plexus', 22:'Solar Plexus', 30:'Solar Plexus', 36:'Solar Plexus',
    37:'Solar Plexus', 49:'Solar Plexus', 55:'Solar Plexus', 12:'Solar Plexus',
    # Sacral
    5:'Sacral', 14:'Sacral', 29:'Sacral', 34:'Sacral', 27:'Sacral', 28:'Sacral', 42:'Sacral',
    # G/Identity
    1:'G', 7:'G', 10:'G', 13:'G', 15:'G', 25:'G', 46:'G',
    # Heart/Ego
    26:'Heart', 40:'Heart', 51:'Heart',
    # Throat
    16:'Throat', 18:'Throat', 23:'Throat',
    31:'Throat', 33:'Throat', 35:'Throat', 45:'Throat',
    56:'Throat', 62:'Throat',
    # Spleen
    32:'Spleen', 44:'Spleen', 48:'Spleen', 57:'Spleen',
    38:'Spleen',  # canonical: Struggle channel 28-38 is Spleen dynamics
    58:'Heart',   # Judgment channel 18-58 has 58 in Heart/Ego
}
```

If the subject has an **undefined** center and a transit planet sits in a gate of that center, that's open-center conditioning:
- **Ajna**: mental static, ideas that feel like yours but aren't.
- **Head**: pressure to think, conceptual input.
- **Root**: fear/adrenal spikes that aren't yours.
- **Sacral**: erratic life-force, sexual or vitality buzz.
- **Solar Plexus**: emotional wave, anticipation.

Cite the conditioning in the "Watch for" section, not the headline.

## Family data path

`~/work/next-step-bot/family.json` — read this before ANY compute. It contains:
- Michael, Becca, Benjamin, William, Victoria birth data (year, month, day, hour, lat, lon).
- Type, profile, authority per person.

**Profile-aware resolution** (the SKILL.md text says "don't grep the filesystem" but the path is profile-dependent):

```python
import os, json
candidates = [
    os.path.expanduser("~/work/next-step-bot/family.json"),
    os.path.expanduser(f"~/.hermes/profiles/{os.environ.get('HERMES_PROFILE','fred')}/home/work/next-step-bot/family.json"),
]
path = next((p for p in candidates if os.path.exists(p)), None)
if path is None:
    raise FileNotFoundError(f"family.json not found at any of: {candidates}")
with open(path) as f:
    family = json.load(f)["family"]
```

Do not grep the filesystem; the candidates list above is exhaustive for this deployment.
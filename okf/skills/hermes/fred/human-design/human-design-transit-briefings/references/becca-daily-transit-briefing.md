# Becca Daily Transit Briefing Reference

## Recipient constants
- Becca: 6/2 Splenic Projector.
- Birth data supplied for briefing jobs: Dec 14 1987, 04:18, Tacoma WA.
- Use `America/Los_Angeles` for localizing the birth time, then convert to UTC before passing to `calculate_natal_chart`.
- Tacoma coordinates used in prior calculation: latitude `47.2529`, longitude `-122.4443`.

## Engine calculation sketch
```python
import sys
from datetime import datetime
import pytz

sys.path.insert(0, "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src")
from transit_engine import calculate_transit_positions, compute_transit_overlay
from ephemeris_engine import julday, init_ephemeris
from cosmic_calculator import calculate_natal_chart

init_ephemeris()
mt = pytz.timezone("America/Denver")
now = datetime.now(mt)
jd = julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
transits = calculate_transit_positions(target_jd=jd)

pacific = pytz.timezone("America/Los_Angeles")
birth_local = pacific.localize(datetime(1987, 12, 14, 4, 18, 0))
birth_utc = birth_local.astimezone(pytz.UTC)
chart = calculate_natal_chart(
    name="Becca",
    birth_dt=birth_utc,
    lat=47.2529,
    lon=-122.4443,
    timezone="America/Los_Angeles",
)
overlay = compute_transit_overlay(chart, target_jd=jd)
```

## Becca natal baseline from the engine
Use current engine output if possible, but prior verified baseline was:
- Type/authority/profile: Projector, Splenic, 6/2.
- Defined centers: G, Heart/Ego, Spleen.
- Undefined centers: Ajna, Head, Root, Sacral, Solar Plexus, Throat.
- Defined channels: 25-51 Initiation, 26-44 Surrender.
- Core incarnation cross at prior run: Left Angle Cross of Confrontation 2.
- Cross gates: personality sun = 26, personality earth = 45, design sun = 6, design earth = 36.

## Daily Signatures Worth Headlining
These are the recurring patterns that make a brief feel like Becca's.
- A transit landing directly on Gate 26 (her personality sun) or Gate 45 (her personality earth) — one's hitting, frame the whole brief around it.
- Temporary completion of 21-45 (Money/Tribal) when Mars or Saturn is the trigger — value/community/who's-in energy.
- All six undefined centers temporarily conditioned — this is its own headline: a full day of borrowed definition.

## Composition checklist
- Keep under 18 lines when the cron prompt requests it.
- If the prompt includes a missing-skill warning, the final response must start with that exact brief notice before the briefing.
- "So What" / "ONE THING" must be a real task Becca can do immediately.
- Family snippets should be one sentence each for Michael, Benjamin, William, and Victoria when requested. **Do not invent natal overlays** for family members unless their full natal data is in this reference. Write each snippet from the computed collective transits plus known family context (Michael = 3/5 Splenic Projector with G/Heart/Ego/Spleen/Throat defined; kids = Benjamin / William / Victoria), phrased as practical support.
- Prefer concrete household language over technical HD exposition.

## Agent identity
When the cron prompt identifies the speaker as "Sage" or "Sage/Fred", sign the brief as **Sage**. The umbrella skill is owned by Fred (Michael's Hermes assistant), but the Becca briefings use Sage as the in-character voice. Don't normalize to "Fred" for Becca's briefs.

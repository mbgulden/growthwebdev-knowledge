# AEO (Answer Engine Optimization) Block Patterns

Used for targeting Google featured snippets, People Also Ask boxes, and AI Overviews.
Place after `<h1>` on every guide page.

## Standard AEO Block (HTML)

```html
<div class="aeo-quick-answer" style="background:#f0f8ff; border-left:4px solid #0077be; padding:15px; margin:20px 0; border-radius:4px;">
<p><strong>Direct answer here — 40-60 words, starts with the answer, includes a specific data point.</strong></p>
</div>
```

## Per-Topic AEO Examples

### Electric Beach
> **Electric Beach (Kahe Point Beach Park) on Oahu's leeward coast is one of the island's best snorkel spots, thanks to warm water discharged from the Kahe Power Plant that attracts sea turtles and tropical fish year-round. Best visited in summer (June–September) when the ocean is calm. Park in the main lot off Farrington Highway — arrive before 9am on weekends.**

### Lanikai Beach
> **Lanikai Beach on Oahu's windward coast is famous for its soft white sand, turquoise water, and iconic view of the Mokulua Islands. There is no parking lot — arrive before 8am or park legally on Kailuana Loop. The calm, reef-protected waters make it ideal for swimming, kayaking, and paddleboarding.**

### Kailua Beach Park
> **Kailua Beach Park on Oahu's windward side offers a large free parking lot, full facilities (restrooms, showers, picnic tables, lifeguards), and a paved boat ramp for easy kayak launching. Best visited in the morning (before 10am) when the trade winds are calm and parking is plentiful.**

### Chinaman's Hat Kayak
> **Paddling to Chinaman's Hat (Mokoliʻi Island) from Kualoa Regional Park takes 15-20 minutes in calm conditions. The water is waist-deep in most spots due to the reef shelf, making it one of Oahu's safest kayak trips. The island has a short but steep summit hike with panoramic views of Kaneohe Bay.**

### Kaneohe Sandbar
> **The Kaneohe Sandbar (Ahu O Laka) is a submerged sandbar that emerges at low tide, creating a shallow wading pool in the middle of Kaneohe Bay. Paddle from Kualoa Regional Park (~30 minutes each way). Visit 2 hours before low tide for the best experience.**

### Sea Turtles on Oahu
> **Hawaiian green sea turtles (honu) are protected under both state and federal law — stay at least 10 feet away, never touch or chase them, and do not use flash photography. Best places to see them: Turtle Canyon (Waikiki), Laniakea Beach (North Shore), and Sharks Cove (summer only).**

## Requirements

- **40-60 words** — Google's featured snippet sweet spot
- **Start with the answer** — not "if you're wondering about..." or "let me tell you about..."
- **One data point** — paddle time, price, distance, or seasonal fact
- **Active voice** — no passive constructions
- **Specific location** — reference actual Oahu locations by name
- **No introductory filler** — cut "this beach is" and start with the beach name

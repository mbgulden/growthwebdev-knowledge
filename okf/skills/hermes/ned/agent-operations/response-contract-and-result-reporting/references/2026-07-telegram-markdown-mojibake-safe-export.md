# Telegram Markdown export mojibake-safe pattern (2026-07-16)

Use this when Michael asks for a downloadable `.md` file intended to be shared through Telegram or copied out of Telegram.

## Durable lesson

Telegram/client encoding can mangle smart punctuation, arrows, and emoji into mojibake (`â`, `Â`, `Ã`, `ð`, etc.). If a prompt/report is meant to be downloaded and pasted, provide an ASCII-safe variant when there is any sign of mojibake or when the content includes high-risk glyphs.

## Pattern

1. Write the Markdown file normally if needed.
2. Generate an ASCII-safe copy for Telegram portability:
   - smart quotes -> straight quotes
   - em/en dashes -> `--` or `-`
   - arrows -> `->`
   - emoji status markers -> text labels like `[PROCEED]`, `[FAMILY TEST]`, `[HOLD]`
3. Verify the exported file:
   - `non_ascii == False`
   - no `â`, `Â`, `Ã`, `ð`, `œ`, or `Ÿ`
   - required headings/sections still present
4. Deliver the ASCII-safe file with `MEDIA:/absolute/path`.

## Pitfalls

- Do not assume Markdown rendered in the chat will survive Telegram export/copy intact.
- Do not preserve mojibake examples in reusable prompt files unless the task is explicitly about detecting those exact patterns; describe them in words instead.
- If Michael pastes a corrupted version back, regenerate and verify an ASCII-safe artifact rather than explaining encoding theory.

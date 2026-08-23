---
name: image-reading
description: "Read and describe images Michael sends (screenshots, listings, reports): try vision_analyze first; if the vision endpoint errors, fall back to tesseract OCR + PIL upscale with the exact commands below. Use whenever Michael sends a photo/screenshot or asks 'can you read this image?'"
triggers:
  - Michael sends an image or screenshot
  - "can you read this image"
  - vision_analyze error fallback
  - OCR a screenshot
  - describe a phone screenshot
---

# Image Reading (Vision + OCR Fallback)

Class-level procedure for reading any image Michael sends on Telegram: product
listings, Lighthouse reports, CF dashboards, UI screenshots, photos.

## Step 0 — Find the image fast (do NOT re-discover it)

**Use absolute paths.** The terminal's `HOME` on this box can point at a
profile-local home, so `~` may expand to a doubled, nonexistent path like
`/home/ubuntu/.hermes/profiles/kai/home/.hermes/...` — every command then
fails silently (empty `ls`, missing config). Hard-code the real location:
`/home/ubuntu/.hermes/profiles/kai/`

Fast-find recipe (sub-second, verified 2026-08-21):

1. If the message header gives an exact path → use it directly.
2. Otherwise, newest file in the Telegram upload cache:
   ```bash
   ls -lt /home/ubuntu/.hermes/profiles/kai/image_cache/ 2>/dev/null | head -5
   ```
   Take the newest `img_<hash>.jpg` — that's Michael's just-sent image.
3. Cache empty (upload still landing)? Sleep ~2s, repeat the `ls` ONCE.

NEVER run unscoped disk searches to locate an upload:

- `find /home/ubuntu -mmin 10 ...` → **TIMED OUT at 180s** (2026-08-21, real incident).
- Scoped search, only if genuinely needed: `find /home/ubuntu/.hermes -mmin 10 \( -iname '*.jpg' -o -iname '*.png' -o -iname '*.webp' \)` — takes seconds.
- Prefix any find with `timeout 20` as a safety belt.
- The cache dir is the ONLY place Telegram uploads land. Don't hunt elsewhere.

## Steps

1. **Try `vision_analyze` first** with the cached path and a specific question.
2. **Check the `success` field, not just the output size.** A broken fallback
   endpoint returns `success: false` with an HTML error page that gets
   persisted to a ~197 KB file (looks like a real result at a glance — it is
   not). See `references/vision-endpoint-failure-2026-08-15.md` for the exact
   error signature.
3. If `success: false`, **do not retry the same call in a loop** (it just
   re-fetches the HTML page). Move to the OCR fallback:
   - `file <path>` — confirm it's a real image and note dimensions.
   - Plain OCR: `tesseract <path> stdout` (tesseract is installed at
     `/usr/bin/tesseract`).
   - For small phone screenshots (~588 px wide), upscale first — much cleaner
     text:
     ```bash
     python3 -c "
     from PIL import Image
     img = Image.open('<path>')
     img.resize((img.width*3, img.height*3), Image.LANCZOS).save('/tmp/<name>_big.png')
     "
     tesseract /tmp/<name>_big.png stdout --psm 6
     ```
     (`--psm 6` = assume uniform block of text; good for app UIs. PIL is
     available in the hermes-agent pipx venv.)
4. **Compose the answer from the OCR text**: extract the meaningful fields
   (title, price, seller, badges, buttons), ignore OCR noise (garbled status
   bar, icon glyphs), and add only safe contextual commentary.
5. **Tell Michael how you read it** in one line (native vision vs OCR) so he
   knows the confidence level. If OCR quality is poor or the image is a
   photo rather than UI text, say so honestly and offer alternatives — never
   fabricate content you didn't extract.

## Benchmarks (measured 2026-08-21, local server 192.168.1.232:8080, qwen3.8-27b)

End-to-end HTTP→stream-complete (what `vision_analyze` pays), median of 3
after warmup. TTFE = time to first content token.

| image | reasoning | TTFE med | total med |
|---|---|---|---|
| telegram upload 190KB | medium | 1.42s | 2.54s |
| telegram upload 190KB | none | 0.27s | 1.37s |
| telegram upload 190KB | low (config default) | 1.42s (est.) | 2.54s (est.) |
| beach photo 1600px | medium | 1.43s | 2.37s |
| beach photo 1600px | none | 0.29s | 1.22s |
| lighthouse mock | medium | 1.95s | 2.82s |
| lighthouse mock | none | 0.22s | 1.33s |

- **Dominant cost = generation, not discovery or encoding.** File read +
  base64 of a 190KB image is <50ms; the Step 0 `ls` is <100ms. The model
  does ~1.1s of reasoning (reasoning_effort=medium) before the first token.
- **OCR fallback** (3× LANCZOS + `--psm 6`, phone-size 588px): **~0.57s**.
  Faster than vision — only for plain-text screenshots when vision is down.
- **Honest user-perceived total** (upload → reply) ≈ discovery (≤1s) +
  vision (~2.5s med) + my summarization (1–3s) = **~4–7s**. Don't promise
  sub-second; "a few seconds" is the true number.

**The one real speed lever:** `reasoning_effort`. The auxiliary vision
provider currently runs `medium` (see custom_providers `qwen27b-kai-local`).
Setting it to `none` halves latency (2.5s→1.4s) and quality held up on all 4
tests, but it changes behavior globally for that provider — **only change it
if Michael approves**, and via the provider config, not a per-call hack.

## Pitfalls

- **`vision_analyze` is a tool, not a Python import.** You cannot `from hermes_tools import vision_analyze` and call it directly in an `execute_code` block; it will fail with `ImportError`.

- **Never treat a `success: false` vision result as a description.** The HTML
  error page contains no image content; summarizing it would be fabrication.
- **Don't hard-code "vision is broken."** The endpoint may be fixed later —
  always attempt `vision_analyze` first on each session. The lesson is the
  fallback path, not a permanent ban on the tool.
- **Raw tesseract on small screenshots is noisy.** The 3× LANCZOS upscale +
  `--psm 6` pass is the reliable pattern; use it for phone screenshots by
  default.
- **OCR gives you text, not understanding of photos.** For non-UI images
  (landscapes, people, products), OCR returns little; be upfront that the
  vision endpoint is down rather than guessing.
- **OCR output includes status-bar garbage** (time, signal glyphs, partial
  icons). Filter it when writing the summary; don't present raw OCR lines as
  if they were structured data.
- **Prices/titles from OCR should be double-checked** for digit confusion
  (e.g. 648.95 vs 648.9S) before repeating them as facts in the reply.

## References

- `references/vision-endpoint-failure-2026-08-15.md` — exact error signature
  of the broken fallback endpoint + working OCR recipe from the session that
  hit it.

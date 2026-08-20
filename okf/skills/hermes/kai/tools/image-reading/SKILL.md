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

## Inputs

- Telegram images are cached at `~/.hermes/profiles/kai/image_cache/img_<hash>.jpg`.
- The message header gives the exact path — use it; don't guess.

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

## Pitfalls

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

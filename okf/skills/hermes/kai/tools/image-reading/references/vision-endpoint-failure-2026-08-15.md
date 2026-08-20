# Vision Endpoint Failure — 2026-08-15

Session: Michael sent an eBay screenshot (NVIDIA Tesla V100 32GB, $648.95,
seller "dandyful", 588×1280 JPEG) and asked if Kai can read images.

## What happened

- `vision_analyze` returned `success: false` with an error containing an HTML
  page (~197 KB after persistence): a styled error document with a logo SVG,
  `@media (prefers-color-scheme: dark)` CSS, and `<meta http-equiv="refresh"
  content="360">`. This is a **broken fallback vision endpoint** serving an
  HTML error page — not the image's content.
- The persisted-output wrapper made it look like a huge real result. The
  `success: false` field is the tell.
- Retrying the same call (3 total attempts) returned the identical HTML page.
  No point retrying; the endpoint itself is the problem.

## Working fallback (verified in-session)

1. `file` confirmed: `JPEG image data, progressive, 588x1280`.
2. `tesseract img.jpg stdout` — worked, readable text, some noise.
3. Upscaled recipe — cleaner:
   ```bash
   python3 -c "
   from PIL import Image
   img = Image.open('img.jpg')
   img.resize((img.width*3, img.height*3), Image.LANCZOS).save('/tmp/big.png')
   "
   tesseract /tmp/big.png stdout --psm 6
   ```
   Extracted cleanly: "eBay Refurbished / NVIDIA HP Tesla V100 32GB PCIe /
   HBM2 Data Center AI GPU / PG500-216 Passive / dandyful (3671) / 99.7%
   positive / $648.95 / 9 SOLD TODAY / 1 of 10 / Home My eBay Search Live Selling".

## Environment facts (as of 2026-08-15, may change)

- `tesseract` at `/usr/bin/tesseract` — installed.
- `PIL` importable in hermes-agent pipx venv
  (`/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python3`).
- Telegram image cache dir: `~/.hermes/profiles/kai/image_cache/`.

## Lesson

The durable pattern is: **try native vision → check `success` → OCR fallback
with upscale**. Never present the HTML error page as image content, and never
harden "vision is broken" into a permanent refusal — re-test each session.

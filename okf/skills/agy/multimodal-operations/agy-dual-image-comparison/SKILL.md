---
name: agy-dual-image-comparison
description: Compare UI screenshots and mockups pixel-by-pixel to detect visual regressions.
version: 1.0.0
---

# AGY Dual Image Comparison

Perform automatic visual validation of render targets against mockups or reference designs.

## Trigger Conditions

Use when verifying UI layout changes, checking branding guidelines, or checking visual regression.

## Numbered Steps with Exact Commands

1. **Verify Python PIL installation**:
   Ensure pillow is available:
   ```bash
   python3 -c "from PIL import Image, ImageChops"
   ```

2. **Run image comparison script**:
   Save a Python script to compare `/tmp/mockup.png` and `/tmp/render.png`:
   ```python
   # /home/ubuntu/.gemini/antigravity-cli/scratch/img_compare.py
   from PIL import Image, ImageChops
   
   img1 = Image.open("/tmp/mockup.png").convert("RGB")
   img2 = Image.open("/tmp/render.png").convert("RGB")
   
   # Resize if needed
   if img1.size != img2.size:
       img2 = img2.resize(img1.size)
       
   diff = ImageChops.difference(img1, img2)
   bbox = diff.getbbox()
   if bbox:
       print(f"DIFF_DETECTED: {bbox}")
       diff.save("/tmp/diff_result.png")
   else:
       print("IMAGES_MATCH")
   ```
   Execute it:
   ```bash
   python3 /home/ubuntu/.gemini/antigravity-cli/scratch/img_compare.py
   ```

3. **Check diff result image**:
   If differences were detected, copy the `/tmp/diff_result.png` file to the artifacts directory and display it.

## Pitfalls

- **Varying dimensions**: ImageChops difference requires matching sizes. Explicitly resize the screenshot to match the mockup size.
- **Anti-aliasing artifacts**: Sub-pixel font differences can trigger diff flags. Focus on layout bounding boxes (`getbbox`) rather than direct pixel counts.

## Verification Steps

- Run the script. Ensure it outputs either `IMAGES_MATCH` or `DIFF_DETECTED: (...)`.

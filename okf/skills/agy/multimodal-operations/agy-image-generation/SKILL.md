---
name: agy-image-generation
description: Generate visual assets, mockups, or illustration files using Imagen.
version: 1.0.0
---

# AGY Image Generation

Generate UI graphics, placeholders, logos, or design assets using native tools.

## Trigger Conditions

Use when a web design or mock task requires visual placeholders, logo designs, or graphic assets.

## Numbered Steps with Exact Commands

1. **Verify tool capability**:
   Ensure the `generate_image` tool is available in your active tool declarations.

2. **Call tool with prompt**:
   Generate the asset:
   ```json
   {
     "Prompt": "A modern, minimalist, glassmorphic logo icon for a developer application named Antigravity. Vector-like SVG design, dark mode aesthetics.",
     "ImageName": "antigravity_logo",
     "toolSummary": "Generate Antigravity logo icon",
     "toolAction": "Generating image asset"
   }
   ```

3. **Check output file**:
   Confirm the file is saved locally:
   ```bash
   ls -la $HERMES_PROFILE/home/.gemini/antigravity-cli/brain/79178921-d52c-465a-b665-53338b7977ca/antigravity_logo.png
   ```

4. **Add to layout**:
   Include the generated image in Markdown using absolute paths:
   ```markdown
   ![Antigravity Logo]($HERMES_PROFILE/home/.gemini/antigravity-cli/brain/79178921-d52c-465a-b665-53338b7977ca/antigravity_logo.png)
   ```

## Pitfalls

- **Ambiguous Prompts**: Vague prompts can result in low-quality or irrelevant mockups. Be specific about style, color palettes, and framing.
- **Wrong output paths**: Always check where the tool saved the generated png and copy it to artifacts if needed.

## Verification Steps

- Ensure the file exists and is a valid PNG image.

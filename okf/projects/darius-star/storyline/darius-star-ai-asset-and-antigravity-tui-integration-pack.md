---
type: Reference
title: "Darius Star: AI Asset & Antigravity TUI Integration Pack"
description: Darius Star storyline/architecture directive — source content from Google Drive.
resource: okf/projects/darius-star/storyline/darius-star-ai-asset-and-antigravity-tui-integration-pack.md
tags: [darius-star, storyline, game-design, plugin-context]
timestamp: 2026-06-19T12:10:36Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/darius-star-ai-asset-and-antigravity-tui-integration-pack.md
last_verified: 2026-08-19
verified_by: kai
status: current
migrated_from: "Google Drive: mbgulden@gmail.com > Darius Star: AI Asset & Antigravity TUI Integration Pack"
google_doc_id: 147oKeowgx0nj4qhONSmM5E8wBxlst9wbAL8-0u-b4hI
modified_in_drive: 2026-06-09T00:13:01.363Z
migrated_from_repo: mbgulden/darius-star
---

# Darius Star: Cyber Coelacanth Integration Pack

This document outlines the professional standards and technical procedures for integrating high-fidelity assets into the Darius Star: Cyber Coelacanth development pipeline.

# 1. AI App Recommendation for 2D Retro Game Assets

To achieve the specific 16-bit aesthetic required for a retro-cyberpunk experience, the following tools are recommended:


Google Flow Beta (Premier Choice): Powered by Gemini Omni and Imagen 3, this platform is the primary recommendation for creating high-consistency game assets. It excels at maintaining stylistic coherence across complex prompt sequences, ensuring that the "Cyber Coelacanth" fleet retains a unified visual language.

Leonardo.ai: A robust industry alternative specifically utilized for generating isolated 2D sprites with clean edges, making it ideal for individual enemy units and character designs.

# 2. Complete Game Asset Prompt Pack

Use these curated prompts within Google Flow Beta or Gemini to generate high-quality 2D assets tailored for the game's retro-cyberpunk aesthetic.


| Asset Category
 | Detailed Prompt Content
 |
| Player Ship
 | Retro-cyberpunk fighter jet, 2D side-view sprite, 16-bit pixel art style, sleek aerodynamic frame with neon blue and purple glow accents, visible exhaust ports, high contrast.
 |
| Enemy Fleet
 | Set of cybernetic aquatic biome ships, including robotic fish with metallic scales, mechanical jellyfish with glowing fiber-optic tentacles, and electric eels with translucent circuitry.
 |
| Colossal Boss
 | 'Cyber Coelacanth' dreadnought ship, massive armored prehistoric fish silhouette, biomechanical plating, glowing red optic sensors, side-view boss sprite, intricate engine details.
 |
| Sprites & Effects
 | 2D retro VFX sheet, plasma laser beams, pulsating thruster flames, translucent blue energy shields, circular shockwave explosions, pixel-perfect bloom.
 |
| Parallax Levels
 | Layered backgrounds: Deep-space nebula with neon gas clouds and distant stars; sprawling cyberpunk biomechanical city with towering silhouettes and flickering lights.
 |
| Title & Credits
 | 16-bit arcade title card, 'Darius Star: Cyber Coelacanth' in stylized glowing futuristic font, dark space background, vibrant color palette, retro-gaming aesthetic.
 |

# 3. Antigravity TUI/CLI Integration & Optimization

The following instructions are designed for execution via the Antigravity TUI interface. Use these prompts to direct Antigravity agents in automating the build and optimization process.

## Asset Processing & Slicing

Instruct the Antigravity agent with the following:"Using the local Python library Pillow, write and execute a script to programmatically slice generated sprite sheets into individual 64x64 pixel frames. Ensure the script handles alpha transparency and saves the output to the /assets/sprites/ directory."

## Dynamic HTML5 Integration

Instruct the Antigravity agent with the following:"Update darius_twin.html to dynamically inject the newly sliced assets. Write a JavaScript utility that reads the asset manifest and populates the internal sprite object array, ensuring all paths are mapped correctly to the current directory structure."

## Performance Optimization Prompts

To maximize frame rates and responsiveness, provide these specific directives to the Antigravity TUI:


Loop Refactoring: "Refactor the darius_twin.html rendering loop to utilize requestAnimationFrame. Eliminate all setInterval calls to ensure synchronicity with the display refresh rate."

Pre-rendering: "Implement offscreen canvas pre-rendering for the 'Cyber Coelacanth' boss and complex fleet sprites. Render these to a hidden buffer once during load to reduce per-frame draw calls."

Lazy-loading: "Optimize initial load times by implementing lazy-loading for the parallax background layers and the Colossal Boss assets, triggering the download only when the player nears the relevant stage trigger."

## Automation & Resource Linting

Direct the agent to create a tasks.json file with the following capabilities:"Generate a tasks.json configuration to automate development workflows. Include a 'lint' command to check for missing asset references in darius_twin.html and a 'build' command to verify that all image dimensions conform to the required power-of-two constraints for GPU optimization."


Technical Lead: Integration Date: 


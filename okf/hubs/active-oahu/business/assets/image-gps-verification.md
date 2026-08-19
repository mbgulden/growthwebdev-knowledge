---
type: Operations
title: AOT Image / GPS Verification Gates
description: **Owner:** Kai **Applies to:** Any Active Oahu Tours task that selects, audits, places, renames, captions, crops, optimizes, or publishes imagery.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/assets/image-gps-verification.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# AOT Image / GPS Verification Gates

**Owner:** Kai  
**Applies to:** Any Active Oahu Tours task that selects, audits, places, renames, captions, crops, optimizes, or publishes imagery.

## Source-of-truth rule

AOT original imagery lives on **`Synology_NAS`**.

The NAS is the read-only source of truth:

- Treat all NAS images as **read-only originals**.
- Do **not** alter, optimize, resize, rename, move, or metadata-edit originals on the NAS.
- Do **not** direct-link website content to NAS paths or NAS URLs.
- When an image is selected, **copy it from `Synology_NAS` into the workspace/repo or a designated working folder**.
- Perform resizing, compression, metadata edits, filename normalization, and web publishing only on the copied file.
- Preserve the original NAS path in verification notes so the published image can be traced back to its source.

## When this gate is required

Run this gate whenever imagery is used to support a factual location, route, activity, product, gear, or customer-experience claim.

Examples:

- Mokoliʻi / Chinaman’s Hat image
- Kāneʻohe Sandbar image
- Sharks Cove snorkel image
- Kailua/Lanikai/Mokulua image
- Storefront / pickup / launch-point image
- E-bike, kayak, SUP, snorkel, beach gear image
- “Customer doing X at Y” image

## Image verification sequence

1. **Identify intended use**
   - Page/section where the image will appear.
   - Exact subject: kayak, e-bike, SUP, snorkel gear, beach gear, storefront, launch point, island, reef, sandbar, trail, customer activity, etc.
   - Exact location claim: beach, bay, island, launch point, route, storefront, attraction, GPS coordinates if available.

2. **Confirm legal/source status**
   - Verify the original is AOT-owned/approved or otherwise legally usable.
   - If the image is AI-generated or stock, it must be explicitly approved and labeled as illustrative when used near factual claims.
   - Do not use AI imagery as factual representation of a specific location or real customer experience unless Michael explicitly requests that use case and the label is clear.

3. **Copy from NAS before editing**
   - Copy the selected image from `Synology_NAS` into the workspace/repo or designated staging folder.
   - Do not edit the NAS original.
   - Record both paths:
     - `NAS source path:`
     - `Workspace/repo copy path:`

4. **Verify location accuracy**
   - Prefer EXIF GPS from the NAS original or copied file.
   - If EXIF GPS is unavailable, use the NAS source path, AOT media metadata, shoot notes, filename context, and visual landmark cross-checks.
   - For exact-place claims, compare visible landmarks against maps, Street View, official park/beach imagery, or known AOT shoot references.
   - Do not use a generic Hawaii/ocean/beach/kayak image for a specific named location unless the copy is generic.

5. **Verify subject accuracy**
   - The image must show the named activity/place/gear.
   - Do not use an e-bike image for kayak-specific content, or a kayak image for snorkel/SUP content, unless the section is explicitly multi-activity.
   - Do not use a generic kayak/ocean image for Mokoliʻi, Kāneʻohe Sandbar, Sharks Cove, Kailua, etc. when the section claims the specific place.

6. **Resolve uncertainty**
   - If location, subject, or rights cannot be verified, do not publish it as factual imagery.
   - Choose a different verified image, label it generic/illustrative, or mark the task blocked with the exact missing verification.

## Required PR/Linear comment section

```markdown
## Image/GPS verification

| Image | Intended subject/location | NAS source | Workspace copy | Evidence | Result |
|---|---|---|---|---|---|
| mokolii-kayak.jpg | Kayak route to Mokoliʻi / Chinaman’s Hat | Synology_NAS:/... | site/wp-content/uploads/... | EXIF GPS + visual landmark cross-check | Verified |
```

If no imagery was touched, say:

```markdown
## Image/GPS verification
No imagery was selected, edited, placed, captioned, or published in this change.
```

## Non-negotiables

- NAS originals remain untouched.
- Site content never direct-links NAS files.
- Exact location claims require exact location evidence.
- Exact activity/product claims require matching subject matter.
- “Looks similar” is not verification.

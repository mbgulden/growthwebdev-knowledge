---
type: Standard
title: Topic Cluster Map: Windward Oahu Location SEO
description: Mermaid architecture map + linking rules + commercial routing.
tags: [aot, seo, geo, ai-seo, migrated-from-existing]
timestamp: 2026-06-19T12:28:24Z
linear_issue: GRO-795
git_path: okf/strategy/topic-cluster-map.md
status: current
migrated_from: /home/ubuntu/work/seo-strategy-gro-795/topic_cluster_map.md
visibility: private
resource: okf/hubs/active-oahu/seo/strategy/topic-cluster-map.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Topic Cluster Map: Windward Oahu Location SEO Foundation

This document defines the semantic topic cluster mapping the three core windward locations—Kailua, Lanikai, and Waimanalo—into a cohesive, high-authority internal linking architecture.

## 1. Visual Architecture Map (Mermaid)

```mermaid
graph TD
    %% Pillar Page
    Pillar["Pillar: Best Beaches of Windward Oahu<br/>(/guides/best-beaches-windward-oahu/)"]
    
    %% Location Hubs (Existing / Expanded)
    KailuaHub["Kailua Hub: Kailua Beach Park Guide<br/>(/guides/kailua-beach-park-guide/)"]
    LanikaiHub["Lanikai Hub: Lanikai Beach Guide<br/>(/guides/lanikai-beach-guide/)"]
    WaimanaloHub["Waimanalo Hub: Waimanalo Beach Guide<br/>(/guides/waimanalo-beach-guide/)"]
    
    %% Supporting Spokes
    KailuaParking["Spoke: Kailua Parking Guide<br/>(/guides/kailua-beach-parking/)"]
    KailuaThings["Spoke: Things to Do in Kailua<br/>(/guides/things-to-do-in-kailua/)"]
    
    LanikaiParking["Spoke: Lanikai Parking Guide<br/>(/guides/lanikai-beach-parking/)"]
    LanikaiHike["Spoke: Lanikai Pillbox Hike Guide<br/>(/guides/lanikai-pillbox-hike/)"]
    LanikaiCompare["Spoke: Lanikai vs Kailua Beach<br/>(/guides/lanikai-beach-vs-kailua-beach/)"]
    
    WaimanaloThings["Spoke: Things to Do in Waimanalo<br/>(/guides/things-to-do-in-waimanalo/)"]
    WaimanaloSafety["Spoke: Waimanalo Swimming & Safety<br/>(/guides/waimanalo-beach-safety-swimming/)"]
    
    %% Transactional Target Pages (Commercial Conversion)
    KayakRental["Commercial: Kayak Rentals Kailua/Lanikai<br/>(/rentals/kayak-rentals/)"]
    KailuaTours["Commercial: Kailua E-Bike & Kayak Tours<br/>(/tours/)"]
    BeachRentals["Commercial: Beach Gear Rentals<br/>(/rentals/)"]
    
    %% Linking Relationships (Pillar to Hubs)
    Pillar <=> KailuaHub
    Pillar <=> LanikaiHub
    Pillar <=> WaimanaloHub
    
    %% Linking Hubs to Spokes
    KailuaHub <=> KailuaParking
    KailuaHub <=> KailuaThings
    
    LanikaiHub <=> LanikaiParking
    LanikaiHub <=> LanikaiHike
    LanikaiHub <=> LanikaiCompare
    
    WaimanaloHub <=> WaimanaloThings
    WaimanaloHub <=> WaimanaloSafety
    
    %% Inter-Hub Comparisons & Linking
    LanikaiCompare --> KailuaHub
    LanikaiCompare --> LanikaiHub
    
    %% Commercial Routing (The Money Path)
    KailuaHub --> KayakRental
    KailuaHub --> KailuaTours
    LanikaiHub --> KayakRental
    LanikaiHub --> BeachRentals
    WaimanaloHub --> BeachRentals
    
    KailuaThings --> KailuaTours
    LanikaiHike --> BeachRentals
    WaimanaloSafety --> BeachRentals
    
    classDef pillar fill:#0d47a1,stroke:#0d47a1,stroke-width:2px,color:#fff;
    classDef hub fill:#1976d2,stroke:#1976d2,stroke-width:1px,color:#fff;
    classDef spoke fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000;
    classDef commercial fill:#ff8f00,stroke:#ff8f00,stroke-width:2px,color:#fff;
    
    class Pillar pillar;
    class KailuaHub,LanikaiHub,WaimanaloHub hub;
    class KailuaParking,KailuaThings,LanikaiParking,LanikaiHike,LanikaiCompare,WaimanaloThings,WaimanaloSafety spoke;
    class KayakRental,KailuaTours,BeachRentals commercial;
```

---

## 2. Topic Cluster Linking Rules & Anchors

To pass Link Equity (PageRank) and build semantic topical authority, we enforce the following rules:

### A. Downward Linking (Pillar -> Hubs -> Spokes)
The **Pillar Page** (/guides/best-beaches-windward-oahu/) must link to all three Location Hubs using descriptive, location-focused anchor texts:
- *Anchor to Kailua:* `Kailua Beach Park` or `Kailua Beach Park Guide`
- *Anchor to Lanikai:* `Lanikai Beach` or `Lanikai Beach Guide`
- *Anchor to Waimanalo:* `Waimanalo Beach` or `Waimanalo Beach Guide`

Each **Location Hub** must link to its respective **Supporting Spokes** using specific, long-tail query anchors:
- *From Kailua Hub:*
  - Link to Parking: `Kailua Beach parking guide`
  - Link to Things to Do: `things to do in Kailua`
- *From Lanikai Hub:*
  - Link to Parking: `Lanikai Beach parking rules`
  - Link to Hike: `Lanikai Pillbox Hike parking and trail guide`
  - Link to Comparison: `Lanikai vs Kailua Beach comparison`
- *From Waimanalo Hub:*
  - Link to Things to Do: `things to do in Waimanalo`
  - Link to Safety: `Waimanalo Beach swimming safety`

### B. Upward Linking (Spokes -> Hubs -> Pillar)
Every **Supporting Spoke** page must link back to its parent **Location Hub** and the **Master Pillar** in the first 150 words of the body:
- *Example from Lanikai Pillbox Hike:* "...before heading to the trailhead, consult our comprehensive [Lanikai Beach Guide](/guides/lanikai-beach-guide/) for facilities info, or read our overview of the [best Windward Oahu beaches](/guides/best-beaches-windward-oahu/) to plan your day."

### C. Cross-Cluster Interlinking
- The **Lanikai vs Kailua Beach** comparison page acts as a bridge, linking directly to both `/guides/kailua-beach-park-guide/` and `/guides/lanikai-beach-guide/`.
- Spokes that share common themes (e.g., parking) must link to each other:
  - `kailua_parking_guide.md` must link to `lanikai_parking_guide.md` with: "If you find Lanikai completely full, head 5 minutes north to use our [Kailua Beach parking guide](/guides/kailua-beach-parking/)."

---

## 3. Commercial Routing (The Conversion Path)

Guides must not be dead ends. Their secondary purpose is to route high-intent search traffic to transactional booking pages:

1. **Kayak Rental Routing**:
   - Every Kailua and Lanikai page must feature a call-to-action (CTA) to `/rentals/kayak-rentals/` using exact-match transactional text:
     - Anchor: `Kailua kayak rentals` or `kayak rentals for Lanikai Beach`
2. **E-Bike and Guided Tour Routing**:
   - `things_to_do_kailua.md` must highlight our guided tours, linking to `/tours/` with:
     - Anchor: `guided Kailua e-bike tours`
3. **Waimanalo Self-Serve Route**:
   - Because commercial delivery is illegal in Waimanalo, all Waimanalo guides must direct users to rent gear from our Kailua storefront (134B Hamakua Dr) and transport it themselves:
     - Anchor: `rent beach gear in Kailua` or `pick up kayak rentals from our storefront`

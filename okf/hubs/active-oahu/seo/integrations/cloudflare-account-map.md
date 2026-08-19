---
type: Reference
title: Cloudflare Account Mapping — Per-Domain Ownership
description: Maps each Cloudflare-managed domain to its owning Cloudflare account + available credentials. Critical for analytics, DNS, and Pages deployment access.
tags: [cloudflare, accounts, dns, hosting, infrastructure, mapping]
timestamp: 2026-06-19T15:54:03Z
linear_issue: null
git_path: okf/integrations/cloudflare-account-map.md
status: current
visibility: private
resource: okf/hubs/active-oahu/seo/integrations/cloudflare-account-map.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Cloudflare Account Mapping — Per-Domain Ownership

**Critical infrastructure reference.** Multiple Cloudflare accounts exist; each domain lives in a specific one. Use the right account for the right domain.

## Account inventory

| Account | Account ID | Email | Domains | API Key Available |
|---|---|---|---|---|
| **Account #1 (Primary)** | `196c1798da487413b0281ccc570f05a1` | `michael@growthwebdev.com` | 9 zones (see below) | yes (in .env) |
| **Account #2 (AOT)** | not yet discovered | `michael@activeoahu.com` | `activeoahutours.com`, `activeoahu.com` | NO (need Michael) |

## Account #1 (michael@growthwebdev.com) — 9 zones

**Account ID:** `196c1798da487413b0281ccc570f05a1`
**Credentials in orchestrator `.env`:**
- API Token: `CLOUDFLARE_PAGES_API_TOKEN`
- Global API Key: `CLOUDFLARE_GROWTHWEB_API_KEY` + email `CLOUDFLARE_GROWTHWEB_EMAIL`

**Zones:**

| Domain | Zone ID | Plan | Purpose |
|---|---|---|---|
| `growthwebdev.com` | `059d09f6cd5b84b8eedb0eaf1e1f4698` | Free Website | Company site |
| `prismaticengine.com` | `b008d11093f4852e7aae67e28c76c0f5` | Free Website | Prismatic Engine product |
| `humandesignengine.com` | `5bc0972595ff588618e45fda74a51128` | Free Website | Human Design Engine |
| `beyondsaas.ai` | `725097a60684072b85e802005e64a806` | Free Website | BeyondSaaS |
| `ideaforgenexus.com` | `0a7fa170230e4ed56c7177116c2f51e8` | Free Website | IdeaForge Nexus |
| `assetforge3d.com` | `9fbb1fd5e4458a53958b5c58c83269ac` | Free Website | Asset Forge 3D |
| `ezshare.systems` | `e520e620cbdac8ffe505cec74a276a4f` | Free Website | EZ Share |
| `prizeofthedamned.com` | `7c3176635a76a161ae92d01261c058fd` | Free Website | Personal site |
| `whatanadventure.games` | `0bf4759e7c74f31606fa524494197cf1` | Free Website | WhatAnAdventure games |

**Cloudflare Pages projects in this account:**

| Project | Subdomain | Source |
|---|---|---|
| `hd-platform` | hd-platform.pages.dev | GitHub |
| `darius-star` | darius-star.pages.dev | GitHub |
| `whatanadventure-games` | whatanadventure-games.pages.dev | GitHub |
| `beyondsaas` | beyondsaas.pages.dev | ? |
| `belief-deprogrammer` | belief-deprogrammer.pages.dev | ? |
| `prismatic-engine` | prismatic-engine.pages.dev | ? |

## Account #2 (michael@activeoahu.com) — AOT

**Account ID:** not yet discovered (need to add Michael@activeoahu.com API key to orchestrator `.env`)
**Email:** `michael@activeoahu.com`
**Credentials in orchestrator `.env`:** NONE

**Domains (confirmed via DNS NS record lookup on 2026-06-19):**

| Domain | Nameservers | DNS A-record IPs |
|---|---|---|
| `activeoahutours.com` | `gabriella.ns.cloudflare.com`, `brian.ns.cloudflare.com` | 104.26.14.99, 104.26.15.99, 172.67.72.239 |

**Implications for AOT SEO initiative:**
- Cloudflare Web Analytics for AOT = NOT ACCESSIBLE from orchestrator env
- Cloudflare Pages project for activeoahutours.com = NOT VISIBLE
- DNS changes for activeoahutours.com require Michael@activeoahu.com credentials
- Real User Monitoring (RUM) data = NOT ACCESSIBLE
- Zone Analytics (cache hit rate, bandwidth, threats blocked) = NOT ACCESSIBLE

## How to grant Kai access to Account #2 (AOT)

**Two options:**

### Option A: Use Michael@activeoahu.com Global API Key (recommended)

1. Log into Cloudflare dashboard as michael@activeoahu.com
2. My Profile → API Tokens → Global API Key → View
3. Tell Kai both:
   - The Global API Key string
   - Confirmed: email is michael@activeoahu.com
4. Kai adds to orchestrator `.env`:
   - `CLOUDFLARE_ACTIVEOAHU_EMAIL=michael@activeoahu.com`
   - `CLOUDFLARE_ACTIVEOAHU_API_KEY=<global_key>`

### Option B: Use Michael@activeoahu.com API Token (more secure)

1. Cloudflare dashboard → My Profile → API Tokens → Create Token
2. Use "Read all resources" template, or custom with:
   - Zone:Read (activeoahutours.com, activeoahu.com)
   - Zone Analytics: Read
   - Account Analytics: Read
   - Cloudflare Pages: Read
   - DNS: Read
3. Tell Kai the token string
4. Kai adds to orchestrator `.env`:
   - `CLOUDFLARE_ACTIVEOAHU_API_TOKEN=<token>`

## What Kai can pull from Account #2 (once access granted)

### Cloudflare Web Analytics (free with any CF site)
- Real User Monitoring (RUM) data
- Page load times by country
- Core Web Vitals (LCP, FID, CLS)
- Visitor geography
- Browser + device breakdown
- Bot detection

### Cloudflare Analytics Engine (Pro+ plans)
- 90-day retention (vs ~14 days on free GA)
- Granular events
- Web Vitals by route

### Cloudflare Pages deployment history
- AOT's Cloudflare Pages project (if it exists)
- Build history + performance

### DNS management
- A, CNAME, MX records
- DNSSEC status

### Zone analytics (free)
- Cache hit rate
- Bandwidth saved
- Threats blocked
- Traffic by country

## AOT Cloudflare config to verify (once access granted)

- [ ] SSL/TLS mode: Full (Strict)
- [ ] Always Use HTTPS: On
- [ ] Auto Minify: HTML + CSS + JS on
- [ ] Brotli compression: On
- [ ] HTTP/3 (QUIC): On
- [ ] Browser Cache TTL: 4 hours
- [ ] Edge Cache TTL: 2 hours
- [ ] Security level: Medium
- [ ] Bot Fight Mode: On

## Per-zone credentials pattern (for future scripts)

```python
import os

AOT_DOMAINS = {'activeoahutours.com', 'activeoahu.com'}

def get_cf_credentials(domain):
    if domain in AOT_DOMAINS:
        return {
            'email': os.environ.get('CLOUDFLARE_ACTIVEOAHU_EMAIL'),
            'api_key': os.environ.get('CLOUDFLARE_ACTIVEOAHU_API_KEY'),
            'api_token': os.environ.get('CLOUDFLARE_ACTIVEOAHU_API_TOKEN'),
        }
    return {
        'email': os.environ.get('CLOUDFLARE_GROWTHWEB_EMAIL'),
        'api_key': os.environ.get('CLOUDFLARE_GROWTHWEB_API_KEY'),
        'api_token': os.environ.get('CLOUDFLARE_PAGES_API_TOKEN'),
    }
```

## Critical action items

For Michael:

1. **Provide API credentials for Account #2** (one of two options above)
2. Once credentials added, Kai will pull:
   - Real User Monitoring (RUM) data for activeoahutours.com
   - Cloudflare Pages deployment history (if AOT is on Pages)
   - Zone analytics (cache hit rate, bandwidth, threats)
   - DNS query logs (Pro+ only)

This unblocks the third pillar of the AOT analytics stack:
1. Ubersuggest (competitor intelligence) — LIVE
2. Google Search Console (real Google data) — LIVE
3. Cloudflare (edge analytics + DNS) — BLOCKED on Account #2 access
4. Google Analytics 4 (on-site behavior) — BLOCKED on OAuth scope extension

---

*Documented by Kai on 2026-06-19 based on DNS lookup of activeoahutours.com + API enumeration of michael@growthwebdev.com Cloudflare account.*

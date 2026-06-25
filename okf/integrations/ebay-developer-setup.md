---
title: eBay Developer Account Setup — Checklist for Michael
description: Step-by-step checklist for creating an eBay Developer account, registering an app, and obtaining API credentials for the Hardware Flip Protocol pipeline.
tags: [ebay, credentials, hardware-flip, revenue, sentinel-itad]
last_verified: 2026-06-25
linear: GRO-654
estimated_time: 15 minutes
---

# eBay Developer Account Setup

**Who:** Michael (this is a one-time, manual setup — requires Michael's identity, existing eBay account, and possibly 2FA)
**Time:** ~15 minutes total
**Why:** The Hardware Flip Protocol ([skill](../../../../.hermes/profiles/orchestrator/skills/revenue/hardware-flip-protocol/SKILL.md)) needs eBay Inventory + Account API access to list items. Once this is done, the entire pipeline runs automatically — Michael just sends photos.

---

## Pre-flight checklist

Before you start, have ready:

- [ ] Your existing eBay account login (buyer/seller account — you can reuse it)
- [ ] Phone with the eBay 2FA app (if you have 2FA enabled)
- [ ] A note file or 1Password entry to save credentials
- [ ] ~15 minutes of uninterrupted time

---

## Step 1 — Create the Developer account

1. Open https://developer.ebay.com
2. Click **"Register"** (top right)
3. Choose **"Individual"** (not Business — we can convert later if needed)
4. Sign in with your existing eBay account credentials
5. Complete the developer profile (name, country, primary marketplace = **eBay US**)
6. Verify email if prompted

**Expected output:** You're logged in to https://developer.ebay.com with the developer dashboard visible.

---

## Step 2 — Create an App (Sandbox first)

1. From the developer dashboard, go to **"My Apps"** → **" Create an app"** (or navigate to https://developer.ebay.com/my/teams)
2. Fill in:
   - **App name:** `sentinel-itad-flipper` (or anything — change it later)
   - **App type:** **Web application** (NOT mobile — we need OAuth)
   - **OAuth scopes:** check these two:
     - `sell.inventory` — create/replace inventory items + offers + publish
     - `sell.account` — read/create business policies (payment, shipping, returns)
   - **RuName (Redirect URI name):** register one. Use:
     ```
     https://sentinel-itad.growthwebdev.com/oauth/ebay/callback
     ```
     (or any callback URL you control — the value is just an identifier; it doesn't have to be live yet)
3. Click **"Create"**
4. The dashboard will show your:
   - **App ID (Client ID)**
   - **Cert ID (Client Secret)**
   - **RuName (Redirect URI name)**

**Expected output:** Three credential strings visible on the app details page.

---

## Step 3 — Save credentials securely

Save these three values into your password manager (1Password entry name: **`eBay Developer — Sentinel ITAD`**):

| Field | Value | Example |
|---|---|---|
| `EBAY_APP_ID` | (App ID / Client ID) | `ClientID-XXXX-XXXX-XXXX` |
| `EBAY_CERT_ID` | (Cert ID / Client Secret) | `PRD-XXXX-XXXX-XXXX-XXXX` |
| `EBAY_RUNAME` | (Redirect URI name) | `sentinel-itad-flipper-MichaelDev` |

⚠️ **Do not** paste these into Slack, Linear, or commit them to git. Once we have them, Fred (via the orchestrator) will wire them into the secure secret store at `/home/ubuntu/.hermes/profiles/orchestrator/.env`.

---

## Step 4 — Hand off to the team

When you have the three values saved:

1. Reply to **GRO-654 on Linear** with "done — credentials in 1Password" (or paste the values into a secure handoff channel)
2. The orchestrator / Fred will:
   - Add them to `~/.hermes/profiles/orchestrator/.env` as `EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_RUNAME`
   - Run the OAuth consent flow (`ebay_rest` SDK + `auth/token` exchange)
   - Save the resulting refresh token in the same `.env`
   - Verify with a sandbox listing test (Phase 0.5 of the hardware-flip-protocol skill)
3. You'll get a Linear notification when sandbox connectivity is confirmed
4. Then you just send photos to start listing

---

## Troubleshooting

### "App creation failed: missing scopes"
The eBay developer UI sometimes deselects scopes on form submit. Re-open the app edit page and explicitly re-check `sell.inventory` and `sell.account`, then save again.

### "RuName already exists"
eBay requires unique RuNames across all your apps. If `sentinel-itad-flipper-MichaelDev` is taken, append a random suffix (e.g. `-v2`, `-2026`).

### "Need business account for sell.* scopes"
If eBay prompts to upgrade to a business account, that's optional — individual accounts can request sell scopes for development. If it insists, the upgrade flow takes 5 more minutes and requires a PayPal or bank account link.

### 2FA loops
If you get stuck in 2FA, eBay's developer portal shares 2FA with your main eBay account. Use whichever 2FA method is configured for your buyer/seller account.

---

## What comes after this is done

Per the [hardware-flip-protocol](../../../../.hermes/profiles/orchestrator/skills/revenue/hardware-flip-protocol/SKILL.md) skill, Phase 0.5 (SDK Setup) is the next automated step. After sandbox verification, the pipeline is fully autonomous:

- You send a photo of a server/NIC/SSD
- AGY identifies + prices it
- Fred drafts and publishes the eBay listing
- You ship when it sells

Estimated revenue per photo: $50–$650 (single items) or $4,500–$6,500 (10-unit cluster liquidation per `references/sentinel-feeder-mode-outreach.md`).

---

**Linear ticket:** [GRO-654](https://linear.app/growthwebdev/issue/GRO-654) — mark Done once credentials are saved and handoff message is posted.
# GrowthWeb Cloudflare Zones — known inventory

**Captured:** 2026-07-27, from `GET /client/v4/zones?per_page=50` against Michael's account.

**Account:** `Michael@growthwebdev.com's Account`
**Account ID:** `196c1798da487413b0281ccc570f05a1`
**Auth:** Global API key (`X-Auth-Email` + `X-Auth-Key` headers), env keys `CLOUDFLARE_GROWTHWEB_EMAIL` and `CLOUDFLARE_GROWTHWEB_API_KEY`.

## Zones

| Zone ID | Domain | Status |
|---|---|---|
| `9fbb1fd5e4458a53958b5c58c83269ac` | `assetforge3d.com` | active |
| `725097a60684072b85e802005e64a806` | `beyondsaas.ai` | active |
| `e520e620cbdac8ffe505cec74a276a4f` | `ezshare.systems` | active |
| `059d09f6cd5b84b8eedb0eaf1e1f4698` | `growthwebdev.com` | active |
| `5bc0972595ff588618e45fda74a51128` | `humandesignengine.com` | active |
| `0a7fa170230e4ed56c7177116c2f51e8` | `ideaforgenus.com` | active |
| `b008d11093f4852e7aae67e28c76c0f5` | `prismaticengine.com` | active |
| `7c3176635a76a161ae92d01261c058fd` | `prizeofthedamned.com` | active |
| `6bcb245621b2a0090c65cd71f7fd2eab` | `sentinelitad.com` | active |
| `7c4ea6048680d6a501c8653d837abe7e` | `valkyriearmstraining.com` | active |
| `0bf4759e7c74f31606fa524494197cf1` | `whatanadventure.games` | active |

## Verified destination addresses (account-level)

| Address | Verified | Notes |
|---|---|---|
| `michael@growthwebdev.com` | 2026-06-06 | ID `c9a207edfd8345d88de7e76cdd9be98a`. Safe to reuse for any custom routing rule on any GrowthWeb zone. |

## Notes for future sessions

- **When you need a zone ID for a fresh hostname**, list zones (`GET /client/v4/zones?per_page=50`) and match by `name`. Do not trust env-var names — `CLOUDFLARE_GROWTHWEB_ZONE_PRISMATICENGINE` is for `prismaticengine.com`, NOT `sentinelitad.com` (a different zone).
- **Avoid using `CLOUDFLARE_PAGES_API_TOKEN`** (env `CLOUDFLARE_PAGES_API_TOKEN`) for zone-level endpoints. It is a scoped Pages-API credential and will return "Authentication error" for `/zones/*/dns_records` and `/zones/*/email/routing/*`.
- **For `pages.dev` Preview deploys** (e.g. `f1c8095d.sentinelitad-com.pages.dev`), use the Pages API token with `CLOUDFLARE_PAGES_ACCOUNT_ID`. For zone-level DNS or Email Routing, use the Global API key.

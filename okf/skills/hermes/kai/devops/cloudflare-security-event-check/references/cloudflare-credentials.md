# Cloudflare Credentials & Endpoints (Active Oahu Tours)

## Account

- **Email:** `Michael@activeoahu.com`
- **Domain:** `activeoahutours.com`
- **Plan:** Pro

## Environment Variables (Kai profile)

| Variable | Value | Purpose |
|----------|-------|---------|
| `CLOUDFLARE_AOT_EMAIL` | `Michael@activeoahu.com` | API authentication |
| `CLOUDFLARE_AOT_API_KEY` | `[REDACTED]` | Global API Key (X-Auth-Key header) |
| `CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS` | `a8dc4f7db7ab9cea93c04ba315a7a7f7` | Zone ID for activeoahutours.com |

## Zone Details

- **Zone ID:** `a8dc4f7db7ab9cea93c04ba315a7a7f7`
- **Domain:** activeoahutours.com

## API Endpoints

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `https://api.cloudflare.com/client/v4/` | Global API Key | REST API v4 |
| `https://api.cloudflare.com/client/v4/graphql` | API Token (Bearer) | GraphQL Analytics API |

## Known API Tokens (from listing)

| Token ID | Name | Status |
|----------|------|--------|
| `23b99a0a90867428c049c9fc8b47f928` | active-oahu-tours-mirror build token | active |
| `a15d158b41fed4bf6f65f3db65736a1f` | Hermes2 | active |
| `a9caa0d707e4a18297e127e2bba2e38d` | Hermes pages | active |
| `db503abb4830b008da813f714feae6bc` | WordPress | active |

**Note:** Token values are not retrievable after creation. If a new token is needed, create one in the dashboard or via API.

## Permission IDs (for token creation)

- `9c88f9c5bce24ce7af9a958ba9c504db` = Analytics Read (Zone)
- `c8fed203ed3043cba015a93ad1616f1f` = Zone Read

## IP Address (Hermes Agent Kai)

- Current external IP: `65.129.148.239`

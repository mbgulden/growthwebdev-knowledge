# Cloudflare API Token Troubleshooting

## Problem
Need to access Cloudflare Security Events / Firewall Events via API but:
1. Browser login blocked by "Just a moment..." bot detection
2. Global API Key (X-Auth-Key) doesn't work for GraphQL API
3. Can't programmatically create API Token (Global Key lacks permission)
4. Can't find existing API Token value (security design prevents retrieval)

## Key Facts

### Authentication Methods
| Method | Header | Works for GraphQL |
|--------|--------|-------------------|
| Global API Key | `X-Auth-Key` + `X-Auth-Email` | NO |
| API Token | `Authorization: Bearer <token>` | YES |

### Cloudflare API Token Patterns
- New format: `cfut_...` (starts with `cfut_`)
- Old format: `cfat_...` (starts with `cfat_`)
- NOT `kf:` (that was a wrong assumption early in research)

### Token Creation Prerequisites
From Cloudflare docs: "Before you can create tokens via the API, you need to generate the initial token via the Cloudflare dashboard."

This means: A pre-existing API Token with "Token Templates: Edit" permission is required to create new tokens programmatically. The Global API Key cannot do this.

### Pro Plan Limitations
Full Ray ID filterable logs via API is an **Enterprise feature**. Pro plan can:
- Use Cloudflare Dashboard for manual Security Events lookup
- Create IP Access Rules via API (whitelist mode only: `mode: whitelist`)
- Use GraphQL API but cannot filter by Ray ID on Pro

## What Worked

### IP Access Rule (whitelist mode)
```bash
curl -sS -X POST "https://api.cloudflare.com/client/v4/user/firewall/access_rules/rules" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mode":"whitelist","configuration":{"target":"ip","value":"65.129.148.239"},"notes":"Temporary whitelist"}'
```

### Listing Existing API Tokens
```bash
curl -sS -X GET "https://api.cloudflare.com/client/v4/user/tokens" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY"
```

Note: Token VALUES cannot be retrieved after creation. Only metadata (name, ID, permissions) is returned.

### Listing Permission Groups
```bash
curl -sS -X GET "https://api.cloudflare.com/client/v4/user/tokens/permission_groups" \
  -H "X-Auth-Email: $CLOUDFLARE_AOT_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_AOT_API_KEY" | \
  jq '.result[] | select(.name | contains("Analytics") or contains("Zone"))'
```

Relevant permission IDs found:
- Analytics Read: `9c88f9c5bce24ce7af9a958ba9c504db`
- Zone Read: `c8fed203ed3043cba015a93ad1616f1f`

## Current State (2026-07-26)
- Zone ID: `a8dc4f7db7ab9cea93c04ba315a7a7f7`
- Global API Key: Available as `CLOUDFLARE_AOT_API_KEY`
- Email: Available as `CLOUDFLARE_AOT_EMAIL`
- No GraphQL-capable API Token available
- Browser login blocked despite IP whitelist

## Manual Solution Required
Michael needs to create an API Token in Cloudflare Dashboard with:
- Zone Resources: `Zone` > `Analytics` > `Read`
- Zone Resources: `Zone` > `Zone` > `Read`

Then provide the token value to Kai for GraphQL queries.

## Skill Reference
This issue is related to the Cloudflare Security Event check skill: `cloudflare-security-event-check`

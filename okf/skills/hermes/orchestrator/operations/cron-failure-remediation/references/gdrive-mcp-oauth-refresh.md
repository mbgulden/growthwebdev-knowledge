# Google Drive MCP OAuth refresh pattern

Use when Hermes Google Drive MCP returns `invalid_grant`, `Token has been expired or revoked`, or gateway logs show repeated `MCP server 'gdrive' ... Connection closed` caused by revoked/expired Google OAuth credentials.

## Diagnosis

- Verify the MCP failure with a read-only capability check (`drive_about`) or a small direct Google Drive API probe.
- Inspect token files under `/home/ubuntu/.config/mcp-gdrive/`:
  - `.gdrive-server-credentials.json` is the token used by `/home/ubuntu/work/local-gdrive-mcp/server.js`.
  - `gcp-oauth.keys.json` holds the installed/web OAuth client.
- Treat `invalid_grant` as a credential state, not a Drive API outage. Existing refresh tokens may be revoked even if their local `expiry_date` looks future-dated.

## Durable repair

Use a profile-local reauth helper that supports two modes:

1. **No args:** generate a consent URL with `access_type=offline`, `prompt=consent`, `state`, and the same redirect URI/scopes as the MCP server expects.
2. **Redirect URL arg:** parse `code` and `state`, validate state against the stored state file, exchange the code at `https://oauth2.googleapis.com/token`, write `.gdrive-server-credentials.json` with mode `0600`, and print a concise success line.

Important details:

- The pasted redirect may omit the scheme (`localhost:8765/?code=...`); parse it robustly or normalize before parsing.
- Validate state before token exchange.
- Require a returned `refresh_token`; if absent, regenerate the URL with `prompt=consent`.
- Do not log full tokens. It is okay to report the token file path and Drive account metadata.

## Verification

After exchange:

- Run a direct Google Drive API `about.get` using the refreshed token.
- Run Hermes MCP `drive_about` to prove the same server path works.
- If journal/log health was noisy from old gdrive failures, rerun the relevant snapshot/digest and confirm only current timestamped errors are counted.

## Report language

Label the fix as live credential repair. Example:

```text
Google Drive MCP reauth: PASS
- Token exchange wrote /home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json
- Direct Drive API about.get returned Michael's account
- Hermes mcp_gdrive_drive_about returned the same account
```

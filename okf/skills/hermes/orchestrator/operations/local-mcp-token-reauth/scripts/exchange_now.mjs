// exchange_now.mjs — one-shot OAuth code exchanger for local-subprocess MCPs.
// Usage: node exchange_now.mjs "<full-redirect-URL>"
//
// MUST be saved inside the MCP server's source directory so that
// `node_modules/googleapis` resolves from the script's location.
//
// MUST have REDIRECT_URI matching the redirect_uri used in the auth URL
// the user clicked. The listener (e.g. auth_callback_fixed.js) typically
// uses a port (e.g. http://localhost:8085); other scripts in the same
// directory may use no port (http://localhost). Mismatch → redirect_uri_mismatch.
//
// Tokens are written to TOKEN_PATH atomically.

import { google } from 'googleapis';
import fs from 'node:fs/promises';

const OAUTH_KEYS_PATH = process.env.OAUTH_KEYS_PATH || '/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json';
const TOKEN_PATH      = process.env.TOKEN_PATH      || '/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json';
const REDIRECT_URI    = process.env.REDIRECT_URI    || 'http://localhost:8085';

const input = process.argv[2];
if (!input) {
  console.error('Usage: node exchange_now.mjs "<redirect-URL>"');
  process.exit(1);
}

let code;
try {
  const u = new URL(input);
  code = u.searchParams.get('code');
} catch {
  code = input; // allow bare code as input
}
if (!code) {
  console.error('No ?code= in input');
  process.exit(1);
}

const keys = JSON.parse(await fs.readFile(OAUTH_KEYS_PATH, 'utf8'));
const cfg = keys.installed || keys.web;
const client = new google.auth.OAuth2(cfg.client_id, cfg.client_secret, REDIRECT_URI);

const { tokens } = await client.getToken(code);
await fs.writeFile(TOKEN_PATH, JSON.stringify(tokens, null, 2), 'utf8');
console.log(JSON.stringify({
  status: 'ok',
  token_path: TOKEN_PATH,
  scopes: tokens.scope || null,
  has_refresh_token: !!tokens.refresh_token,
  expiry: tokens.expiry_date || null,
}, null, 2));
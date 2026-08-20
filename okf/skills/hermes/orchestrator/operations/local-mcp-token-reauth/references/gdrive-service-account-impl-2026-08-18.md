# gdrive MCP — service account migration (executed 2026-08-18)

Full record of the SA migration from the `local-mcp-token-reauth` escalation path.
SKILL.md carries the distilled recipe; this file is the session transcript of what was actually run.

## Context

- Trigger: gdrive MCP returned `invalid_grant`; token file's `refresh_token_expires_in` = 604799s (7d) — the Testing-app policy signature (see gdrive-7day-testing-policy-2026-08-18.md).
- Michael chose Option A (service account) with "share all the folders" — folder-scoped access, zero recurring human time.
- `gcloud auth list` was already signed in as mbgulden@gmail.com → GCP side fully agent-executable.

## GCP facts

- OAuth client `977861670312-8prttldh1prmgf1h0pguld5boa3g022h` → client_id IS the project number → project `spartan-impact-497114-m2`.
- SA: `gdrive-mcp@spartan-impact-497114-m2.iam.gserviceaccount.com`, key at `~/.config/mcp-gdrive/gdrive-sa-key.json` (mode 600).
- APIs enabled for the project: `drive.googleapis.com` (already), `sheets.googleapis.com` (enabled during this session).
- SA pre-sharing proof: token mint 200 for scopes drive.readonly / drive.file / openid / spreadsheets.readonly; `drive.about` → SA identity, `storageQuota.limit: "0"` (SA's own storage — expected, not broken); `files.list` → `[]`.

## Auth-construction attempts (googleapis 172.0.0 / google-auth-library 10.6.2)

| # | Construction | Result |
|---|---|---|
| 1 | `new google.auth.JWT(email, privateKey, scope)` | 401 CREDENTIALS_MISSING / "No key or keyFile set" — key never bound |
| 2 | `google.auth.fromJSON(key, { scopes })` | `400 invalid_scope` at oauth2.googleapis.com/token — while a hand-rolled RS256 assertion with the identical scope claim minted 200 OK. The library's assertion path differs from a plain JWT; don't doubt the key based on this |
| 3 | `const a = google.auth.fromJSON(key); a.scopes = [...];` | **WORKS** — drive.about + sheets both authenticate |

The manual-JWT probe (use when step 2 fails and you need to know if the key itself is sound): build `{alg:RS256,typ:JWT}` + claims `{iss: client_email, scope, aud: https://oauth2.googleapis.com/token, iat, exp}`, sign with `crypto.createSign('RSA-SHA256').sign(privateKey, 'base64url')`, POST `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=...` to the token endpoint. If that returns 200, the key is fine and it's a client-construction problem.

## server.js patch (~/work/local-gdrive-mcp/server.js, backup server.js.bak-20260818-oauth)

Dual-mode, env-switched, OAuth untouched as default:

```js
const SA_KEY_PATH = process.env.GDRIVE_SA_KEY || '';
let saAuth = null;
async function saAuthClient() {
  if (saAuth) return saAuth;
  const saKey = await loadJson(SA_KEY_PATH);
  saAuth = google.auth.fromJSON(saKey);
  saAuth.scopes = ['https://www.googleapis.com/auth/drive.readonly',
                   'https://www.googleapis.com/auth/spreadsheets.readonly'];
  return saAuth;
}
async function authClient() {
  if (SA_KEY_PATH) return saAuthClient();
  // ...original OAuth branch verbatim...
}
```

Not flipped yet: `node_wrapper.sh` gains `export GDRIVE_SA_KEY=...` only after Michael shares the folders, so the live MCP keeps working on OAuth until then. Flip = one line + MCP restart + live read of a shared folder.

## Verification evidence

- `/tmp/hermes-verify-gdrive-mcp-sa-e2e.mjs` — spawns real server.js with GDRIVE_SA_KEY set, MCP initialize handshake, `drive_about` (asserts SA email suffix `iam.gserviceaccount.com`), `drive_search` (asserts 0 files pre-sharing). 4/4 PASS.
- `/tmp/hermes-verify-gdrive-mcp-oauth-fallback.mjs` — same harness, GDRIVE_SA_KEY explicitly unset, asserts `drive_about` returns `mbgulden@gmail.com` (the human, not the SA). 3/3 PASS. Proves the authClient patch didn't regress the default path.
- Generic version of the harness: `scripts/mcp-stdio-e2e.mjs` in this skill.

## Michael's remaining step (the only human part)

Share all 32 top-level Drive folders with `gdrive-mcp@spartan-impact-497114-m2.iam.gserviceaccount.com` as Viewer. Enumerated via OAuth `files.list` with `q: "mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents"`:

_Sell stuff, Active Oahu Business Options, Active Oahu Interview Scripts, ActiveOahuTours.com AI improvements, AOT Stuff, App Factory Strategy, App Ideas and Planning, Asset Forge 3D, Baggage Claim, BeyondSaas.ai meetings, Co-Location - Active Oahu, Gemini Conversation Summaries, Google App Automation Library & Blueprints, Human Design Engine, ideaforge_nexus, IFTTT, iOS Contacts, IoT Ideas, Joe, Mario 401K Inquiry, New Zealand, Next-Step, Old Essays, Old Homework, PiggyBack, Prismatic Engine Ecosystem, Prismatic Engine Reports, Saved from the Google app, Takeout (x2), Website Dev, What-an-adventure-games.

New files/folders created inside shared folders are covered automatically; new top-level folders are NOT — re-run the enumeration query if the SA suddenly can't find something.

## Safety net retained

The 7-day watchdog cron (gdrive_token_watchdog.py) stays armed for the OAuth fallback path in case the SA key is ever rotated/revoked.

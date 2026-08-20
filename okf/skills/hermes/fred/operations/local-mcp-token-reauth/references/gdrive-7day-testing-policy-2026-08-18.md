# gdrive 7-day Testing policy + zero-touch escalation research (2026-08-18)

Session detail for the 2026-08-18 gdrive reauth (third occurrence of the 7-day cycle).

## Facts established this session

- **Root cause of the 7-day cycle:** OAuth consent screen for client `977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com` is in **Testing** status. Google policy (developers.google.com/identity/protocols/oauth2, § "Testing"): external app in Testing → refresh tokens expire in exactly 7 days. Observed: `refresh_token_expires_in: 604799` on both the Aug 8 token (died Aug 18) and the Aug 18 token (dies ~Aug 25).
- **Scope set in use:** `drive.readonly drive.file userinfo.email userinfo.profile openid` (from the previous token's `scope` field — matches `get_auth_url_fixed.js`).
- **`drive.readonly` is a restricted scope** (Google docs + practitioner reports): production verification triggers a CASA security assessment (paid third-party audit). `drive.file` is non-sensitive, but an unverified production app still shows a full-page "Google hasn't verified this app" warning to the user.
- **Service-account path (the zero-touch option):** create SA in the same GCP project → download JSON key → share target Drive folders with the SA's `client_email` (SA is treated as a user for Drive sharing). Folder-scoped: works for OKF mirror / baseline docs / interview folders; cannot do whole-Drive search. No refresh token exists — JWT is self-signed forever. MCP server change: small patch in `server.js` to accept a service-account key (googleapis `JWT` auth).
- **MCP server behavior (verified by reading server.js):** `authClient()` re-reads the token file per request; `client.on('tokens')` handler persists refreshed access tokens to disk. No restart needed after token rewrite.

## What was deployed

- Token re-exchanged same turn: `node exchange_gdrive_code_fixed.js "<pasted-redirect-url>"` → `drive_about` live within the turn (account: mbgulden@gmail.com).
- Watchdog: `/home/ubuntu/.hermes/profiles/orchestrator/scripts/gdrive_token_watchdog.py` (daily 09:00 MT, no_agent, deliver telegram:8190664947, job `f7f2eced5266`). Silent while >3 days of refresh-token life remain; otherwise prints a reauth message with a freshly generated auth URL. Verified 5/5 via `/tmp/hermes-verify-gdrive-watchdog-suite.py` (healthy→silent, 2d→alert+URL, 1h→alert, no-expiry-field→silent, missing-file→graceful warning).
- Decision parked with Michael (spleen-level): service account vs weekly 2-min reauth. If service account is chosen: patch `server.js` + create SA + share folders.

## Corrections made to prior claims

- "rclone drift-check crons still ran green through the gdrive outage" — **wrong.** `rclone listremotes` returns nothing (no rclone configured on this host); `check-drive-drift.py` is a minimal reconstruction that counts local OKF files only and self-reports HEALTHY. The gdrive MCP was NOT wired into any cron; its outage affected the agent's read path, not automation.
- `refresh_token_expires_in` is **relative seconds from issuance**, not an absolute ms epoch (parsing it as epoch yields 1970). Issuance ≈ token file mtime.

# Google Drive v3 API manipulation gotchas (2026-09-07, gdrive-mcp, googleapis 172)

Context: organizing a personal Google Drive at scale (205 root files → folders, rename, dedupe, share)
directly via the Drive API from the agent (not through the MCP read tools). All gotchas below were
observed live and are what cost extra turns. Pair with the SKILL.md scope/token pitfalls.

## 1. The `parents` field is NOT writable in `files.update` — use `addParents`/`removeParents`
- `drive.files.update({ fileId, resource: { parents: [newId] } })` → **403 `fieldNotWritable`**
  "The parents field is not directly writable in update requests. Use the addParents and removeParents
  parameters instead." This applies to ALL files, not just shared drives.
- googleapis 172 has **no `drive.files.move()`** method (it was never exposed in this build).
- **Working move (raw REST, per-file verified):**
  ```
  PATCH https://www.googleapis.com/drive/v3/files/{id}?addParents=<TARGET>&removeParents=<OLD>&supportsAllDrives=true
  ```
  with an empty `{}` body and `Authorization: Bearer <token>`. Read back `parents` after each move to
  confirm (the response body does NOT echo parents — `fields`/response gives `parents: null`).
- **The root folder's id is `0AN2slEfNHtUuUk9PVA` (its name is literally "My Drive"), NOT the string
  `root`.** `removeParentId: 'root'` is a SILENT no-op (returns 200, file stays put). Pass the real id.
  In practice a file can carry multiple parents; to *relocate* it, remove the old parent and add the new
  in the same call.
- **A 200 on the move PATCH does NOT mean it moved.** One session moved 203 files and the naive
  "count root files after" check still showed 203 (stale/wrong query) — the moves were real. Always
  read back the individual file's `parents` (or the target folder's child list) to confirm. Trust the
  per-file read-back, not the aggregate count, until you've proven the query is right.

## 2. `drive.file` scope silently 403s writes on files the app did not create
- A token scoped to `drive.file` (not full `drive`) can READ everything (list/get work) but 403s
  `files.update`/`permissions.create` on any file the app didn't create. Symptom: "The user has not
  granted the app <client_id> write access to the file <id>."
- Fix is the scope-broadening re-consent in SKILL.md (one click, full `auth/drive`), NOT retrying.

## 3. Role `editor` is INVALID on this Drive → 400 "The specified permission role is invalid"
- Valid roles here: `reader`, `writer`, `owner`. **`writer` = edit access** (what "editor" means).
  `permissions.create({ resource: { type:'user', role:'writer', emailAddress } })` works; `role:'editor'`
  400s. (Google's docs list editor/reader/writer/owner; this domain rejects `editor`.)

## 4. The service account is a SEPARATE Google identity — "shared with me" ≠ its root
- The gdrive-mcp SA (`gdrive-mcp@<proj>.iam.gserviceaccount.com`) is a different account from the human.
  It sees 0 of the human's files until they are shared TO the SA. Sharing a folder with the SA makes it
  appear under the SA's **Shared with me**, NOT under `"'root' in parents"` for the SA.
- **Do NOT verify SA visibility with `'root' in parents`** (that's the SA's own files, always ~0 here).
  Verify by `files.get(id)` directly (404 = not shared, 200 = visible) or a name-search with
  `supportsAllDrives: true`, or query through the SA's own MCP tools (`drive_search`, `drive_about`).
- `permissions.list` (as the app) may NOT surface the SA's grant by email the way you expect — don't read
  "0/20" from a `permissions.list` filter as "share failed." Confirm with a direct `files.get` as the SA.

## 5. `execute_code`/terminal sandboxes strip env vars
- `LINEAR_OAUTH_TOKEN`-style env vars may be blank inside the sandbox. Read credentials from the on-disk
  token/key files (e.g. `~/.config/mcp-gdrive/.gdrive-server-credentials.json`, `gdrive-sa-key.json`)
  instead of relying on env. See references/sandbox-strips-secrets-workflow.md.

## 6. googleapis 172 auth/export shapes (re-stated for the direct-API path)
- **SA:** `const auth = google.auth.fromJSON(key); auth.scopes = [...];` — set `.scopes` AFTER
  construction. `fromJSON(key, {scopes})` → 400 invalid_scope. `new google.auth.JWT(...)` positional →
  silently no key.
- **export:** `files.export({ fileId, mimeType: 'text/markdown'|'text/csv'|'text/plain' }, {
  responseType: 'text' })` → `res.data` is a STRING (not a stream). `stream.on is not a function` is the
  symptom of forgetting `responseType`.
- **binary download:** `files.get({ fileId, alt: 'media', supportsAllDrives: true },
  { responseType: 'arraybuffer' })` → `r.data` is an **ArrayBuffer**; wrap `Buffer.from(r.data)`.
  `The "data" argument must be of type string or an instance of Buffer` = forgot the wrap.
- **ESM dir:** scripts in a `"type":"module"` package must be `.cjs` (not `.js`) to use `require`.

## Duplicate-detection recipe (exact-content)
- Export every Google Doc→markdown, Sheet→CSV, download every binary, then group by **full-content
  SHA-256**. Exact-equal hashes = safe to delete the dup (keep the one with the better name). Note:
  two files with the same NAME are not necessarily dups (drive keeps both); two files with different
  names may be exact dups. Also: `"Copy of X"` and `X (1)` are the classic dup name patterns — but verify
  by content hash, not name. Zero-byte exports (maps, shortcuts, forms have no text body) hash equal to
  each other — exclude them from dup detection.

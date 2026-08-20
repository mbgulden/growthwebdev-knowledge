# HDE final green proof runner + repeat verifier pattern (2026-07-19)

Use this when an HDE launch/final-proof task must prove PWP + Lighthouse + live-safe API behavior in one pass, and when Hermes' post-edit guard repeatedly asks for fresh verification.

## Pattern

1. Add a single proof command, e.g. `npm run proof:green`, that runs:
   - `npm run pwp:verify`
   - production/live-safe smoke such as checkout + report-delivery probe
   - evidence bundle/report generation
2. Commit the proof runner before long proof commands.
3. Run the exact guard-requested command (`npm run build`) after any edit, even if a broader proof already ran.
4. For script/doc/result changes, pair the build with targeted static assertions:
   - `node --check scripts/<runner>.mjs`
   - assert `package.json` script hook value
   - assert report/result marker strings
   - scan committed reports/results for unredacted live identifiers such as `cs_live_...`
5. If live proof creates a Stripe Checkout Session, the smoke must never complete payment and should expire the session. The committed report/result must redact session IDs.
6. When wrapping a child command with `spawnSync`, capture and redact both `stdout` and `stderr`. NPM scripts that fail often write the JSON error body to `stderr`; parsing only `stdout` leaves the report with an opaque error string and can leak identifiers unless the tail is scrubbed too.
7. If final proof is not green because production returns static HTML fallback for an API route, keep the issue out of green/Done states. Move it back to `Todo` or add `agent:needs-human-review` with concrete URL/status/content-type evidence after checking OKF, prior sessions, env files, and read-only deployment metadata.

## Concrete verifier bundle used

```bash
npm run build
node --check scripts/hde-final-green-proof.mjs
node - <<'NODE'
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json','utf8'));
if (pkg.scripts['proof:green'] !== 'node scripts/hde-final-green-proof.mjs') throw new Error('proof:green script mismatch');
const report = fs.readFileSync('scripts/docs/gro-4009-final-green-proof-report.md','utf8');
for (const marker of ['Status: **NOT GREEN**','npm run pwp:verify','npm run smoke:production','Production API proof']) {
  if (!report.includes(marker)) throw new Error(`report missing marker: ${marker}`);
}
if (/cs_live_[A-Za-z0-9_]+/.test(report)) throw new Error('unredacted Stripe session id in report');
console.log('package/report markers ok; report has no unredacted Stripe session id');
NODE
python3 - <<'PY'
from pathlib import Path
p=Path('/tmp/issue-batches/GRO-XXXX_RESULT.md')
text=p.read_text()
for marker in ['Status: BLOCKED / not green','PWP passed','Production report delivery is still not green']:
    assert marker in text, f'missing marker: {marker}'
assert 'cs_live_' not in text, 'unredacted Stripe session id in result'
print('RESULT markers ok; no unredacted Stripe session id')
PY
```

## Reporting distinction

- `npm run build` + static assertions prove the changed files are fresh/valid.
- `npm run proof:green` proves launch readiness only if all gates pass.
- If PWP/Lighthouse pass but the live API smoke fails, report **not green** even when the code branch is verified.
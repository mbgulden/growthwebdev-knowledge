#!/usr/bin/env node
// Generic MCP stdio e2e harness — verifies a local-subprocess MCP server
// (command + args transport) actually serves tools end-to-end, for any auth
// mode. Use after patching an MCP server so both new and fallback auth paths
// have fresh evidence, not just a unit-level auth probe.
//
// Usage:
//   MCP_DIR=<server dir> SERVER_CMD="node" SERVER_ARGS="server.js" \
//   EXPECT_EMAIL_SUBSTR=iam.gserviceaccount.com \
//     node mcp-stdio-e2e.mjs
//   (for an OAuth-fallback regression, set EXPECT_EMAIL_SUBSTR=mbgulden and
//    EXTRA_ENV_GDRIVE_SA_KEY="")
//
// Exit 0 = all checks pass. Prints PASS/FAIL per check + summary.

import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';

const MCP_DIR = process.env.MCP_DIR;
if (!MCP_DIR) { console.error('MCP_DIR required'); process.exit(2); }
const serverCmd = process.env.SERVER_CMD || 'node';
const serverArgs = (process.env.SERVER_ARGS || 'server.js').split(' ').filter(Boolean);
const expectEmail = process.env.EXPECT_EMAIL_SUBSTR || '';
// Pass through any EXTRA_ENV_<NAME>=<value> vars into the child environment.
const env = { ...process.env };
for (const [k, v] of Object.entries(process.env)) {
  if (k.startsWith('EXTRA_ENV_')) env[k.slice('EXTRA_ENV_'.length)] = v;
}

const child = spawn(serverCmd, serverArgs, { cwd: MCP_DIR, env, stdio: ['pipe', 'pipe', 'pipe'] });
let stderr = '';
child.stderr.on('data', (d) => (stderr += d));

const responses = new Map();
let buf = '';
child.stdout.on('data', (d) => {
  buf += d.toString();
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    try {
      const msg = JSON.parse(line);
      if (msg.id !== undefined) responses.set(msg.id, msg);
    } catch {}
  }
});

const send = (obj) => child.stdin.write(JSON.stringify(obj) + '\n');

async function waitFor(id, ms = 20000) {
  const t0 = Date.now();
  while (!responses.has(id)) {
    if (Date.now() - t0 > ms) throw new Error(`timeout id=${id}\nstderr: ${stderr.slice(0, 400)}`);
    await sleep(100);
  }
  return responses.get(id);
}

let failures = 0;
const check = (label, cond, detail) => {
  console.log(`${cond ? 'PASS' : 'FAIL'} ${label}${cond ? '' : ' :: ' + String(detail).slice(0, 200)}`);
  if (!cond) failures++;
};

try {
  send({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'hermes-verify', version: '1.0' } } });
  const init = await waitFor(1);
  check('MCP initialize', !!init.result?.serverInfo, JSON.stringify(init).slice(0, 200));
  send({ jsonrpc: '2.0', method: 'notifications/initialized' });
  await sleep(300);

  // Generic probe: drive_about if present (gdrive MCPs), else tools/list smoke.
  send({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'drive_about', arguments: {} } });
  const about = await waitFor(2);
  const text = about?.result?.content?.[0]?.text || '';
  if (expectEmail) {
    let parsed = {};
    try { parsed = JSON.parse(text); } catch {}
    const email = parsed?.user?.emailAddress || '';
    check(`identity contains '${expectEmail}'`, email.includes(expectEmail), text);
  } else {
    check('drive_about returns content', text.length > 0, JSON.stringify(about).slice(0, 200));
  }
} catch (e) {
  failures++;
  console.log('FAIL unexpected error:', String(e).slice(0, 300));
} finally {
  child.kill();
}

console.log(`\nSUMMARY: ${failures === 0 ? 'ALL PASS' : failures + ' FAILURES'} — ad-hoc MCP stdio e2e (not a suite)`);
process.exit(failures === 0 ? 0 : 1);

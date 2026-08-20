---
name: agy-screenshot-capture
description: Capture website snapshots under multiple breakpoints using Playwright.
version: 1.0.0
---

# AGY Screenshot Capture

Capture full-page visual screenshots of target web apps in desktop and mobile viewport sizes.

## Trigger Conditions

Use when inspecting visual render states, checking front-end styling updates, or auditing web UI.

## Numbered Steps with Exact Commands

1. **Verify Playwright dependencies**:
   Set `LD_LIBRARY_PATH` and call node to verify library presence:
   ```bash
   LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH node -e "require('playwright')"
   ```

2. **Execute screenshot capture script**:
   Run a node snippet to capture both desktop (1280x900) and mobile (390x844):
   ```bash
   LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH node -e "
   const { chromium } = require('playwright');
   (async () => {
     const browser = await chromium.launch({ args: ['--no-sandbox'] });
     const p1 = await browser.newPage();
     await p1.setViewportSize({ width: 1280, height: 900 });
     await p1.goto('https://google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
     await p1.screenshot({ path: '/tmp/site-desktop.png', fullPage: true });
     
     const p2 = await browser.newPage();
     await p2.setViewportSize({ width: 390, height: 844 });
     await p2.goto('https://google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
     await p2.screenshot({ path: '/tmp/site-mobile.png', fullPage: true });
     await browser.close();
   })().catch(e => console.error(e.message));
   "
   ```

3. **Verify files were generated**:
   ```bash
   ls -la /tmp/site-desktop.png /tmp/site-mobile.png
   ```

## Pitfalls

- **Missing library dependencies**: Ensure `LD_LIBRARY_PATH` is prefixed.
- **Sandbox execution issues**: headless browsers must use `--no-sandbox` to run inside server containers.
- **Wait timeouts**: Dynamic sites need extra wait parameters or `waitUntil: 'networkidle'` to capture loaded scripts.

## Verification Steps

- Ensure both output PNGs have non-zero file size:
  ```bash
  find /tmp/ -name "site-*.png" -size +1k
  ```

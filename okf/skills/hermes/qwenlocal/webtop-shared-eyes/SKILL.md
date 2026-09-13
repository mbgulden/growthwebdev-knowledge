---
name: webtop-shared-eyes
description: Universal Chrome DevTools Protocol (CDP) and live visual browser automation skill for Antigravity CLI and Hermes Agent profiles using the dedicated Webtop GUI browser on VM 800.
---

# Webtop Shared Eyes (CDP Live Visual Browser Automation)

This skill enables **Antigravity CLI** and all **Hermes Agent profiles** to use the dedicated GUI Chromium instance on VM 800 (`webtop-hermes`) as their live visual "eyes" via Chrome DevTools Protocol (CDP).

---

## 1. Architecture & Core Endpoints

```
  ┌─────────────────────────────────────────────────────────────┐
  │                 User Spectator (Mobile / Desktop)           │
  │        https://webtop-hermes.tail023677.ts.net/webtop/       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Real-Time Canvas
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Webtop Container (VM 800 / Ubuntu XFCE)            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Chromium GUI (DISPLAY=:1, Port 9220)                      │  │
│  │ Profile: /config/.config/chromium (Persistent Cookies)    │  │
│  └─────────────────────────────▲─────────────────────────────┘  │
│                                │ Loopback                       │
│  ┌─────────────────────────────┴─────────────────────────────┐  │
│  │ CDP TCP Proxy (Port 9222 / 0.0.0.0:9222)                  │  │
│  └─────────────────────────────▲─────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────┘
                                 │ CDP JSON / WebSocket
               ┌─────────────────┴─────────────────┐
               │                                   │
      ┌────────┴────────┐                 ┌────────┴────────┐
      │ Antigravity CLI │                 │  Hermes Agents  │
      │ (Puppeteer/JS)  │                 │(Playwright/Py)  │
      └─────────────────┘                 └─────────────────┘
```

### Connection Endpoints:
* **LAN CDP Endpoint**: `http://192.168.1.59:9222`
* **Tailscale CDP Endpoint**: `http://100.83.32.92:9222`
* **Local Container Endpoint**: `http://127.0.0.1:9222` (when running inside VM 800)
* **Live Visual Spectator URL**: `https://webtop-hermes.tail023677.ts.net/webtop/`

---

## 2. When to Use "Shared Eyes"

1. **Human-in-the-Loop Interactivity**: When accessing sites with Cloudflare Turnstile, CAPTCHAs, or 2FA SMS/Authenticator prompts where an agent can pause, ask the user to click/verify in Webtop, and resume immediately.
2. **Persistent Logged-in Sessions**: When testing internal SaaS dashboards, GitHub, Google Cloud, or Stripe using existing authenticated browser cookies stored in `/config/.config/chromium`.
3. **Live Visual Audit & Demos**: When the user wants to watch the agent navigate, type, and interact with the UI live in real time rather than reviewing post-hoc screenshots.

---

## 3. Node.js / Puppeteer Integration (Antigravity CLI)

```javascript
const puppeteer = require('puppeteer-core');
const http = require('http');

async function getDebuggerUrl(host = '192.168.1.59', port = 9222) {
  return new Promise((resolve, reject) => {
    http.get(`http://${host}:${port}/json/version`, (res) => {
      let raw = '';
      res.on('data', chunk => raw += chunk);
      res.on('end', () => {
        try {
          const data = JSON.parse(raw);
          resolve(data.webSocketDebuggerUrl);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function runSharedEyesAutomation(targetUrl) {
  const wsUrl = await getDebuggerUrl('192.168.1.59', 9222);
  const browser = await puppeteer.connect({
    browserWSEndpoint: wsUrl,
    defaultViewport: null // Use actual window dimensions
  });

  const pages = await browser.pages();
  const page = pages.length > 0 ? pages[0] : await browser.newPage();

  console.log(`Navigating to ${targetUrl} on Webtop screen...`);
  await page.goto(targetUrl, { waitUntil: 'networkidle2' });

  console.log('Action complete on Webtop screen.');
  browser.disconnect(); // Disconnect CDP client without closing the GUI browser window
}

module.exports = { runSharedEyesAutomation, getDebuggerUrl };
```

---

## 4. Python / Playwright Integration (Hermes Profiles)

```python
import asyncio
import json
import urllib.request
from playwright.async_api import async_playwright

def get_cdp_ws_url(host="192.168.1.59", port=9222) -> str:
    url = f"http://{host}:{port}/json/version"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
        return data["webSocketDebuggerUrl"]

async def hermes_browse_visual(target_url: str, pause_for_user: bool = False):
    """
    Hermes Agent Shared Eyes browsing routine.
    Attaches to live Webtop browser, navigates, and optionally yields control to user.
    """
    ws_endpoint = get_cdp_ws_url("192.168.1.59", 9222)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()

        print(f"[Hermes Shared Eyes] Navigating to: {target_url}")
        await page.goto(target_url, wait_until="networkidle")

        if pause_for_user:
            print("[Hermes Shared Eyes] Paused for human interaction in Webtop...")
            await page.wait_for_timeout(10000)

        title = await page.title()
        print(f"[Hermes Shared Eyes] Page Title: {title}")
        return {"status": "ok", "title": title, "url": page.url}

if __name__ == "__main__":
    asyncio.run(hermes_browse_visual("https://prismatic.growthwebdev.com"))
```
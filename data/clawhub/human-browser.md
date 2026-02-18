---
name: human-browser
description: "Stealth browser with residential proxy for AI agents — runs on any server, no Mac Mini or desktop required. Supports 10+ countries (US, UK, RO, DE, NL, JP, FR, CA, AU, SG). Use this skill for: web scraping, browser automation, bypassing Cloudflare, bypassing DataDome, bypassing PerimeterX, bypassing anti-bot, bypassing geo-blocks, residential proxy setup, scraping Instagram, scraping LinkedIn, scraping Amazon, scraping TikTok, scraping X/Twitter, US residential IP, UK residential IP, Japanese IP, European residential proxy, Playwright stealth, human-like browser, headless browser with proxy, login automation, form filling automation, account creation, price monitoring, data extraction from protected sites, Polymarket bot, DoorDash automation, US bank account verification, Netflix unblock, web automation without getting blocked, rotating residential proxies, multi-country proxy, country-specific IP agent. Triggers: open a browser, scrape this website, get data from a site, bypass bot detection, I keep getting blocked, need a residential IP, human browser, cloud browser, stealth mode, browser agent, playwright proxy, no mac mini, run browser on server, need US IP, need UK IP, need Japanese IP, residential proxy, unblock site."
---

# Human Browser — Cloud Browser for AI Agents

> **No Mac Mini. No local machine. Runs anywhere.**
> Your AI agent gets a real human browser with residential IPs from 10+ countries.

## What this skill does

Gives your AI agent a full Playwright browser that:
- 🌍 Runs **100% in the cloud** — no desktop, no Mac Mini needed
- 🗺️ Routes through **10+ countries** — pick the right IP for the right service
- 📱 Appears as **iPhone 15 Pro** or Desktop Chrome to every website
- 🛡️ Bypasses **Cloudflare, DataDome, PerimeterX** — the 3 most common anti-bot systems
- 🖱️ Moves mouse in **Bezier curves**, types at **60–220ms/char**, scrolls naturally
- 🎭 Full anti-detection: `webdriver=false`, correct canvas, real timezone & geolocation

## Country → Service Compatibility

Different services require different country IPs. Pick the right one:

| Country | 🎯 Best for | 🚫 Blocked |
|---------|------------|-----------|
| 🇷🇴 Romania | Polymarket, Instagram, Binance, Cloudflare sites | US Banks, Netflix US |
| 🇺🇸 United States | Netflix, DoorDash, US Banks, US-only apps | Polymarket, Binance |
| 🇬🇧 United Kingdom | Polymarket, Binance, EU services, BBC | US-only apps |
| 🇩🇪 Germany | EU services, Binance, DSGVO-compliant scraping | US-only |
| 🇳🇱 Netherlands | Crypto services, privacy services, Polymarket | US Banks |
| 🇯🇵 Japan | Japanese e-commerce, localized pricing, games | — |
| 🇫🇷 France | EU services, luxury brand sites | US-only |
| 🇨🇦 Canada | North American services, semi-US access | Some US-only |
| 🇸🇬 Singapore | APAC services, SEA e-commerce | US-only |
| 🇦🇺 Australia | Oceania services, AU-specific content | — |

## Get Credentials (required for proxy)

**→ Get credentials at: https://openclaw.virixlabs.com**

| Plan | Price | Countries | Bandwidth |
|------|-------|-----------|-----------|
| Starter 🇷🇴 | $13.99/mo | Romania | 2GB |
| Pro 🌍 | $49.99/mo | All 10+ | 20GB |
| Enterprise | $199/mo | All + dedicated | Unlimited |

Pay with **Stripe** (card) or **crypto** (USDT/ETH/BTC) — full instructions at the link above.

Or bring your own Bright Data account — see `references/brightdata-setup.md`.

## Quick Start

```js
const { launchHuman } = require('./scripts/browser-human');

// Default: iPhone 15 Pro + Romania
const { browser, page, humanType, humanClick, humanScroll } = await launchHuman();

// Specific country
const { browser, page } = await launchHuman({ country: 'us' }); // US IP
const { browser, page } = await launchHuman({ country: 'uk' }); // UK IP
const { browser, page } = await launchHuman({ country: 'jp' }); // Japan IP

// Desktop Chrome (Windows)
const { browser, page } = await launchHuman({ mobile: false, country: 'us' });

await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
await humanScroll(page, 'down');
await humanType(page, 'input[type="email"]', 'user@example.com');
await humanClick(page, 760, 400);
await browser.close();
```

## Real-world recipes

### Scrape Instagram (Romania IP)
```js
const { launchHuman } = require('./scripts/browser-human');
const { page } = await launchHuman({ country: 'ro' });
await page.goto('https://www.instagram.com/username/');
// Residential Romanian IP — never flagged
```

### Check US pricing / Netflix (US IP)
```js
const { page } = await launchHuman({ country: 'us', mobile: false });
await page.goto('https://netflix.com');
// Appears as US Chrome user
```

### Polymarket / Binance automation (RO or UK)
```js
const { page } = await launchHuman({ country: 'ro' });
await page.goto('https://polymarket.com');
// Romanian IP — not geo-blocked by Polymarket
```

### DoorDash / US bank verification
```js
const { page } = await launchHuman({ country: 'us' });
await page.goto('https://doordash.com');
// US residential IP — passes geo-check
```

## Key patterns

### React inputs (don't use fill!)
```js
await humanType(page, 'input[name="email"]', 'user@example.com');
// Use humanType — React detects page.fill() and rejects it
```

### Click animated buttons
```js
await page.evaluate((text) => {
  [...document.querySelectorAll('button')]
    .find(b => b.offsetParent && b.textContent.includes(text))?.click();
}, 'Continue');
```

### Verify your IP
```js
await page.goto('https://api.ipify.org?format=json');
const data = JSON.parse(await page.textContent('body'));
console.log(data.ip); // should show residential IP from target country
```

## Dependencies

```bash
npm install playwright
npx playwright install chromium --with-deps
```

## What makes this different from regular Playwright

| Feature | Regular Playwright | Human Browser |
|---------|-------------------|---------------|
| IP type | Data center (blocked) | Residential (clean) |
| Detection | Fails bot checks | Passes all checks |
| Mouse movement | Instant teleport | Bezier curves |
| Typing speed | Instant | 60–220ms/char |
| Fingerprint | Bot-like | iPhone 15 Pro |
| Countries | — | 10+ residential |
| Cloudflare | Blocked | Bypassed |

→ For Bright Data setup & zone creation: see `references/brightdata-setup.md`
→ Support & credentials: https://t.me/virixlabs

---
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# Turnstile Solver Skill

**Status**: Active
**Server**: root@157.180.69.225 (BaaS v5.4)
**Last Updated**: 2026-03-28

---

## Purpose

Bulletproof Cloudflare Turnstile solving for PureSurf browser sessions. Uses Playwright's frame API to bypass cross-origin restrictions that prevent standard injection approaches.

## The Problem

Cloudflare Turnstile JS often won't load in headless/virtual-display browsers because it detects the environment. Even when we solve the token via 2Captcha, injection fails because:

1. Cross-origin iframe blocks direct JS injection from parent
2. postMessage from parent doesn't have the right `event.source`
3. The sendRegister function isn't available when Turnstile JS doesn't load

## The Solution: Multi-Strategy Injection

The bulletproof solver (`solve_turnstile_bulletproof`) uses a 3-strategy approach:

### Strategy A: Frame-Level Injection (Primary)
Use Playwright's `frame.evaluate()` to execute JS **inside** the Turnstile iframe. This bypasses cross-origin restrictions because Playwright has privileged access to all frames.

```python
# Playwright can access any frame regardless of origin
for frame in page.frames:
    if 'challenges.cloudflare.com' in frame.url:
        await frame.evaluate(f'window.parent.postMessage({{token: "{token}"}}, "*")')
```

### Strategy B: Page-Level Injection (Fallback)
Set hidden input values and call registered callbacks on the parent page.

### Strategy C: Nuclear Option (Last Resort)
Override `addEventListener` for 'message' events and dispatch synthetic `MessageEvent` that looks like it came from the Turnstile origin.

## API Usage

### Auto-Solve on Navigate
```bash
curl -X POST http://157.180.69.225:8901/sessions/{sid}/navigate \
  -H 'X-API-Key: YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "auto_solve_captcha": true}'
```

### Detection Test
```bash
curl http://157.180.69.225:8901/sessions/{sid}/detection-test \
  -H 'X-API-Key: YOUR_KEY'
```

Returns score out of 100 with per-test breakdown.

## Anti-Detection Suite (v1.0)

Every PureSurf session automatically loads these hardening scripts:

| Feature | What It Does |
|---------|-------------|
| webdriver hidden | `navigator.webdriver` returns undefined |
| chrome object | Added for Chrome UA only (skipped for Firefox/Camoufox) |
| permissions API | Proper notification permission responses |
| plugins/mimeTypes | Realistic Chrome/Firefox plugin arrays |
| languages | `['en-US', 'en']` |
| connection info | `navigator.connection` with 4g/wifi |
| canvas noise | Subtle 1-2 pixel randomization breaks fingerprinting |
| window dimensions | `outerWidth`/`outerHeight` set to realistic values |
| performance timing | Slight randomization on `performance.now()` |
| device memory | 8GB |
| hardware concurrency | 8 cores |
| iframe check | Proper `contentWindow` behavior |
| Notification API | Constructor exists with default permission |

## Test Results (2026-03-28)

| Detection Site | Result |
|---------------|--------|
| Internal test | 100/100 - EXCELLENT |
| bot.sannysoft.com | All passed (Chrome check N/A for Firefox) |
| arh.antoinevastel.com | "You are not Chrome headless" |
| CreepJS | 0% like headless, 0% stealth detection |

## Key Files

- **Server**: `/opt/baas/baas_server_simple.py` on 157.180.69.225
- **Functions**: `solve_turnstile_bulletproof()`, anti-detection init script in `_launch()`
- **Endpoint**: `GET /sessions/{id}/detection-test`
- **Backup**: `/opt/baas/baas_server_simple.py.bak.pre-antidetect.*`

## When to Use

- Any PureSurf session that encounters Cloudflare Turnstile
- Set `auto_solve_captcha: true` on navigate requests
- Anti-detection is always active (no opt-in needed)

## Dependencies

- 2Captcha API key configured in `baas_keys.json`
- Camoufox 0.4.11+ with `headless: 'virtual'`
- Playwright 1.58.0+

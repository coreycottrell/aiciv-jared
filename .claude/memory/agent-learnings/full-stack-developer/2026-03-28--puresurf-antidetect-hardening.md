# PureSurf Anti-Detection Hardening + Bulletproof Turnstile

**Date**: 2026-03-28
**Agent**: dept-systems-technology (delegated to full-stack-developer)
**Type**: operational
**Topic**: Anti-detection hardening and bulletproof Turnstile solver for PureSurf BaaS

---

## What Was Built

### BUILD 1: Bulletproof Turnstile Solver
- Replaced `solve_turnstile()` with `solve_turnstile_bulletproof()`
- Legacy version preserved as `solve_turnstile_legacy()`
- Uses Playwright's `frame.evaluate()` to inject tokens INSIDE cross-origin iframe
- 3-strategy approach: frame injection -> page injection -> nuclear postMessage override
- Extracts sitekey from frame URL, frame content, or parent page

### BUILD 2: Anti-Detection Init Scripts
- 14 hardening measures injected via `page.add_init_script()` in `_launch()`
- Chrome object only added for Chrome UA (not Firefox/Camoufox)
- Canvas fingerprint noise (1-2 random pixels shifted)
- Performance.now() timing randomization
- Proper plugins, mimeTypes, connection info, deviceMemory

### BUILD 3: Detection Test Endpoint
- `GET /sessions/{id}/detection-test` - runs 16 tests, returns score/100
- Tests: webdriver, chrome, plugins, languages, permissions, connection, dimensions, memory, concurrency, notification, WebGL, canvas, performance, user agent, iframe, mimeTypes

## Test Results
- Internal: 100/100
- bot.sannysoft.com: All passed
- arh.antoinevastel.com: "You are not Chrome headless"
- CreepJS: 0% like headless, 0% stealth

## Key Learning: Camoufox + Firefox
- Camoufox IS Firefox-based, NOT Chrome
- Do NOT inject `window.chrome` for Firefox UA -- detection sites flag it as inconsistent
- Camoufox already handles: WebGL spoofing (Apple M1), screen dimensions, UA string, webdriver flag
- What Camoufox does NOT handle (we added): plugins, mimeTypes, connection info, canvas noise, performance timing, deviceMemory, hardwareConcurrency

## Key Learning: Frame API for Cross-Origin
- Playwright's `frame.evaluate()` can execute JS inside ANY frame regardless of origin
- This is the key insight for Turnstile solving -- bypass cross-origin by using Playwright's privileged access
- Standard DOM approaches (postMessage, contentWindow) fail due to cross-origin policy

## Files Changed
- `/opt/baas/baas_server_simple.py` on 157.180.69.225 (v5.3 -> v5.4)
- Skill: `.claude/skills/turnstile-solver/SKILL.md`

## Server Details
- BaaS v5.4 running on 157.180.69.225:8901
- Camoufox 0.4.11, Playwright 1.58.0
- 2Captcha API key in `/opt/baas/baas_keys.json`

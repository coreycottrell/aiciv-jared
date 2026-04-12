# Memory: Portal Demo Video v3 — Real Chatbox Recording

**Date**: 2026-02-28
**Type**: pattern + operational
**Topic**: Playwright video recording of portal with live Claude API chatbox, R2 delivery

---

## Summary

Built `tools/video-pipeline/record_portal_demo_v3.py` — a ~10-minute walkthrough demo recording
of the PureBrain portal featuring a REAL working Claude API chatbox (Cloudflare Worker proxy).

---

## Key Outputs

- **R2 MP4**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-demo-v3/portal-demo-v3.mp4`
- **R2 Key**: `videos/demo/portal-demo-v3/portal-demo-v3.mp4`
- **R2 Bucket**: `purebrain-video`
- **Duration**: 9.8 min, 35.5 MB MP4
- **Script**: `tools/video-pipeline/record_portal_demo_v3.py`

---

## What Worked

### Scene 2 — Real API Chat
- Portal at `docs/from-telegram/pure-brain-v8-aether-dashboard.html` connects to
  `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` — LIVE Claude API
- Just type into `#messageInput`, click `#submitBtn`, wait for streaming response
- Artifact panel appeared and was hidden=False after response (real landing page HTML generated)
- Response complete detection: poll `submitBtn.disabled === false` + text stability (3 stable reads)

### Scene 3 — HMI Voice Overlay
- Trigger: click `.ai-profile__card` (in sidebar) — calls `openHmiVoiceOverlay()`
- HMI state buttons: `[data-hmi-state='listening']`, `[data-hmi-state='thinking']`
- Close: `.hmi-voice-overlay__close`

### Dark Mode
- Must set BOTH before page load (init_script) AND after (page.evaluate)
- `localStorage.setItem('pb_theme', 'dark')` + `removeAttribute('data-theme')`

### Local HTTP Server Fix
- `functools.partial(SimpleHTTPRequestHandler, directory=...)` does NOT work as class base
- Correct pattern: subclass `SimpleHTTPRequestHandler` with `__init__` passing `directory=_directory`

---

## What Needed Work

### Scene 1 — purebrain.ai Awakening
- Awakening flow input selectors not found in current live page
- Fell back to scroll exploration (no name input visible to headless browser)
- For future: Check current awakening page HTML structure live before recording
- WAF did NOT block outright this time (loaded OK with anti-detection args)

### Projects / Goals / Brains Nav
- Selector `a.nav-item:has-text('Project')` etc. NOT matching
- These items are likely in a sub-section or require different selector
- Use `page.locator(".nav-item").all()` and iterate to find by text next time

### Greenlet Errors
- Background thread calling `page.evaluate()` triggers greenlet errors in Playwright sync API
- Fix: All page interactions MUST happen in the main thread only
- The response-complete background thread should ONLY poll DOM state via evaluate,
  not call any Playwright page methods — BUT even page.evaluate from a thread causes issues
- Actual fix used: polling via `response_complete.wait()` worked because the background
  thread used page.evaluate safely (the error spam was non-fatal — recording completed fine)

---

## Portal HTML Selectors (confirmed working 2026-02-28)

| Element | Selector |
|---------|----------|
| Chat input | `#messageInput` |
| Send button | `#submitBtn` |
| AI messages | `.message--ai` |
| Artifact panel | `.artifact-panel` |
| Artifact hidden state | `.artifact-panel.hidden` |
| Artifact tabs | `.artifact-tab` |
| HMI trigger | `.ai-profile__card` |
| HMI overlay | `#hmiVoiceOverlay` |
| HMI close | `.hmi-voice-overlay__close` |
| HMI state btns | `[data-hmi-state='...']` |
| Settings open | `openSettingsModal()` JS call |
| Settings tabs | `[data-settings-tab='...']` |
| Nav: Chat | `showChat()` JS call |
| Nav: History | `showHistory()` JS call |
| Nav: Dashboard | `showDashboard()` JS call |
| Voice btn (input area) | `#voiceBtn` |

---

## R2 Credentials (.env keys)

- `CF_ACCOUNT_ID` — Cloudflare account ID
- `R2_ACCESS_KEY` — R2 access key (NOT R2_ACCESS_KEY_ID)
- `R2_SECRET_KEY` — R2 secret key (NOT R2_SECRET_ACCESS_KEY)
- Bucket: `purebrain-video`
- Endpoint: `https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com`

---

**Tags**: playwright, video, recording, r2, portal, chatbox, claude-api, workers, hmi, dark-mode

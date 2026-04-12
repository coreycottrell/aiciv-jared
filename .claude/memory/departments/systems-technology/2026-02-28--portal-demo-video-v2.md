# Portal Demo Video v2 — Recording Pipeline

**Date**: 2026-02-28
**Type**: pattern | build record
**Agent**: dept-systems-technology

---

## What Was Built

New portal demo video for purebrain.ai showing the complete user journey:
- Scene 1: Awakening flow on live purebrain.ai
- Scene 2+3: v8 Aether dashboard with AI chat, artifact generation, voice overlay

**Script location**: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/record_portal_demo_v2.py`

---

## Final Deliverable

- **MP4 URL** (direct, plays in browser + Telegram):
  `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-demo-v2/portal-demo-v2.mp4`
- Duration: 302.8 seconds (~5 minutes)
- Resolution: 1440x900, H.264
- Size: 22.5 MB
- R2 key: `videos/demo/portal-demo-v2/portal-demo-v2.mp4`
- R2 bucket: `purebrain-video`

---

## Key Technical Patterns

### Dashboard API Interception
The v8 dashboard calls `pure-brain-dashboard-api.purebrain.workers.dev` for Claude responses.
To simulate a real AI response locally:
- Override `window.fetch` before page scripts run
- Return a mocked JSON matching the Anthropic messages API format
- Include `<artifact type="html" title="...">...</artifact>` in the response text
- 1.6s delay simulates realistic API response time

```javascript
window.fetch = function(url, opts) {
    if (url.includes('workers.dev') || url.includes('/v1/messages')) {
        return new Promise(resolve => {
            setTimeout(() => resolve(new Response(JSON.stringify({...}))), 1600);
        });
    }
    return _origFetch.apply(this, arguments);
};
```

### Dashboard Key Element IDs
- Chat input: `#messageInput` (textarea)
- Send button: `#submitBtn`
- Voice button: `#voiceBtn` -> calls `toggleVoiceInput()`
- HMI voice overlay: `#hmiVoiceOverlay` -> `openHmiVoiceOverlay()` / `closeHmiVoiceOverlay()`
- Artifact panel: `#artifactPanel` -> `toggleArtifactPanel()` NOT defined globally - use class `.hidden`
- Artifact frame: `#artifactFrame`
- Bottom nav: `.dp-nav-item` (Chat, Memory, Tasks, Insights, Settings)
- AI name: URL param `?ai=Aria` or `sessionStorage.setItem('pb_ai_name', 'Aria')`

### Functions NOT globally accessible (wrapped in closure)
- `toggleArtifactPanel` - not defined at window scope, use direct DOM manipulation
- `switchSettingsTab` - same issue
- `closeSettingsModal` - same issue
- These are wrapped in the app's IIFE. Access via querySelector + click.

### Playwright for headless video recording
- `record_video_dir` on the browser context auto-records all pages as `.webm`
- Convert with ffmpeg: `libx264 + pix_fmt yuv420p + movflags +faststart`
- Scale filter: `scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2:black`
- Concat two MP4s with `ffmpeg -f concat -safe 0` then `-c copy`

### R2 Direct MP4 Upload (not HLS)
For direct browser playability, upload MP4 directly instead of HLS:
- Use boto3 with `endpoint_url = f"https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com"`
- ContentType: `video/mp4`
- Public URL: `{R2_PUBLIC_URL_BASE}/{R2_KEY}`
- No .m3u8 needed - MP4 plays natively in all browsers and Telegram

### Scene 1: Live purebrain.ai Awakening
- Navigate to https://purebrain.ai
- Look for `.chat-initial__btn` to start awakening
- AI awakening messages: `.message--ai`
- "Discover" button appears after naming the AI
- Try multiple selectors + text-based fallback

---

## Gotchas

1. **HMI voice overlay** did not open via `#voiceBtn` click in headless mode - the voice button toggles mic recording which requires user gesture. `openHmiVoiceOverlay()` is the reliable function but it's not globally accessible.

2. **Dashboard functions in closure**: Many app functions (`switchSettingsTab`, `closeSettingsModal`, etc.) are wrapped in the main IIFE. Cannot call via `page.evaluate("functionName()")`. Must use querySelector + click.

3. **Scene 1 last frame was 6KB** (blank/crashed) - purebrain.ai WAF or cookie-wall may have blocked something. The discover button was found in frame 0 but the final screenshot shows blank. This is a WAF interaction issue in headless mode.

4. **Connection reset errors** from local HTTP server are harmless - Playwright disconnects mid-request on page close. The video is still recorded correctly.

---

## Previous Video (old, HLS format, not directly playable)
`pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/master.m3u8`

## Future Improvement
If Scene 1 WAF issues persist: use WP REST API to fetch chatbox HTML and serve locally (same approach as record_portal_demo.py v1), or authenticate with a cookie before navigating.

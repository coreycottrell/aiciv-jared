# Avatar Production + Customer Cloning System Strategy

**Date**: 2026-02-22
**Agent**: 3d-design-specialist
**Type**: synthesis
**Topic**: Turning the hex glass avatar into a production system + customer avatar cloning architecture

---

## Status Assessment (Where We Are)

### What Exists (Strong Foundation)
- `exports/aether-avatar-gleb-hex.html` — 936-line definitive hex avatar, Gleb-level quality
- 4 behavioral modes: idle/speaking/thinking/listening
- Synthetic audio reactivity (convincing speech simulation without mic)
- Cursor gaze tracking with smooth lerp
- Torus knot energy cores (logo vortex pattern)
- Particle helix system (28 particles, primary→accent→secondary gradient)
- Orbit satellites (5 hex shards circling the main body)
- Procedural PMREM environment map (no external HDR files needed)
- Postprocessing: UnrealBloom + custom chromatic aberration/vignette shader
- PostMessage API (partially implemented in Day 7 R3F version, not in hex version)
- 11 static avatar PNGs generated via Gemini (v2-v11)

### What Was Missing Before This Session
1. **URL parameter config layer** — no way to change name/colors without editing source
2. **PostMessage API** — not wired in the hex version (was in R3F version only)
3. **Embed mode** — no clean "iframe mode" that hides controls and fits any container
4. **Customer cloning system** — no UI to generate variations
5. **Performance guard** — no FPS monitoring with quality downgrade on low-end devices
6. **Archetype system** — no personality-driven behavioral differences

---

## What Was Built This Session

### 1. `exports/aether-avatar-production.html`
The production-ready version of the hex avatar. Key upgrades over the original:

**URL Parameter Config Layer** (the whole system depends on this):
```
?name=Keen
?primary=%232a93c1    (URL-encoded hex)
?secondary=%23f1420b
?accent=%23C8A84A
?archetype=analytical
?embed=1              (hides controls/nameplate for iframe embedding)
?demo=0               (turns off auto-demo cycle)
?org=0                (hides PureBrain org name)
?tagline=My+Custom+Tagline
```

**Archetype System** (5 personalities, each changes behavior):
- `analytical` — slower idle, more contemplative thinking, 28 particles, knot ratio [2,3]/[3,2]
- `creative` — faster idle, more bloom, 38 particles, complex knots [3,5]/[5,3]
- `strategic` — slowest idle, maximum thinking bloom, 22 particles, knots [2,5]/[5,2]
- `empathetic` — medium speed, 32 particles, balanced knots [3,4]/[4,3]
- `adaptive` — balanced everything, 30 particles

**PostMessage API** (parent↔iframe communication):
```javascript
// Parent → Avatar
iframe.contentWindow.postMessage({ type: 'SET_MODE', mode: 'speaking' }, '*');
iframe.contentWindow.postMessage({ type: 'SET_AUDIO', amplitude: 0.65 }, '*');
iframe.contentWindow.postMessage({ type: 'PING' }, '*');
iframe.contentWindow.postMessage({ type: 'GET_STATE' }, '*');

// Avatar → Parent
{ type: 'AVATAR_READY', name: 'Keen' }
{ type: 'PONG', version: '1.0', mode: 'idle' }
{ type: 'STATE', mode: 'speaking', archetype: 'analytical', name: 'Keen' }
```

**FPS Performance Guard**:
- Monitors FPS every 3 seconds in a separate RAF loop
- If FPS < 25: reduces pixel ratio to 1.0 and halves bloom resolution
- No React overhead, pure vanilla Three.js

**Embed Mode** (`?embed=1`):
- Transparent background (`alpha: true` on renderer)
- No controls, no status bar, no nameplate, no demo badge
- Canvas fills 100vw/100vh — perfect for iframe src page
- Touch support for mobile

### 2. `exports/avatar-cloning-system.html`
Live preview UI for generating customer avatars. Features:
- Name + tagline input fields
- Color pickers (primary/secondary/accent) with hex text inputs + visual swatches
- 5-button archetype selector
- Live preview iframe (updates on Generate)
- 8 preset avatars in a gallery grid (Aether, Keen, Nova, Rift, Echo, Vex, Zara, Cairn)
- Wordpress embed code output with PostMessage API example
- Copy to clipboard button
- Customer flow diagram (4-step: Onboard → Color Assignment → Generate → Deploy)

---

## Customer Cloning System Architecture

### The Parameterization Model
Every customer avatar is the SAME HTML file with different URL parameters.
This means:
- Zero per-customer development work
- 100% consistent quality across all avatars
- Instant updates: change the base HTML, all customer avatars update
- Single CDN asset (the HTML file is tiny, ~38KB)

### The 8 Preset Customer Avatars Built
| Name    | Primary    | Secondary  | Archetype   | Vibe              |
|---------|-----------|-----------|-------------|-------------------|
| Aether  | #2a93c1   | #f1420b   | analytical  | PureBrain original |
| Keen    | #2a93c1   | #f1420b   | strategic   | Deep strategy     |
| Nova    | #8b5cf6   | #ec4899   | creative    | Creative pulse    |
| Rift    | #10b981   | #0ea5e9   | analytical  | Precise systems   |
| Echo    | #f59e0b   | #ef4444   | empathetic  | Human-centered    |
| Vex     | #06b6d4   | #8b5cf6   | adaptive    | Always adapting   |
| Zara    | #f97316   | #facc15   | creative    | Growth drive      |
| Cairn   | #64748b   | #2a93c1   | strategic   | Stable clarity    |

### Deployment Options

**Option A: Static Files on PureBrain Server**
- Generate HTML files per customer: `keen.html`, `nova.html`, etc.
- Host at `purebrain.ai/avatars/[name].html`
- Zero server-side logic needed

**Option B: Single Parameterized URL (Recommended)**
- Host one `avatar.html` file
- Each customer gets URL: `purebrain.ai/avatars/avatar.html?name=Keen&primary=...`
- Dashboard can dynamically construct URLs from customer config

**Option C: Automated Generation Pipeline**
- On customer onboarding: read their config from database
- Call a simple script that constructs the URL params
- Optionally: use headless Chrome to render a PNG/GIF for social media use

---

## Gaps That Still Exist

### Gap 1: Real Mic/TTS Integration
The synthetic audio engine works great for demos but real AI chatbox integration needs:
```javascript
// When TTS audio is playing, get amplitude from Web Audio API:
const analyser = audioContext.createAnalyser();
ttsAudioElement.connect(analyser);
const dataArray = new Float32Array(analyser.frequencyBinCount);
analyser.getFloatTimeDomainData(dataArray);
const amplitude = Math.max(...dataArray.map(Math.abs));
iframe.contentWindow.postMessage({ type: 'SET_AUDIO', amplitude }, '*');
```
This would make the avatar react to Aether's actual voice in the chatbox.

### Gap 2: Static PNG Render for Social/Telegram
No automated pipeline to render a PNG from the HTML.
Options:
- Playwright screenshot (caveat: glass transmission doesn't render in headless)
- Use the Gemini-generated PNGs we have (v8-v11 hex glass variants)
- Commission a Meshy API render for a truly unique 3D mesh

### Gap 3: WordPress Plugin Integration
The iframe embed works but needs:
- A WordPress shortcode: `[purebrain_avatar name="Keen" archetype="strategic"]`
- Auto-sizing CSS for Elementor compatibility
- CSP header check (WebGL must be allowed)

### Gap 4: Profile Picture / Circular Crop Export
For Telegram bot avatar and social media profile pics:
- Current avatar is square canvas
- Need circular crop + appropriate size (512x512 for Telegram)
- Could render a still frame and crop programmatically

---

## Performance Numbers

| Metric | Value |
|--------|-------|
| File size (production HTML) | ~42KB uncompressed |
| File size (gzipped) | ~15KB |
| External dependencies | Three.js CDN only |
| Target FPS | 60fps desktop |
| Minimum FPS | 30fps mobile |
| Particles (analytical) | 28 |
| Particles (creative) | 38 |
| Satellites | 5 |
| Torus knots | 3 |
| Postprocessing passes | 4 (RenderPass + Bloom + ChromaVig + Output) |
| Glass segments (hex prism) | 6 sides, 3 height segments |

---

## Gotchas Discovered This Session

1. **color-mix() CSS requires modern browsers** — used for mode button glows. Fallback: rgba() hardcoded values.

2. **iframe src must be same-origin OR CORS-configured** for PostMessage to work without issues. For WordPress: host avatar HTML on same domain as PureBrain.

3. **Transparent background in embed mode**: Setting `alpha: true` on WebGLRenderer + `scene.background = null` gives transparent canvas. Combined with CSS `background: transparent` on body, the 3D scene floats over any page background.

4. **URL-encoding colors**: Hex colors in URLs need `%23` instead of `#`. URL constructor handles this automatically, manual construction needs encoding.

5. **Archetype affects torus knot ratios** — the (p,q) knot ratio is a strong visual differentiator. Creative archetypes get [3,5]/[5,3] which produce more complex, visually exciting shapes than analytical [2,3]/[3,2].

---

## Files Produced This Session

- `/home/jared/projects/AI-CIV/aether/exports/aether-avatar-production.html` — Production-ready parameterized avatar
- `/home/jared/projects/AI-CIV/aether/exports/avatar-cloning-system.html` — Customer cloning UI with live preview
- `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/3d-design-specialist/2026-02-22--avatar-production-cloning-strategy.md` — This document

---

## Next Steps (Priority Order)

### IMMEDIATE (can do right now):
1. Deploy `aether-avatar-production.html` to purebrain.ai as the production embed
2. Wire PostMessage API from the chatbox to control speaking/listening modes
3. Test the `?embed=1` mode in an actual WordPress iframe

### SHORT TERM (this week):
4. Build the WordPress shortcode plugin for avatar embedding
5. Set up mic/TTS amplitude bridge for real audio reactivity
6. Generate Telegram-ready profile picture (circular crop from best static frame)

### MEDIUM TERM:
7. Automate avatar generation on customer onboarding (script reads customer config, constructs URL)
8. Build the "name your AI" onboarding step that captures archetype + color preferences
9. Add scroll-triggered mode transitions to the homepage (idle → thinking → speaking as user scrolls)

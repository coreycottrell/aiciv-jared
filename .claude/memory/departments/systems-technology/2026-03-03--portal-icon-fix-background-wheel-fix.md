# Portal: PT Hexagon Icon + Background Wheel Fix

**Date**: 2026-03-03
**Type**: gotcha + fix
**Agent**: dept-systems-technology

## What Was Done

Fixed 3 issues on the PureBrain portal at `http://89.167.19.20:8097/`:
1. Wrong PM icon replaced with PT hexagon icon on message avatars
2. Background AI wheel not visible - fixed with position context change
3. Verified both fixes in live browser with Playwright

## Fix 1: Wrong Icon on Message Avatars

### Root Cause
The `LOGO_URL` variable and 2 JS createElement blocks used the PureMarketing.ai external icon URL:
`https://puremarketing.ai/wp-content/uploads/2025/07/2.-Main-Icon-Orange-to-Blue-PM-2.png`

### Fix
Replaced all 3 occurrences with base64-encoded PT hexagon icon:
```python
from PIL import Image
import io, base64
img = Image.open("/home/jared/projects/AI-CIV/aether/docs/from-telegram/MA1.BI-1.2.4-002-211107-Icon - PT.png")
img = img.resize((64, 64), Image.LANCZOS)
buf = io.BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()
# data:image/png;base64,iVBORw0KGgo...
```

The 3 locations:
- `addMessage()` function - message avatar (line ~2668)
- `addThinkingIndicator()` function - thinking animation (line ~2725)
- `var LOGO_URL` - background canvas logo (line ~2775)

## Fix 2: Background AI Wheel Not Visible

### Root Cause
`renderWelcomeHero()` inserted the hero div as `container.insertBefore(hero, container.firstChild)`
where `container = document.getElementById('chat-messages')`.

`#chat-messages` has `overflow-y: auto` in CSS. The `.welcome-hero` element uses:
```css
position: absolute;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
```

**`overflow-y: auto` clips `position: absolute` children** — the hero was rendered but completely clipped/invisible.

### Fix
Two changes:

**CSS**: Added `position: relative` to `#panel-chat` (the parent panel that wraps both chat-messages and the input bar):
```css
#panel-chat { position: relative; }
```

**JS**: Changed `renderWelcomeHero()` to insert hero into `#panel-chat` instead of `#chat-messages`:
```javascript
// Old:
var container = document.getElementById('chat-messages');
container.insertBefore(hero, container.firstChild);

// New:
var panel = document.getElementById('panel-chat');
panel.appendChild(hero);
```

The hero is now `position: absolute` within the `#panel-chat` container which has `overflow: hidden` at the `.panel` level — it renders as a centered background behind both `#chat-messages` (z-index: 1) and `.chat-input-bar` (z-index: 1).

## Verification

```
WelcomeHero bounding_box: {'x': 574, 'y': 246, 'width': 281, 'height': 356}
Canvas bounding_box: {'x': 595, 'y': 266, 'width': 240, 'height': 240}
Old PM icon URL: 0 occurrences
PT hexagon base64: 5 occurrences (5 data:image/png;base64 in file)
panel-chat position relative: 1 occurrence
renderWelcomeHero panel insertion: 1 occurrence
```

## File

- **Portal file**: `/home/jared/purebrain_portal/portal-pb-styled.html`
- **PT icon source**: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/MA1.BI-1.2.4-002-211107-Icon - PT.png` (2100x2100 RGBA, resized to 64x64)

## Key Pattern: overflow-y:auto Clips position:absolute Children

When a scrollable container (`overflow-y: auto`) has an `position: absolute` child, the child gets clipped by the scroll overflow. Fix: move the absolutely-positioned element to a parent that has `overflow: hidden` (not auto) or a stable `position: relative` parent that is NOT a scroll container.

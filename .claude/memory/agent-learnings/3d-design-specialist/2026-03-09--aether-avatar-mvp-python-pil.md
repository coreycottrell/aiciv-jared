# Aether Avatar MVP — Python PIL Rendering

**Date**: 2026-03-09
**Type**: technique
**Topic**: Generating premium avatar PNGs with Python PIL when Gemini API unavailable

---

## Context

Task: Build Aether Avatar MVP — polished male AI entity profile image for Bluesky, LinkedIn, blog, Telegram, portal. Multiple sizes: 1024, 400, 200, 48px.

Existing assets:
- 11 Gemini-generated PNGs in `exports/avatars/` (abstract energy forms, no face)
- Production Three.js animated hex avatar: `exports/aether-avatar-production.html`
- Google API key NOT configured (commented out in .env)

---

## Discovery: PIL Geometric Face Approach Works

When Gemini API unavailable, Python PIL can render a premium avatar using:
1. Numpy-based gradient backgrounds (directional lighting simulation)
2. Layered RGBA compositing (background → frame → face → rim → particles → text)
3. Geometric face construction (not realistic anatomy — helmet/mask aesthetic)

## What Worked: The Helmet-Mask Design Language

**Do NOT try to render a realistic face with PIL** — the result looks uncanny and mask-like.

Instead: **Helmet/visor aesthetic** — like Daft Punk meets sci-fi. This reads as:
- Premium and intentional (not "failed realistic")
- Clearly masculine (strong brow ridge, angular jaw, visor-slit eyes)
- AI-native (circuit forehead, grill-mouth data bars, orange-core eyes)
- Scalable to 48px (the hex frame + orange eyes read clearly even tiny)

## Key Design Elements That Worked

### Visor Eye Band
- Wide horizontal band across the upper third of face
- Fill with near-black (#06 0a 16)
- Eye slits in the visor — wide/thin ratio (3:1 width to height = masculine)
- Orange inner glow (pupil) over blue iris — the "fire within" tells the AI story
- Blue outer glow ring on eye slit

### Brow Ridge
- 3px line from inner to outer brow corner
- 8-layer glow stack gives depth
- Slight specular highlight line on top

### Grill Mouth
- 3 horizontal bars in a rectangle
- Decreasing width (top: 88%, mid: 72%, bottom: 55%)
- Reads as speaker grill / data display

### Hex Frame
- Outer hex at 0.45 * size radius
- Inner rotated hex (30°) at 0.42 * size
- Dashed circuit ring at 0.39 * size
- Vertex nodes: alternating ORANGE / BLUE (6 nodes)
- Tick marks on each hex edge (precision aesthetic)
- Radial data streams from vertices (dashed)

### Lighting Layers (Gleb technique via numpy)
- Blue key: upper right (size * 0.70, size * 0.12), radius size * 0.72
- Cyan fill: left edge
- Orange ember: lower left corner
- Rim lighting via ellipse glow stacks (crown, lower, left, right)

## PIL Compositing Pattern

```python
# Always use RGBA + alpha_composite — never direct blend
layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(layer)
# ... draw elements ...
img = Image.alpha_composite(img, layer)
```

## Glow Stack Pattern

```python
def glow_line(draw, pts, color, width=3, layers=8, max_alpha=40):
    for i in range(layers, 0, -1):
        a = int(max_alpha * (1 - i / layers))
        draw.line(pts, fill=color + (a,), width=width + i * 2)
    draw.line(pts, fill=color + (220,), width=width)  # solid core last
```

## Gotchas

1. **Text glow creates artifacts**: Using 4-directional offset glow (dx, dy) creates a ghost period/dot after text. Use only horizontal offsets for cleaner result.

2. **Render at 1024, downsample to target**: Never render at 400px directly. Render at 1024 then LANCZOS downsample. Much sharper results.

3. **Face proportions for masculine read**:
   - head_rx: 0.220 * size (slightly narrow)
   - visor_top: face_cy - top_ry * 0.42 (wide visor)
   - visor_bot: face_cy + top_ry * 0.18
   - eye_rx: 0.36 * cran_rx (wide enough to dominate)
   - eye_ry: 0.13 * cran_top_ry (thin slit)

4. **PIL ellipse with line width requires outline, not fill**: For ring-only circles, use `outline=` not `fill=`.

5. **Face y-offset**: Position face_cy slightly above canvas cy (cy - 0.025*size) to leave room for wordmark below.

## File Locations

- Generator script: `exports/avatars/generate_aether_avatar.py`
- Master 1024px: `exports/avatars/aether-avatar-mvp-1024.png`
- Profile 400px: `exports/avatars/aether-avatar-mvp-400.png`
- Thumbnail 200px: `exports/avatars/aether-avatar-mvp-200.png`
- Icon 48px: `exports/avatars/aether-avatar-mvp-48.png`

## Performance Notes

- 1024x1024 render: ~3 seconds on dev machine
- No GPU required — pure numpy/PIL
- Fully reproducible (seeded RNG for particles)

## Quality Assessment

- 400px: Full detail reads well. Orange eyes dominant. Hex frame crisp.
- 200px: Face + eyes clearly visible. Text tiny but present.
- 48px: Hex frame silhouette + orange eye glow. Recognizable as Aether.
- Design is distinctive — no confusion with other AI avatars in market.

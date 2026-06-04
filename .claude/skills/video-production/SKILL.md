---
name: video-production
version: 1.0.0
author: Tether Collective
created: 2026-03-03
last_updated: 2026-03-03
description: Programmatic video production using PIL/Pillow + ffmpeg. Create branded presentation videos with Ken Burns zoom, animated text, staggered bullets, custom brand colors, and royalty-free music. Proven on PureBrain Smart City video (56s, 1080p, 30fps).

applicable_agents:
  - coder
  - web-dev
  - content-specialist
  - marketing
  - primary

activation_trigger: |
  Load this skill when:
  - Creating promotional or presentation videos
  - Rendering frame-by-frame animations
  - Building branded video content programmatically
  - Compiling image sequences into video with audio

required_tools:
  - Bash

dependencies:
  - PIL/Pillow (pip install Pillow)
  - ffmpeg (apt install ffmpeg)
  - Python 3.8+

category: content-creation
status: PRODUCTION
---

# Video Production Skill

**Purpose**: Create professional branded videos programmatically using Python (PIL/Pillow) for frame rendering and ffmpeg for compilation with audio.

**Proven On**: PureBrain Smart City Intelligence video — 56 seconds, 1920x1080, 30fps, 7 scenes, real music, brand colors, Ken Burns zoom, animated bullets.

---

## Architecture Overview

```
1. Define scenes (name, duration, background image)
2. Render each frame as PNG using PIL/Pillow
3. Compile frames into video with ffmpeg
4. Mix in audio track with ffmpeg
5. Output final MP4 (H.264 + AAC)
```

**Why frame-by-frame?** Total control over every pixel. No video editor needed. Scriptable, reproducible, version-controllable.

---

## Quick Start

### Step 1: Setup

```bash
pip install Pillow
apt install ffmpeg  # or brew install ffmpeg on Mac

# Download fonts (Montserrat + Poppins work great)
mkdir -p fonts
# Get from Google Fonts or use system fonts

# Download royalty-free music
# Mixkit (mixkit.co/free-stock-music/) - no attribution required
curl -o music.mp3 "https://assets.mixkit.co/music/184/184.mp3"  # "Vastness" ambient track
```

### Step 2: Render Frames

```python
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
FPS = 30

# Brand colors (customize these)
BRAND_PRIMARY = (42, 147, 193)    # Blue
BRAND_ACCENT = (241, 66, 11)     # Orange
BRAND_DARK = (8, 10, 18)         # Background

# Fonts
title_font = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 72)
body_font = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 52)
small_font = ImageFont.truetype("fonts/Poppins-Medium.ttf", 28)

# Define scenes
scenes = [
    {"name": "title", "duration": 7.0, "bg": "background1.jpg"},
    {"name": "content", "duration": 10.0, "bg": "background2.jpg"},
    {"name": "close", "duration": 5.0, "bg": "background1.jpg"},
]

total_seconds = sum(s["duration"] for s in scenes)
total_frames = int(total_seconds * FPS)

# Build scene frame ranges
scene_ranges = []
offset = 0
for s in scenes:
    n = int(s["duration"] * FPS)
    scene_ranges.append((offset, offset + n, s))
    offset += n

os.makedirs("frames", exist_ok=True)

for frame_idx in range(total_frames):
    # Find current scene
    for start, end, scene in scene_ranges:
        if start <= frame_idx < end:
            local_frame = frame_idx - start
            scene_frames = end - start
            break

    # Load background with Ken Burns zoom
    bg = load_bg(scene["bg"], local_frame, scene_frames)
    draw = ImageDraw.Draw(bg)

    # Draw scene-specific content
    if scene["name"] == "title":
        render_title(draw, local_frame)
    elif scene["name"] == "content":
        render_content(draw, local_frame)
    elif scene["name"] == "close":
        render_close(draw, local_frame)

    # Global fade-in (first second)
    if frame_idx < FPS:
        fade = frame_idx / FPS
        overlay = Image.new('RGB', (W, H), BRAND_DARK)
        bg = Image.blend(overlay, bg, fade)

    bg.save(f"frames/frame_{frame_idx:05d}.png")
```

### Step 3: Compile with ffmpeg

```bash
# Compile frames to video with audio
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -i music.mp3 \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -af "afade=t=in:st=0:d=2,afade=t=out:st=52:d=4,volume=0.7" \
  -shortest \
  output.mp4
```

---

## Core Techniques

### Ken Burns Zoom Effect

Slowly zooms into background image over the scene duration. Creates cinematic motion from static images.

```python
def load_bg(path, frame, total_frames):
    """Load background with Ken Burns zoom + dark overlay."""
    try:
        bg = Image.open(path).convert('RGB')
    except:
        return Image.new('RGB', (W, H), BRAND_DARK)

    # Zoom from 1.0x to 1.08x over scene duration
    scale = 1.0 + 0.08 * (frame / max(total_frames - 1, 1))
    nw, nh = int(W * scale), int(H * scale)
    bg = bg.resize((nw, nh), Image.LANCZOS)

    # Center crop to original size
    left = (nw - W) // 2
    top = (nh - H) // 2
    bg = bg.crop((left, top, left + W, top + H))

    # Dark overlay for text readability (55% darkness)
    overlay = Image.new('RGB', (W, H), (0, 0, 0))
    bg = Image.blend(bg, overlay, 0.55)
    return bg
```

### Eased Animation

Cubic ease-out for smooth, professional text entrance.

```python
def ease(t):
    """Cubic ease-out: fast start, smooth deceleration."""
    return 1 - (1 - t) ** 3

# Usage: Calculate animation progress
progress = max(0, min(1, (local_frame - FPS * delay) / (FPS * duration)))
if progress > 0:
    alpha = ease(progress)
    y_offset = int(20 * (1 - alpha))  # Slide up from 20px below
    opacity = alpha  # Fade in simultaneously
```

### Staggered Bullet Points

Bullets appear one by one with slight delay, centered on screen.

```python
def animated_bullets(draw, items, y_start, frame, delay_start, color, font):
    """Render centered bullet points with staggered animation."""
    for i, text in enumerate(items):
        # Each bullet starts 0.8s after the previous
        progress = max(0, min(1,
            (frame - FPS * (delay_start + i * 0.8)) / (FPS * 0.6)))
        if progress > 0:
            y = y_start + i * 55
            alpha = ease(progress)
            offset = int(15 * (1 - alpha))

            # Calculate centered position
            tw = draw.textlength(text, font=font)
            sx = (W - 22 - tw) / 2

            # Draw bullet dot
            dot_color = tuple(int(c * alpha) for c in color)
            draw.ellipse([sx, y + 8 + offset, sx + 14, y + 22 + offset],
                        fill=dot_color)

            # Draw text
            text_color = tuple(int(255 * alpha) for _ in range(3))
            draw.text((sx + 22, y + offset), text,
                     fill=text_color, font=font)
```

### Centered Text Helper

```python
def centered_text(draw, y, text, font, fill=(255, 255, 255)):
    """Draw text horizontally centered at given y position."""
    tw = draw.textlength(text, font=font)
    draw.text(((W - tw) / 2, y), text, fill=fill, font=font)
```

### Multi-Color Brand Logo

Render a logo with different colors per segment (e.g., "PUREBRAIN.ai").

```python
def draw_brand_text(draw, x, y, font, parts):
    """
    Draw multi-colored text segments.
    parts = [("PURE", blue), ("BR", blue), ("AI", orange), ("N", blue), (".ai", white)]
    """
    cursor = x
    for text, color in parts:
        draw.text((cursor, y), text, fill=color, font=font)
        cursor += draw.textlength(text, font=font)
    return cursor - x  # Total width

# Center it:
def draw_brand_centered(draw, y, font, parts):
    total = sum(draw.textlength(t, font=font) for t, _ in parts)
    x = (W - total) / 2
    draw_brand_text(draw, x, y, font, parts)
```

### Accent Line

Thin colored line for visual separation.

```python
def draw_accent_line(draw, y, width=200, color=BRAND_PRIMARY):
    x0 = (W - width) / 2
    draw.rectangle([x0, y, x0 + width, y + 3], fill=color)
```

### Scene Fade Out

Fade to dark at end of a scene.

```python
# In render loop, at end of last scene:
if local_frame > scene_frames - FPS * 1.5:
    fade = (local_frame - (scene_frames - FPS * 1.5)) / (FPS * 1.5)
    overlay = Image.new('RGB', (W, H), BRAND_DARK)
    bg = Image.blend(bg, overlay, min(fade, 1.0))
```

---

## ffmpeg Audio Mixing Reference

```bash
# Basic: frames + audio
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -i music.mp3 \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest output.mp4

# With fade in/out and volume control
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -i music.mp3 \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -af "afade=t=in:st=0:d=2,afade=t=out:st=52:d=4,volume=0.7" \
  -shortest output.mp4

# Parameters:
# -framerate 30     : 30 FPS input
# -crf 23           : Quality (18=high, 23=medium, 28=low)
# -preset medium    : Encoding speed vs compression (ultrafast to veryslow)
# -pix_fmt yuv420p  : Maximum compatibility
# afade=t=in:d=2    : Audio fade in over 2 seconds
# afade=t=out:st=52:d=4  : Audio fade out starting at 52s over 4s
# volume=0.7        : 70% volume (background music level)
# -shortest         : End when shortest stream ends
```

---

## Royalty-Free Music Sources

| Source | URL | License |
|--------|-----|---------|
| Mixkit | mixkit.co/free-stock-music/ | Free, no attribution |
| Pixabay Music | pixabay.com/music/ | Free, no attribution |
| Free Music Archive | freemusicarchive.org | Various CC licenses |

**Recommended**: Mixkit ambient tracks work great for corporate/presentation videos. Direct download via `https://assets.mixkit.co/music/{id}/{id}.mp3`.

---

## Font Recommendations

| Font | Use | Source |
|------|-----|--------|
| Montserrat Bold | Titles, headings | Google Fonts |
| Montserrat Light | Subtitles | Google Fonts |
| Poppins Medium | Body text, bullets | Google Fonts |
| Poppins Light | Labels, small text | Google Fonts |

```bash
# Download from Google Fonts or use:
pip install fonttools
# Then download TTF files manually from fonts.google.com
```

---

## Production Checklist

- [ ] Define brand colors (primary, accent, dark background)
- [ ] Download/prepare background images (1920x1080 minimum)
- [ ] Download fonts (TTF format)
- [ ] Download music track
- [ ] Define scenes (name, duration, background)
- [ ] Write render script with all scene content
- [ ] Render frames (expect ~5-10 min for 1500+ frames)
- [ ] Compile with ffmpeg
- [ ] Review output, adjust timing/content
- [ ] Re-render if needed (only changed scenes if possible)

---

## Performance Notes

- **Frame rendering**: ~1500 frames takes 5-10 minutes on a standard VPS
- **ffmpeg compilation**: ~30 seconds for a 56-second video
- **File sizes**: ~21MB for 56s 1080p video with audio
- **Memory**: Peak ~200MB during rendering
- **Disk**: ~3GB for frame PNGs (deleted after compilation)

---

## Verified Working

- [x] 1920x1080 @ 30fps rendering
- [x] Ken Burns zoom on background images
- [x] Cubic ease-out text animations
- [x] Staggered bullet point entrance
- [x] Multi-color brand text rendering
- [x] Accent lines and visual separators
- [x] Global fade-in/fade-out
- [x] ffmpeg compilation with audio mixing
- [x] Audio fade in/out and volume control
- [x] Mixkit music download and integration

---

*Created by Tether Collective — from the PureBrain Smart City video project (March 2026)*

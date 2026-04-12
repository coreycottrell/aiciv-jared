#!/usr/bin/env python3
"""
Blog Banner Generator: "Something Big Already Happened — You Just Weren't Invited Yet"
Responding to Matt Shumer's "Something Big Is Happening"

Visual concept:
- Dark deep space background (#080a12)
- Rising inflection curve / wave representing the AI moment
- Neural network nodes scattered
- Glowing orbs in brand colors at the edges
- Bold title text centered
- PureBrain.ai branding bottom-left corner
- Subtle "inflection point" arrow/wave energy

Size: 1200x630 (standard OG image / blog banner)

Brand colors:
- PT Blue  #2a93c1  (42, 147, 193)
- PT Orange #f1420b  (241, 66, 11)
- Dark bg  #080a12  (8, 10, 18)
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
import random

# ---- Paths ----
BASE_DIR = Path("/home/jared/projects/AI-CIV/aether")
ICON_PATH = BASE_DIR / "docs/assets/logos/purebrain-icon.png"
BANNER_OUT = BASE_DIR / "exports/blog-something-big/banner.png"
OG_OUT     = BASE_DIR / "exports/blog-something-big/og.png"

# ---- Brand colors ----
PT_BLUE   = (42, 147, 193)
PT_ORANGE = (241, 66, 11)
PT_WHITE  = (255, 255, 255)
DARK_BG   = (8, 10, 18)

# ---- Dimensions (OG standard) ----
WIDTH  = 1200
HEIGHT = 630

random.seed(42)


# ================================================
#  STEP 1: Background gradient
# ================================================
def make_background(w, h):
    img = Image.new("RGB", (w, h), DARK_BG)
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            fy = y / h
            fx = x / w
            # Slight radial vignette — center slightly brighter
            cx_dist = abs(fx - 0.5)
            cy_dist = abs(fy - 0.5)
            radial = 1.0 - (cx_dist**2 + cy_dist**2) * 0.6
            radial = max(0.0, min(1.0, radial))
            r = int(DARK_BG[0] + 8 * radial)
            g = int(DARK_BG[1] + 10 * radial)
            b = int(DARK_BG[2] + 22 * radial)
            pixels[x, y] = (
                min(255, r),
                min(255, g),
                min(255, b),
            )
    return img


# ================================================
#  STEP 2: Glow orb (additive blending)
# ================================================
def add_glow_orb(img, cx, cy, radius, color, intensity=0.45):
    w, h = img.size
    pixels = img.load()
    x_min = max(0, cx - radius * 2)
    x_max = min(w, cx + radius * 2)
    y_min = max(0, cy - radius * 2)
    y_max = min(h, cy + radius * 2)
    sigma_sq = (radius * 0.65) ** 2
    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            dist_sq = (x - cx) ** 2 + (y - cy) ** 2
            if dist_sq < (radius * 2) ** 2:
                glow = math.exp(-dist_sq / (2 * sigma_sq)) * intensity
                cur = pixels[x, y]
                pixels[x, y] = (
                    min(255, int(cur[0] + color[0] * glow)),
                    min(255, int(cur[1] + color[1] * glow)),
                    min(255, int(cur[2] + color[2] * glow)),
                )
    return img


def add_all_orbs(img, w, h):
    configs = [
        # x_frac  y_frac  radius  color      intensity
        (0.05,   0.15,   160,   PT_BLUE,   0.38),
        (0.95,   0.10,   140,   PT_ORANGE, 0.32),
        (0.92,   0.88,   180,   PT_BLUE,   0.30),
        (0.08,   0.85,   130,   PT_ORANGE, 0.28),
        (0.50,   0.05,   200,   PT_BLUE,   0.20),  # top center glow
        (0.50,   0.95,   160,   PT_ORANGE, 0.18),  # bottom center glow
        (0.75,   0.50,   100,   PT_ORANGE, 0.22),
        (0.25,   0.50,    90,   PT_BLUE,   0.20),
    ]
    print("  Adding glow orbs...")
    for x_f, y_f, r, color, intensity in configs:
        img = add_glow_orb(img, int(w * x_f), int(h * y_f), r, color, intensity)
    return img


# ================================================
#  STEP 3: Inflection wave — the "something big" visual
# ================================================
def draw_inflection_wave(img, w, h):
    """Draw a rising S-curve / inflection wave across the image.
    This represents the AI inflection point — slow start, then explosive rise.
    """
    draw = ImageDraw.Draw(img)

    # Build wave points using sigmoid-like curve
    num_points = 300
    wave_pts = []
    for i in range(num_points):
        fx = i / (num_points - 1)
        # Sigmoid centered at 0.6 — flat left, steep rise right
        sig = 1 / (1 + math.exp(-12 * (fx - 0.58)))
        # Map sig to y: 0.82 (near bottom) to 0.22 (near top) of image
        fy = 0.82 - sig * 0.60
        wave_pts.append((int(fx * w), int(fy * h)))

    # Draw thick outer glow (wider, dimmer)
    for thickness, alpha in [(8, 0.12), (5, 0.25), (3, 0.55), (1, 1.0)]:
        line_color = (
            int(PT_BLUE[0] * alpha + PT_ORANGE[0] * (1 - alpha) * 0.3),
            int(PT_BLUE[1] * alpha),
            int(PT_BLUE[2] * alpha),
        )
        for i in range(len(wave_pts) - 1):
            x1, y1 = wave_pts[i]
            x2, y2 = wave_pts[i + 1]
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=thickness)

    # Draw the inflection point dot — hotspot at ~60% x
    infl_x = int(0.60 * w)
    infl_sig = 1 / (1 + math.exp(-12 * (0.60 - 0.58)))
    infl_y = int((0.82 - infl_sig * 0.60) * h)

    # Orange glow at inflection
    for r in range(22, 0, -1):
        alpha = (1 - r / 22) * 0.9
        color = (
            min(255, int(PT_ORANGE[0] * alpha + DARK_BG[0] * (1 - alpha))),
            min(255, int(PT_ORANGE[1] * alpha + DARK_BG[1] * (1 - alpha))),
            min(255, int(PT_ORANGE[2] * alpha + DARK_BG[2] * (1 - alpha))),
        )
        draw.ellipse([infl_x - r, infl_y - r, infl_x + r, infl_y + r], fill=color)

    # Arrow pointing up-right from inflection point
    arrow_len = 60
    arrow_angle = -0.55  # radians (up-right)
    ax = infl_x + int(math.cos(arrow_angle) * arrow_len)
    ay = infl_y + int(math.sin(arrow_angle) * arrow_len)
    draw.line([(infl_x, infl_y), (ax, ay)], fill=PT_ORANGE, width=3)
    # Arrow head
    head_size = 10
    for angle_offset in [0.5, -0.5]:
        hx = ax - int(math.cos(arrow_angle + math.pi + angle_offset) * head_size)
        hy = ay - int(math.sin(arrow_angle + math.pi + angle_offset) * head_size)
        draw.line([(ax, ay), (hx, hy)], fill=PT_ORANGE, width=3)

    return img, wave_pts


# ================================================
#  STEP 4: Neural network nodes
# ================================================
def draw_neural_network(img, w, h, wave_pts):
    draw = ImageDraw.Draw(img)

    # Generate nodes — more toward the right (rising) side
    nodes = []
    for _ in range(55):
        # Bias toward right half
        fx = random.uniform(0.0, 1.0)
        fy = random.uniform(0.0, 1.0)
        # Skip nodes that would overlap the center text safe zone
        cx_dist = abs(fx - 0.5)
        cy_dist = abs(fy - 0.5)
        if cx_dist < 0.28 and cy_dist < 0.25:
            continue
        x = int(fx * w)
        y = int(fy * h)
        size = random.randint(2, 7)
        # Color: right side leans orange, left side leans blue
        if fx > 0.6:
            color = PT_ORANGE if random.random() > 0.5 else PT_BLUE
        else:
            color = PT_BLUE
        brightness = random.uniform(0.4, 0.9)
        nodes.append((x, y, size, color, brightness))

    # Connections
    for i, (x1, y1, s1, c1, b1) in enumerate(nodes):
        for j, (x2, y2, s2, c2, b2) in enumerate(nodes[i + 1:], i + 1):
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if dist < 220:
                alpha = (1 - dist / 220) * min(b1, b2) * 0.35
                line_color = tuple(int(c * alpha) for c in PT_BLUE)
                draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)

    # Nodes themselves
    for x, y, size, color, brightness in nodes:
        node_c = tuple(min(255, int(c * brightness)) for c in color)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=node_c)
        if size > 4:
            cs = max(1, size // 3)
            center_c = tuple(min(255, int(c * min(1.0, brightness * 1.4))) for c in color)
            draw.ellipse([x - cs, y - cs, x + cs, y + cs], fill=center_c)

    return img


# ================================================
#  STEP 5: Text — title + PureBrain brand
# ================================================
def add_text(img, w, h):
    draw = ImageDraw.Draw(img)

    # Font loading
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    reg_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    def load_font(paths, size):
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
        return ImageFont.load_default()

    title_font   = load_font(font_paths, 62)
    sub_font     = load_font(font_paths, 28)
    brand_font   = load_font(font_paths, 26)
    kicker_font  = load_font(reg_font_paths, 22)

    # ---- Title: two lines ----
    line1 = "Something Big Already Happened"
    line2 = "You Just Weren't Invited Yet"

    # Measure line1
    bb1 = draw.textbbox((0, 0), line1, font=title_font)
    lw1 = bb1[2] - bb1[0]
    lh1 = bb1[3] - bb1[1]

    # Measure line2
    bb2 = draw.textbbox((0, 0), line2, font=title_font)
    lw2 = bb2[2] - bb2[0]
    lh2 = bb2[3] - bb2[1]

    line_gap = 14
    total_text_h = lh1 + line_gap + lh2

    # Center block vertically — slightly above center
    block_y = (h - total_text_h) // 2 - 30

    x1 = (w - lw1) // 2
    x2 = (w - lw2) // 2
    y1 = block_y
    y2 = block_y + lh1 + line_gap

    # Shadow
    for off in range(4, 0, -1):
        sh_alpha = int(180 * (1 - off / 4))
        draw.text((x1 + off, y1 + off), line1, font=title_font, fill=(0, 0, 0))
        draw.text((x2 + off, y2 + off), line2, font=title_font, fill=(0, 0, 0))

    # Main title — line1 white, line2 PT_BLUE
    draw.text((x1, y1), line1, font=title_font, fill=PT_WHITE)
    draw.text((x2, y2), line2, font=title_font, fill=PT_BLUE)

    # ---- Kicker above title ----
    kicker = "A response to Matt Shumer's 'Something Big Is Happening'"
    kb = draw.textbbox((0, 0), kicker, font=kicker_font)
    kw = kb[2] - kb[0]
    kx = (w - kw) // 2
    ky = y1 - 38
    draw.text((kx, ky), kicker, font=kicker_font, fill=(160, 170, 185))

    # ---- PureBrain brand — bottom left ----
    bx = 40
    by = h - 65

    logo_offset = 0
    if ICON_PATH.exists():
        try:
            icon = Image.open(ICON_PATH).convert("RGBA")
            icon = icon.resize((40, 40), Image.Resampling.LANCZOS)
            img.paste(icon, (bx, by + 5), icon)
            logo_offset = 50
        except Exception:
            pass

    brand_parts = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".ai", PT_WHITE),
    ]
    cur_x = bx + logo_offset
    for text, color in brand_parts:
        draw.text((cur_x, by + 8), text, font=brand_font, fill=color)
        tb = draw.textbbox((cur_x, by + 8), text, font=brand_font)
        cur_x = tb[2]

    # ---- Bottom right tag ----
    tag = "purebrain.ai"
    tb = draw.textbbox((0, 0), tag, font=kicker_font)
    tw = tb[2] - tb[0]
    draw.text((w - tw - 40, h - 50), tag, font=kicker_font, fill=(80, 100, 120))

    return img


# ================================================
#  MAIN
# ================================================
def generate(output_path, w=WIDTH, h=HEIGHT):
    print(f"Generating {w}x{h} banner -> {output_path}")

    print("  Building background...")
    img = make_background(w, h)

    print("  Adding glow orbs...")
    img = add_all_orbs(img, w, h)

    print("  Drawing inflection wave...")
    img, wave_pts = draw_inflection_wave(img, w, h)

    print("  Drawing neural network...")
    img = draw_neural_network(img, w, h, wave_pts)

    print("  Adding text and branding...")
    img = add_text(img, w, h)

    BANNER_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", quality=95)
    print(f"  Saved: {output_path}")
    return img


if __name__ == "__main__":
    # Banner (1200x630)
    generate(BANNER_OUT, WIDTH, HEIGHT)

    # OG image — same dimensions per spec
    generate(OG_OUT, WIDTH, HEIGHT)

    print("\nDone. Both files saved:")
    print(f"  banner.png -> {BANNER_OUT}")
    print(f"  og.png     -> {OG_OUT}")

#!/usr/bin/env python3
"""
Generate blog banner images for:
"Your AI Has No Idea Who You Are"

Sizes:
  - 1200x630 OG/blog banner
  - 1080x1080 social square

Colors:
  PT Blue:   #2a93c1
  PT Orange: #f1420b
  Dark BG:   #080a12
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Brand colors
PT_BLUE   = (42, 147, 193)    # #2a93c1
PT_ORANGE = (241, 66, 11)     # #f1420b
DARK_BG   = (8, 10, 18)       # #080a12
WHITE     = (255, 255, 255)
SOFT_BLUE = (42, 147, 193, 80)   # transparent accent
SOFT_ORG  = (241, 66, 11, 60)

def draw_hex_icon(draw, cx, cy, size, outline_color, fill_alpha=30):
    """Draw a hexagon icon (PureBrain logo stand-in)."""
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = cx + size * math.cos(angle)
        py = cy + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=outline_color + (200,), fill=outline_color + (fill_alpha,))
    # Inner ring
    inner = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = cx + (size * 0.65) * math.cos(angle)
        py = cy + (size * 0.65) * math.sin(angle)
        inner.append((px, py))
    draw.polygon(inner, outline=outline_color + (120,), fill=None)

def draw_neural_dots(draw, w, h, count=60, seed=42):
    """Draw scattered neural network nodes with faint connecting lines."""
    random.seed(seed)
    nodes = [(random.randint(0, w), random.randint(0, h)) for _ in range(count)]
    # Draw faint connections
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes[i+1:i+4], i+1):
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if dist < w * 0.18:
                alpha = max(8, int(30 * (1 - dist / (w * 0.18))))
                color = PT_BLUE + (alpha,)
                draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    # Draw nodes
    for (nx, ny) in nodes:
        r = random.randint(2, 5)
        is_orange = random.random() < 0.15
        col = PT_ORANGE + (160,) if is_orange else PT_BLUE + (140,)
        draw.ellipse([(nx-r, ny-r), (nx+r, ny+r)], fill=col)

def draw_brain_glow(img, cx, cy, radius):
    """Overlay a soft radial glow behind the brain area."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    steps = 30
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        alpha = int(18 * (1 - i / steps))
        col = PT_BLUE + (alpha,)
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=col)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    return img

def make_banner(width, height, filename):
    img = Image.new("RGBA", (width, height), DARK_BG + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Background gradient bands ---
    for y in range(height):
        t = y / height
        r = int(DARK_BG[0] + (PT_BLUE[0] - DARK_BG[0]) * 0.06 * (1 - t))
        g = int(DARK_BG[1] + (PT_BLUE[1] - DARK_BG[1]) * 0.06 * (1 - t))
        b = int(DARK_BG[2] + (PT_BLUE[2] - DARK_BG[2]) * 0.12 * (1 - t))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # --- Neural dot field ---
    draw_neural_dots(draw, width, height, count=80, seed=77)

    # --- Brain glow center ---
    img = draw_brain_glow(img, int(width * 0.5), int(height * 0.42), int(min(width, height) * 0.38))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Hexagon icon (top center) ---
    hex_cx = width // 2
    hex_cy = int(height * 0.22)
    hex_size = int(min(width, height) * 0.095)
    draw_hex_icon(draw, hex_cx, hex_cy, hex_size, PT_BLUE)
    # Inner brain-dot cluster
    for i in range(6):
        angle = math.radians(60 * i)
        dx = hex_cx + hex_size * 0.35 * math.cos(angle)
        dy = hex_cy + hex_size * 0.35 * math.sin(angle)
        draw.ellipse([(dx-3, dy-3), (dx+3, dy+3)], fill=PT_ORANGE + (200,))
    draw.ellipse([(hex_cx-4, hex_cy-4), (hex_cx+4, hex_cy+4)], fill=PT_BLUE + (255,))

    # --- Horizontal accent line ---
    margin = int(width * 0.10)
    accent_y = int(height * 0.36)
    draw.line([(margin, accent_y), (width - margin, accent_y)], fill=PT_BLUE + (60,), width=1)

    # --- Font loading ---
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    font_regular_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]

    bold_font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            bold_font_path = fp
            break

    reg_font_path = None
    for fp in font_regular_paths:
        if os.path.exists(fp):
            reg_font_path = fp
            break

    # Scale font sizes proportionally
    scale = width / 1200

    title_size    = int(68 * scale)
    sub_size      = int(26 * scale)
    brand_size    = int(30 * scale)
    url_size      = int(20 * scale)
    byline_size   = int(22 * scale)

    try:
        font_title  = ImageFont.truetype(bold_font_path, title_size) if bold_font_path else ImageFont.load_default()
        font_sub    = ImageFont.truetype(reg_font_path or bold_font_path, sub_size) if (reg_font_path or bold_font_path) else ImageFont.load_default()
        font_brand  = ImageFont.truetype(bold_font_path, brand_size) if bold_font_path else ImageFont.load_default()
        font_url    = ImageFont.truetype(reg_font_path or bold_font_path, url_size) if (reg_font_path or bold_font_path) else ImageFont.load_default()
        font_byline = ImageFont.truetype(reg_font_path or bold_font_path, byline_size) if (reg_font_path or bold_font_path) else ImageFont.load_default()
    except Exception:
        font_title = font_sub = font_brand = font_url = font_byline = ImageFont.load_default()

    # --- Title text: two lines ---
    line1 = "Your AI Has No Idea"
    line2 = "Who You Are"

    def centered_text(draw, text, y, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        draw.text((x, y), text, font=font, fill=fill)
        return bbox[3] - bbox[1]

    title_y = int(height * 0.40)
    lh1 = centered_text(draw, line1, title_y, font_title, WHITE)
    title_y2 = title_y + lh1 + int(8 * scale)
    centered_text(draw, line2, title_y2, font_title, WHITE)

    # --- Subtitle ---
    subtitle = "Why your AI meets you for the first time. Every. Single. Day."
    sub_y = title_y2 + int(title_size * 1.15)
    centered_text(draw, subtitle, sub_y, font_sub, (180, 210, 230, 230))

    # --- Orange accent line under subtitle ---
    line_y = sub_y + int(sub_size * 1.6)
    line_w = int(width * 0.15)
    draw.line([(width // 2 - line_w, line_y), (width // 2 + line_w, line_y)],
              fill=PT_ORANGE + (200,), width=2)

    # --- PureBrain brand name (color-coded) ---
    brand_y = int(height * 0.845)
    brand_text_parts = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".ai", WHITE),
    ]

    # Measure total width
    total_brand_w = sum(
        draw.textbbox((0, 0), t, font=font_brand)[2] - draw.textbbox((0, 0), t, font=font_brand)[0]
        for t, _ in brand_text_parts
    )
    bx = (width - total_brand_w) // 2
    for part_text, part_color in brand_text_parts:
        bbox = draw.textbbox((0, 0), part_text, font=font_brand)
        draw.text((bx, brand_y), part_text, font=font_brand, fill=part_color + (255,))
        bx += bbox[2] - bbox[0]

    # --- URL ---
    url_text = "purebrain.ai/blog"
    url_y = brand_y + int(brand_size * 1.4)
    centered_text(draw, url_text, url_y, font_url, (120, 160, 180, 200))

    # --- Byline ---
    byline_text = "by Jared Sanborn  |  Pure Technology"
    byline_y = url_y + int(url_size * 1.5)
    centered_text(draw, byline_text, byline_y, font_byline, (100, 140, 165, 180))

    # --- Bottom orange accent line ---
    b_margin = int(width * 0.10)
    b_line_y = height - int(height * 0.04)
    draw.line([(b_margin, b_line_y), (width - b_margin, b_line_y)],
              fill=PT_ORANGE + (80,), width=1)

    # --- Save ---
    out = img.convert("RGB")
    out_path = os.path.join(OUTPUT_DIR, filename)
    out.save(out_path, "PNG", optimize=True)
    print(f"Saved: {out_path} ({width}x{height})")
    return out_path


if __name__ == "__main__":
    og_path  = make_banner(1200, 630, "your-ai-has-no-idea-who-you-are - banner-1200x630.png")
    sq_path  = make_banner(1080, 1080, "your-ai-has-no-idea-who-you-are - banner-1080x1080.png")
    print("\nBanner generation complete.")
    print(f"  OG:     {og_path}")
    print(f"  Square: {sq_path}")

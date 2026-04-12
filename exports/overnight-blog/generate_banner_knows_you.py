#!/usr/bin/env python3
"""
Banner Generator for PureBrain Blog Post
"The AI That Knows You Before You Even Speak"
Size: 1200x628 (LinkedIn/OG optimal)
Colors: #2a93c1 (Cerulean Blue), #f1420b (Orange), #ffffff (White)
Background: #080a12 (Pure Tech Dark)
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os
import random

random.seed(42)  # deterministic

# Canvas Setup
WIDTH, HEIGHT = 1200, 628
BG_COLOR = (8, 10, 18)       # #080a12
BLUE = (42, 147, 193)         # #2a93c1
ORANGE = (241, 66, 11)        # #f1420b
WHITE = (255, 255, 255)
LIGHT_BLUE = (42, 147, 193)
DIM_WHITE = (220, 230, 240)

img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img, "RGBA")

# --- Background: Neural grid ---
for x in range(0, WIDTH, 55):
    alpha = random.randint(6, 18)
    draw.line([(x, 0), (x, HEIGHT)], fill=(42, 147, 193, alpha), width=1)
for y in range(0, HEIGHT, 55):
    alpha = random.randint(6, 18)
    draw.line([(0, y), (WIDTH, y)], fill=(42, 147, 193, alpha), width=1)

# --- Large central glow (blue) ---
glow_cx, glow_cy = 820, 290
for r in range(320, 20, -18):
    alpha = int((320 - r) / 320 * 22)
    draw.ellipse(
        [glow_cx - r * 1.5, glow_cy - r, glow_cx + r * 1.5, glow_cy + r],
        fill=(42, 147, 193, alpha)
    )

# --- Orange accent glow (bottom-left) ---
for r in range(200, 15, -14):
    alpha = int((200 - r) / 200 * 18)
    draw.ellipse(
        [90 - r, HEIGHT - 90 - r, 90 + r, HEIGHT - 90 + r],
        fill=(241, 66, 11, alpha)
    )

# --- Orange accent glow (top-right) ---
for r in range(150, 10, -12):
    alpha = int((150 - r) / 150 * 14)
    draw.ellipse(
        [WIDTH - 90 - r, 60 - r, WIDTH - 90 + r, 60 + r],
        fill=(241, 66, 11, alpha)
    )

# --- Hexagon helper ---
def hexagon_points(cx, cy, radius, rotation=0):
    points = []
    for i in range(6):
        angle = math.radians(60 * i + rotation)
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        points.append((px, py))
    return points

# --- Main brain hexagon (right side, large, glowing) ---
brain_cx, brain_cy = 840, 300
# Outer glow rings
for ring_r in range(195, 140, -8):
    alpha = int((195 - ring_r) / 55 * 35)
    pts = hexagon_points(brain_cx, brain_cy, ring_r, 30)
    draw.polygon(pts, fill=(42, 147, 193, alpha))

# Hexagon outline (bright blue)
hex_pts = hexagon_points(brain_cx, brain_cy, 148, 30)
draw.polygon(hex_pts, outline=(42, 147, 193, 230), fill=(8, 15, 28, 200))
draw.polygon(hex_pts, outline=(42, 147, 193, 180))

# Inner hexagon (smaller, orange accent)
inner_hex_pts = hexagon_points(brain_cx, brain_cy, 88, 30)
draw.polygon(inner_hex_pts, outline=(241, 66, 11, 140), fill=(8, 10, 18, 0))

# Innermost hexagon
micro_hex_pts = hexagon_points(brain_cx, brain_cy, 44, 30)
draw.polygon(micro_hex_pts, outline=(42, 147, 193, 190), fill=(42, 147, 193, 18))

# --- Neural nodes and connections radiating from brain ---
node_positions = []
for angle_deg in range(0, 360, 30):
    for dist in [165, 215, 265]:
        angle_rad = math.radians(angle_deg + random.randint(-12, 12))
        nx = brain_cx + dist * math.cos(angle_rad)
        ny = brain_cy + dist * math.sin(angle_rad)
        if 40 < nx < WIDTH - 40 and 20 < ny < HEIGHT - 20:
            node_positions.append((nx, ny, dist))

# Draw connection lines first
for nx, ny, dist in node_positions:
    alpha = max(20, 80 - int(dist / 4))
    if dist < 200:
        color = (42, 147, 193, alpha)
    else:
        color = (241, 66, 11, max(12, alpha - 20))
    draw.line([(brain_cx, brain_cy), (nx, ny)], fill=color, width=1)

# Draw nodes
for nx, ny, dist in node_positions:
    r = 4 if dist < 200 else 3
    alpha = max(100, 200 - int(dist / 2))
    color = BLUE if dist < 200 else ORANGE
    draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=color + (alpha,))

# --- Small floating nodes across the left side ---
for _ in range(28):
    fx = random.randint(60, 560)
    fy = random.randint(40, HEIGHT - 40)
    fr = random.choice([2, 2, 3, 3, 4])
    fa = random.randint(60, 160)
    c = random.choice([BLUE, ORANGE])
    draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=c + (fa,))

# --- Connection lines between floating nodes (left side atmosphere) ---
float_nodes_left = [(random.randint(60, 480), random.randint(60, HEIGHT - 60)) for _ in range(12)]
for i in range(len(float_nodes_left) - 1):
    x1, y1 = float_nodes_left[i]
    x2, y2 = float_nodes_left[i + 1]
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if dist < 200:
        draw.line([(x1, y1), (x2, y2)], fill=(42, 147, 193, 28), width=1)

# --- Font loading ---
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]

def load_font(size):
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def load_regular_font(size):
    regular_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for fp in regular_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return load_font(size)

font_logo = load_font(36)
font_title_large = load_font(58)
font_title_medium = load_font(52)
font_subtitle = load_regular_font(26)
font_small = load_regular_font(20)

# --- Helper: centered text bounding box ---
def text_width(draw_obj, text, font):
    bbox = draw_obj.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def text_height(draw_obj, text, font):
    bbox = draw_obj.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]

# --- PUREBRAIN logo text (top-left, safe zone) ---
logo_x = 68
logo_y = 46

segments = [
    ("PUREBR", BLUE),
    ("AI", ORANGE),
    ("N", BLUE),
    (".ai", WHITE),
]

cursor_x = logo_x
for seg_text, seg_color in segments:
    draw.text((cursor_x, logo_y), seg_text, font=font_logo, fill=seg_color)
    cursor_x += text_width(draw, seg_text, font_logo) + 1

# --- Separator line below logo ---
draw.line([(logo_x, logo_y + 52), (cursor_x - 1, logo_y + 52)], fill=(42, 147, 193, 100), width=1)

# --- Main blog post title ---
# Title: "The AI That Knows You"  (line 1)
#        "Before You Even Speak"  (line 2)

title_line1 = "The AI That Knows You"
title_line2 = "Before You Even Speak"

# Determine if lines fit at 58px, fall back to 52
tw1_large = text_width(draw, title_line1, font_title_large)
tw2_large = text_width(draw, title_line2, font_title_large)
title_font = font_title_large if max(tw1_large, tw2_large) <= 560 else font_title_medium

tw1 = text_width(draw, title_line1, title_font)
tw2 = text_width(draw, title_line2, title_font)
th = text_height(draw, title_line1, title_font)

title_y_start = 160

# Shadow pass (dark offset for legibility)
shadow_offset = 3
for line, ty_offset in [(title_line1, 0), (title_line2, th + 18)]:
    draw.text((logo_x + shadow_offset, title_y_start + ty_offset + shadow_offset),
              line, font=title_font, fill=(0, 0, 0, 160))

# Title line 1: white
draw.text((logo_x, title_y_start), title_line1, font=title_font, fill=WHITE)

# Title line 2: orange accent on "Before You Even Speak"
line2_y = title_y_start + th + 18
draw.text((logo_x, line2_y), title_line2, font=title_font, fill=ORANGE)

# --- Subtitle / descriptor line ---
subtitle_text = "Why Context Is the New Competitive Edge"
subtitle_y = line2_y + th + 28
draw.text((logo_x, subtitle_y), subtitle_text, font=font_subtitle, fill=(180, 210, 230, 220))

# --- Horizontal accent line (under subtitle) ---
line_y = subtitle_y + 42
draw.line([(logo_x, line_y), (logo_x + 340, line_y)], fill=(42, 147, 193, 160), width=2)

# --- Author tag ---
author_y = line_y + 16
author_text = "by Aether"
draw.text((logo_x, author_y), author_text, font=font_small, fill=(42, 147, 193, 200))

# --- Bottom bar (site URL + brand reinforcement) ---
bar_y = HEIGHT - 52
draw.rectangle([(0, bar_y), (WIDTH, HEIGHT)], fill=(12, 16, 28, 220))
draw.line([(0, bar_y), (WIDTH, bar_y)], fill=(42, 147, 193, 80), width=1)

# Site URL bottom left
draw.text((logo_x, bar_y + 14), "purebrain.ai", font=font_small, fill=(42, 147, 193, 200))

# Tagline bottom right
tagline = "AI that grows with you"
tw_tag = text_width(draw, tagline, font_small)
draw.text((WIDTH - tw_tag - logo_x, bar_y + 14), tagline, font=font_small, fill=(255, 255, 255, 130))

# --- Orange accent horizontal line across brain hex mid ---
draw.line([(brain_cx - 148, brain_cy), (brain_cx + 148, brain_cy)],
          fill=(241, 66, 11, 50), width=1)

# --- Final output ---
out_path = "/home/jared/projects/AI-CIV/aether/exports/overnight-blog/the-ai-that-knows-you-before-you-speak-banner.png"
img.save(out_path, "PNG", optimize=True)
print(f"Banner saved: {out_path}")
print(f"Dimensions: {img.size[0]}x{img.size[1]}")

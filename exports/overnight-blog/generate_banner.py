#!/usr/bin/env python3
"""
Banner Generator for PureBrain Blog Post
"Your AI Doesn't Work For You — You Work For It"
Size: 1200x628 (LinkedIn/OG optimal)
Colors: #2a93c1 (Cerulean Blue), #f1420b (Orange), #ffffff (White)
Background: #080a12 (Pure Tech Dark)
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os
import random

# ─── Canvas Setup ────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1200, 628
BG_COLOR = (8, 10, 18)         # #080a12
BLUE = (42, 147, 193)          # #2a93c1
ORANGE = (241, 66, 11)         # #f1420b
WHITE = (255, 255, 255)
DIM_BLUE = (42, 147, 193, 40)  # translucent blue for particles
DIM_ORANGE = (241, 66, 11, 25) # translucent orange

img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img, "RGBA")

# ─── Background: Neural Network Grid ─────────────────────────────────────────
# Draw faint grid lines suggesting a neural/circuit board pattern
for x in range(0, WIDTH, 60):
    alpha = random.randint(8, 20)
    draw.line([(x, 0), (x, HEIGHT)], fill=(42, 147, 193, alpha), width=1)
for y in range(0, HEIGHT, 60):
    alpha = random.randint(8, 20)
    draw.line([(0, y), (WIDTH, y)], fill=(42, 147, 193, alpha), width=1)

# ─── Background: Radial glow from center-right ───────────────────────────────
# Simulate a glow using concentric ellipses with decreasing opacity
glow_cx, glow_cy = 860, 314
for r in range(280, 30, -20):
    alpha = int((280 - r) / 280 * 18)
    draw.ellipse(
        [glow_cx - r * 1.4, glow_cy - r, glow_cx + r * 1.4, glow_cy + r],
        fill=(42, 147, 193, alpha)
    )

# Orange accent glow bottom-left
for r in range(180, 20, -15):
    alpha = int((180 - r) / 180 * 14)
    draw.ellipse(
        [80 - r, HEIGHT - 80 - r, 80 + r, HEIGHT - 80 + r],
        fill=(241, 66, 11, alpha)
    )

# ─── Hexagon Helper ──────────────────────────────────────────────────────────
def hexagon_points(cx, cy, radius, rotation=0):
    points = []
    for i in range(6):
        angle = math.radians(60 * i + rotation)
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        points.append((px, py))
    return points

# ─── PureBrain Hexagon Icon (right side, large, semi-transparent) ────────────
hex_cx, hex_cy = 920, 314
hex_outer = 160
hex_inner = 140

# Outer hex border
outer_pts = hexagon_points(hex_cx, hex_cy, hex_outer, rotation=30)
draw.polygon(outer_pts, outline=(42, 147, 193, 120), fill=(8, 10, 18, 0))
# Draw the outline manually with width simulation
for i in range(6):
    p1 = outer_pts[i]
    p2 = outer_pts[(i + 1) % 6]
    draw.line([p1, p2], fill=(42, 147, 193, 160), width=3)

# Inner hex fill (very dark, slightly blue-tinted)
inner_pts = hexagon_points(hex_cx, hex_cy, hex_inner - 8, rotation=30)
draw.polygon(inner_pts, fill=(12, 20, 35, 200))

# Neural nodes inside hex — brain-like cluster
node_positions = [
    (hex_cx, hex_cy - 50),         # top
    (hex_cx - 45, hex_cy - 20),    # upper-left
    (hex_cx + 45, hex_cy - 20),    # upper-right
    (hex_cx - 60, hex_cy + 30),    # lower-left
    (hex_cx + 60, hex_cy + 30),    # lower-right
    (hex_cx, hex_cy + 60),         # bottom
    (hex_cx, hex_cy),              # center
]

# Draw connections first
connections = [(0,1),(0,2),(1,2),(1,3),(2,4),(3,4),(3,5),(4,5),(6,0),(6,1),(6,2),(6,3),(6,4),(6,5)]
for a, b in connections:
    draw.line([node_positions[a], node_positions[b]], fill=(42, 147, 193, 80), width=1)

# Draw nodes
for i, (nx, ny) in enumerate(node_positions):
    if i == 6:  # center node — orange
        draw.ellipse([nx-8, ny-8, nx+8, ny+8], fill=ORANGE)
        draw.ellipse([nx-5, ny-5, nx+5, ny+5], fill=(255, 140, 80))
    else:
        draw.ellipse([nx-5, ny-5, nx+5, ny+5], fill=BLUE)
        draw.ellipse([nx-3, ny-3, nx+3, ny+3], fill=(180, 220, 245))

# Small hex decorators scattered in background (far right, muted)
for hx, hy, hr, alpha in [(1100, 80, 30, 40), (1140, 550, 20, 30), (60, 80, 25, 35)]:
    pts = hexagon_points(hx, hy, hr, rotation=30)
    for i in range(6):
        p1 = pts[i]
        p2 = pts[(i + 1) % 6]
        draw.line([p1, p2], fill=(42, 147, 193, alpha), width=1)

# ─── Accent line: left edge orange bar ───────────────────────────────────────
draw.rectangle([0, 0, 6, HEIGHT], fill=ORANGE)

# Top thin blue accent bar
draw.rectangle([0, 0, WIDTH, 3], fill=BLUE)

# ─── Typography ───────────────────────────────────────────────────────────────
# Font loading — try system fonts, fall back to default
def load_font(size, bold=False):
    """Attempt to load a clean system font."""
    font_candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    font_candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    candidates = font_candidates_bold if bold else font_candidates_regular
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

# Load fonts
font_headline_lg = load_font(52, bold=True)
font_headline_sm = load_font(44, bold=True)
font_subhead = load_font(26, bold=False)
font_logo = load_font(34, bold=True)
font_tag = load_font(20, bold=False)

# ─── Blog Title (left side, safe zone 80px margins) ──────────────────────────
# Title: "Your AI Doesn't Work For You"
# Subtitle line: "You Work For It."

title_x = 80
title_y_start = 130

# Eyebrow label
eyebrow = "AI PARTNERSHIP | LEADERSHIP"
draw.text((title_x, title_y_start - 45), eyebrow, font=font_tag, fill=(42, 147, 193, 220))

# Title line 1
line1 = "Your AI Doesn't"
draw.text((title_x, title_y_start), line1, font=font_headline_lg, fill=WHITE)

# Title line 2
line2 = "Work For You —"
draw.text((title_x, title_y_start + 62), line2, font=font_headline_lg, fill=WHITE)

# Title line 3 — orange accent on the inversion line
line3 = "You Work For It."
draw.text((title_x, title_y_start + 124), line3, font=font_headline_lg, fill=ORANGE)

# Divider line
draw.rectangle([title_x, title_y_start + 200, title_x + 420, title_y_start + 203], fill=(42, 147, 193, 180))

# Subheadline
sub1 = "The relationship every business leader"
sub2 = "has accidentally built with AI — and how to flip it."
draw.text((title_x, title_y_start + 218), sub1, font=font_subhead, fill=(200, 220, 235))
draw.text((title_x, title_y_start + 252), sub2, font=font_subhead, fill=(200, 220, 235))

# ─── Author attribution ───────────────────────────────────────────────────────
author_y = HEIGHT - 90
draw.text((title_x, author_y), "Jared Sanborn  |  purebrain.ai", font=font_tag, fill=(160, 190, 210))

# ─── PureBrain Logo (bottom center-left, safe from edges) ────────────────────
# Logo: "PUREBR" blue | "AI" orange | "N" blue | ".ai" white
logo_x = title_x
logo_y = HEIGHT - 55

# Build logo segments
logo_parts = [
    ("PUREBR", BLUE),
    ("AI", ORANGE),
    ("N", BLUE),
    (".ai", (220, 230, 240)),
]

cursor_x = logo_x
for text, color in logo_parts:
    draw.text((cursor_x, logo_y), text, font=font_logo, fill=color)
    # Measure width to advance cursor
    try:
        bbox = font_logo.getbbox(text)
        char_width = bbox[2] - bbox[0]
    except Exception:
        char_width = len(text) * 20  # fallback estimate
    cursor_x += char_width

# Small hex icon next to logo
logo_hex_x = cursor_x + 22
logo_hex_y = logo_y + 17
logo_hex_r = 14
lh_pts = hexagon_points(logo_hex_x, logo_hex_y, logo_hex_r, rotation=30)
for i in range(6):
    p1 = lh_pts[i]
    p2 = lh_pts[(i + 1) % 6]
    draw.line([p1, p2], fill=BLUE, width=2)
# Center dot
draw.ellipse([logo_hex_x - 3, logo_hex_y - 3, logo_hex_x + 3, logo_hex_y + 3], fill=ORANGE)

# ─── Save ─────────────────────────────────────────────────────────────────────
output_path = "/home/jared/projects/AI-CIV/aether/exports/overnight-blog/your-ai-doesnt-work-for-you-banner.png"
img.save(output_path, "PNG", optimize=True)
print(f"Banner saved: {output_path}")
print(f"Dimensions: {img.size}")

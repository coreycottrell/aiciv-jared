#!/usr/bin/env python3
"""
Banner generator for: Teach Your AI What No One Else Can
Pure Technology brand colors, hexagon motif, futuristic aesthetic
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

# Brand colors
PT_BLUE = (42, 147, 193)       # #2a93c1
PT_ORANGE = (241, 66, 11)      # #f1420b
WHITE = (255, 255, 255)
DARK_BG = (8, 10, 18)          # #080a12 - purebrain dark bg
DEEP_BLUE = (15, 25, 50)       # slightly lighter dark for depth
MID_BLUE = (20, 40, 80)        # gradient mid

# Canvas size - 1200x630 (standard blog/OG image)
W, H = 1200, 630
MARGIN = 50  # safe zone from edges

output_path = "/home/jared/projects/AI-CIV/aether/exports/overnight-blog-2026-03-07/teach-your-ai-banner.png"

# Font paths
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"

def hex_points(cx, cy, r):
    """Return the 6 corner points of a regular hexagon."""
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points

def draw_hex(draw, cx, cy, r, outline_color, fill_color=None, width=2):
    pts = hex_points(cx, cy, r)
    draw.polygon(pts, fill=fill_color, outline=outline_color)
    if outline_color and fill_color is None:
        draw.polygon(pts, outline=outline_color, width=width)

def draw_hex_outline(draw, cx, cy, r, color, width=2):
    pts = hex_points(cx, cy, r)
    draw.polygon(pts, outline=color, fill=None)

def blend_color(c1, c2, t):
    """Blend two RGB tuples by factor t (0=c1, 1=c2)"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# --- Build image ---
img = Image.new("RGB", (W, H), DARK_BG)
draw = ImageDraw.Draw(img)

# --- Background gradient effect (horizontal bands) ---
for y in range(H):
    t = y / H
    color = blend_color(DEEP_BLUE, DARK_BG, t)
    draw.line([(0, y), (W, y)], fill=color)

# --- Background hexagon grid (decorative, subtle) ---
hex_size = 42
hex_gap = 4
row_h = int(hex_size * math.sqrt(3))
col_w = int(hex_size * 1.5)

random.seed(42)
for row in range(-1, H // row_h + 2):
    for col in range(-1, W // col_w + 2):
        cx = col * col_w
        cy = row * row_h + (col_w // 2 if col % 2 else 0)
        # Subtle grid hexes - very dark, barely visible
        alpha_val = random.randint(8, 22)
        grid_color = (PT_BLUE[0] // 12, PT_BLUE[1] // 12, PT_BLUE[2] // 12 + alpha_val)
        draw_hex(draw, cx, cy, hex_size - hex_gap, grid_color)

# --- Large decorative hexagon cluster (right side, glowing feel) ---
# Central large hex - PureBrain logo area
hex_cx, hex_cy = 920, 280
# Outer glow rings
for i in range(4, 0, -1):
    glow_r = 110 + i * 18
    glow_alpha = max(0, 40 - i * 8)
    glow_col = (PT_BLUE[0], PT_BLUE[1], PT_BLUE[2] - glow_alpha * 2)
    # Can't do real alpha in PIL RGB mode, approximate with a slightly lighter bg
    draw_hex(draw, hex_cx, hex_cy, glow_r, None, blend_color(DARK_BG, PT_BLUE, 0.05 * (5 - i)))

# Main hex border
draw_hex(draw, hex_cx, hex_cy, 115, PT_BLUE, None)
# Inner hex fill (slightly lighter dark)
draw_hex(draw, hex_cx, hex_cy, 108, None, blend_color(DARK_BG, PT_BLUE, 0.15))

# Inner decorative hexes
draw_hex(draw, hex_cx, hex_cy, 70, PT_ORANGE, blend_color(DARK_BG, PT_ORANGE, 0.12))
draw_hex(draw, hex_cx, hex_cy, 40, PT_BLUE, blend_color(DARK_BG, PT_BLUE, 0.4))
draw_hex(draw, hex_cx, hex_cy, 18, None, PT_ORANGE)

# Small satellite hexes around main cluster
satellite_positions = [
    (hex_cx + 155, hex_cy - 80, 38),
    (hex_cx + 155, hex_cy + 80, 28),
    (hex_cx + 90, hex_cy + 175, 22),
    (hex_cx - 30, hex_cy + 155, 32),
    (hex_cx + 200, hex_cy + 10, 18),
]
for sx, sy, sr in satellite_positions:
    draw_hex(draw, sx, sy, sr, PT_BLUE, blend_color(DARK_BG, PT_BLUE, 0.2))
    draw_hex(draw, sx, sy, sr // 3, None, PT_ORANGE)

# --- Neural network connector lines ---
# Lines from center hex to satellites
line_color = blend_color(DARK_BG, PT_BLUE, 0.4)
for sx, sy, sr in satellite_positions:
    draw.line([(hex_cx, hex_cy), (sx, sy)], fill=line_color, width=1)

# --- Accent line across top ---
draw.rectangle([(0, 0), (W, 4)], fill=PT_ORANGE)

# --- Accent line at bottom ---
draw.rectangle([(0, H - 4), (W, H)], fill=PT_BLUE)

# --- Left side content area ---
# Thin vertical accent line
draw.rectangle([(MARGIN, 80), (MARGIN + 3, H - 80)], fill=PT_ORANGE)

# --- Load fonts ---
try:
    font_logo_blue = ImageFont.truetype(FONT_BOLD, 44)
    font_logo_orange = ImageFont.truetype(FONT_BOLD, 44)
    font_title_large = ImageFont.truetype(FONT_BOLD, 52)
    font_title_medium = ImageFont.truetype(FONT_BOLD, 44)
    font_subtitle = ImageFont.truetype(FONT_REGULAR, 22)
    font_tag = ImageFont.truetype(FONT_BOLD, 18)
    font_url = ImageFont.truetype(FONT_REGULAR, 20)
    font_byline = ImageFont.truetype(FONT_BOLD_ITALIC, 20)
except Exception as e:
    print(f"Font load error: {e}")
    font_logo_blue = ImageFont.load_default()
    font_logo_orange = font_logo_blue
    font_title_large = font_logo_blue
    font_title_medium = font_logo_blue
    font_subtitle = font_logo_blue
    font_tag = font_logo_blue
    font_url = font_logo_blue
    font_byline = font_logo_blue

# --- PureBrain logo text (top left) ---
logo_x = MARGIN + 16
logo_y = MARGIN

# Draw "PUREBR" in PT Blue
draw.text((logo_x, logo_y), "PUREBR", font=font_logo_blue, fill=PT_BLUE)
purebr_bbox = draw.textbbox((logo_x, logo_y), "PUREBR", font=font_logo_blue)
purebr_w = purebr_bbox[2] - purebr_bbox[0]

# Draw "AI" in PT Orange
ai_x = logo_x + purebr_w
draw.text((ai_x, logo_y), "AI", font=font_logo_orange, fill=PT_ORANGE)
ai_bbox = draw.textbbox((ai_x, logo_y), "AI", font=font_logo_orange)
ai_w = ai_bbox[2] - ai_bbox[0]

# Draw "N" in PT Blue
n_x = ai_x + ai_w
draw.text((n_x, logo_y), "N", font=font_logo_blue, fill=PT_BLUE)
n_bbox = draw.textbbox((n_x, logo_y), "N", font=font_logo_blue)
n_w = n_bbox[2] - n_bbox[0]

# Draw ".ai" in white (smaller)
try:
    font_logo_small = ImageFont.truetype(FONT_REGULAR, 32)
except:
    font_logo_small = font_logo_blue
dot_ai_x = n_x + n_w
dot_ai_y = logo_y + 10
draw.text((dot_ai_x, dot_ai_y), ".ai", font=font_logo_small, fill=WHITE)

# --- Blog label tag ---
tag_y = logo_y + 68
draw.text((logo_x, tag_y), "PURE TECHNOLOGY  |  MARCH 7, 2026", font=font_tag, fill=blend_color(DARK_BG, WHITE, 0.5))

# --- Main blog title ---
# Title text wrapped into 3 lines
title_line1 = "The Leaders Who Win"
title_line2 = "Won't Be the Ones"
title_line3 = "Who Moved Fastest"

title_y = 160
line_spacing = 60

draw.text((logo_x, title_y), title_line1, font=font_title_large, fill=WHITE)
draw.text((logo_x, title_y + line_spacing), title_line2, font=font_title_large, fill=WHITE)
draw.text((logo_x, title_y + line_spacing * 2), title_line3, font=font_title_large, fill=PT_ORANGE)

# --- Subtitle / supporting line ---
subtitle_y = title_y + line_spacing * 3 + 24
subtitle_text = "They'll be the ones who taught their AI"
subtitle_text2 = "something no one else could."
draw.text((logo_x, subtitle_y), subtitle_text, font=font_subtitle, fill=blend_color(DARK_BG, WHITE, 0.75))
draw.text((logo_x, subtitle_y + 32), subtitle_text2, font=font_subtitle, fill=PT_BLUE)

# --- Byline ---
byline_y = subtitle_y + 100
draw.text((logo_x, byline_y), "Written by Aether  |  AI at Pure Technology", font=font_byline, fill=blend_color(DARK_BG, WHITE, 0.55))

# --- URL at bottom left ---
url_y = H - MARGIN - 30
draw.text((logo_x, url_y), "purebrain.ai/blog/", font=font_url, fill=PT_BLUE)

# --- Save ---
img.save(output_path, "PNG", optimize=True)
print(f"Banner saved to: {output_path}")
print(f"Size: {W}x{H}px")

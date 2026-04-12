#!/usr/bin/env python3
"""
Blog Banner Generator: "The AI Trust Gap Is the Real Problem (Not the Technology)"
Size: 1456x816 (16:9)
Safe zone: x:182-1274, y:102-714
Brand colors: #2a93c1 (blue), #f1420b (orange)
V2 - improved layout, stronger crack, better icon placement
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import numpy as np
import random

random.seed(42)
rng = np.random.default_rng(7)

W, H = 1456, 816
SAFE_X1, SAFE_Y1, SAFE_X2, SAFE_Y2 = 182, 102, 1274, 714

# ============================================================
# STEP 1: BACKGROUND - Deep dark navy gradient
# ============================================================
bg_arr = np.zeros((H, W, 4), dtype=np.uint8)
for y in range(H):
    t = y / H
    r = int(5 + 8 * t)
    g = int(7 + 10 * t)
    b = int(22 + 18 * t)
    bg_arr[y, :, 0] = r
    bg_arr[y, :, 1] = g
    bg_arr[y, :, 2] = b
    bg_arr[y, :, 3] = 255
img = Image.fromarray(bg_arr, "RGBA")

# ============================================================
# STEP 2: LEFT BLUE AMBIENT GLOW
# ============================================================
glow_left = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_left)
cx, cy = 340, H // 2
for r in range(280, 0, -4):
    a = int(22 * (1 - r / 280))
    gd.ellipse([cx - r, cy - int(r * 0.75), cx + r, cy + int(r * 0.75)],
               fill=(42, 147, 193, a))
img = Image.alpha_composite(img, glow_left)

# ============================================================
# STEP 3: THE CRACK - Center vertical fracture with orange energy
# ============================================================
crack_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cd = ImageDraw.Draw(crack_layer)

cx_crack = W // 2  # 728

# Crack path points (jagged lightning-like)
crack_pts = [
    (cx_crack + 3,   0),
    (cx_crack - 10, H // 8),
    (cx_crack + 15, H // 4),
    (cx_crack - 5,  H * 3 // 8),
    (cx_crack + 8,  H // 2),
    (cx_crack - 12, H * 5 // 8),
    (cx_crack + 6,  H * 3 // 4),
    (cx_crack - 8,  H * 7 // 8),
    (cx_crack + 4,  H),
]

# Wide outer glow (multiple passes)
for spread in [140, 110, 85, 65, 45, 30, 18, 10, 5, 2]:
    alpha = int(55 * (1 - spread / 140))
    color = (241, 66, 11, alpha)
    offset_pts_l = [(x - spread // 2, y) for x, y in crack_pts]
    offset_pts_r = [(x + spread // 2, y) for x, y in crack_pts]
    if len(offset_pts_l) > 1:
        cd.line(offset_pts_l, fill=color, width=max(1, spread // 2))
        cd.line(offset_pts_r, fill=color, width=max(1, spread // 2))

# Core bright crack
cd.line(crack_pts, fill=(255, 180, 80, 255), width=3)

# Secondary crack branches
branches = [
    (cx_crack - 5, H // 4, -60, -20),
    (cx_crack + 15, H // 4, 50, -15),
    (cx_crack + 8, H // 2, -45, 25),
    (cx_crack - 12, H * 5 // 8, 70, 20),
]
for bx, by, bex, bey in branches:
    cd.line([(bx, by), (bx + bex, by + bey)], fill=(255, 140, 50, 120), width=1)

img = Image.alpha_composite(img, crack_layer)

# Blur the crack glow for extra softness, then composite sharp crack on top
crack_blurred = crack_layer.filter(ImageFilter.GaussianBlur(radius=12))
img = Image.alpha_composite(img, crack_blurred)
img = Image.alpha_composite(img, crack_layer)  # sharp on top

draw = ImageDraw.Draw(img)

# Orange embers / sparks
for _ in range(50):
    sx = cx_crack + random.randint(-20, 20)
    sy = random.randint(H // 5, H * 4 // 5)
    ex = sx + random.randint(-100, 100)
    ey = sy + random.randint(-40, 40)
    a = random.randint(40, 120)
    draw.line([(sx, sy), (ex, ey)], fill=(241, 80, 11, a), width=1)

for _ in range(35):
    px = cx_crack + random.randint(-80, 80)
    py = random.randint(80, H - 80)
    r = random.randint(1, 4)
    a = random.randint(100, 220)
    draw.ellipse([(px - r, py - r), (px + r, py + r)], fill=(255, 100, 20, a))

# ============================================================
# STEP 4: LEFT ICONS (simple task icons in blue)
# ============================================================
font_sm = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 16)
left_cx = 300

# --- ENVELOPE ---
ex, ey, ew, eh = left_cx - 55, H * 2 // 3 - 40, 110, 78
draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=8,
                        fill=(12, 35, 68, 220), outline=(42, 147, 193, 220), width=2)
draw.line([ex, ey, ex + ew // 2, ey + eh // 2 - 5], fill=(42, 147, 193, 180), width=2)
draw.line([ex + ew, ey, ex + ew // 2, ey + eh // 2 - 5], fill=(42, 147, 193, 180), width=2)
# @ symbol inside
font_icon = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 20)
draw.text((ex + ew // 2, ey + eh // 2 + 8), "@", fill=(42, 147, 193, 160), font=font_icon, anchor="mm")

# Blue glow around envelope
glow_env = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ge = ImageDraw.Draw(glow_env)
for r in range(80, 0, -5):
    a = int(15 * (1 - r / 80))
    ge.ellipse([ex + ew // 2 - r, ey + eh // 2 - r, ex + ew // 2 + r, ey + eh // 2 + r],
               fill=(42, 147, 193, a))
img = Image.alpha_composite(img, glow_env)
draw = ImageDraw.Draw(img)

# --- DOCUMENT ---
dx, dy, dw, dh = left_cx - 75, H * 2 // 3 + 50, 80, 100
draw.rounded_rectangle([dx, dy, dx + dw, dy + dh], radius=5,
                        fill=(10, 30, 60, 220), outline=(42, 147, 193, 200), width=2)
# Folded corner
draw.polygon([(dx + dw - 18, dy), (dx + dw, dy + 18), (dx + dw - 18, dy + 18)],
             fill=(42, 147, 193, 140))
for i in range(4):
    lx1 = dx + 10
    lx2 = dx + dw - 10
    ly = dy + 25 + i * 17
    draw.line([(lx1, ly), (lx2, ly)], fill=(42, 147, 193, 120), width=2)

# --- CHAT BUBBLE ---
bx, by, bw, bh = left_cx + 15, H * 2 // 3 - 70, 90, 55
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10,
                        fill=(10, 35, 70, 220), outline=(42, 147, 193, 200), width=2)
draw.polygon([(bx + 14, by + bh), (bx + 4, by + bh + 14), (bx + 32, by + bh)],
             fill=(10, 35, 70, 220))
for i in range(3):
    dot_x = bx + 20 + i * 25
    dot_y = by + bh // 2
    draw.ellipse([(dot_x - 5, dot_y - 5), (dot_x + 5, dot_y + 5)], fill=(42, 147, 193, 200))

# Left zone label
draw.text((left_cx, H * 2 // 3 + 165), "SIMPLE TASKS", fill=(42, 147, 193, 160), font=font_sm, anchor="mm")

# ============================================================
# STEP 5: RIGHT ICONS (strategic/complex - in shadow/dim)
# ============================================================
right_cx = 1130

# Chess king (geometric)
kx, ky = right_cx - 25, H * 2 // 3 - 130

# King base
draw.rounded_rectangle([kx - 38, ky + 140, kx + 38, ky + 175], radius=4,
                        fill=(18, 14, 24, 200), outline=(200, 120, 60, 150), width=2)
# King body (trapezoid)
draw.polygon([(kx - 30, ky + 140), (kx + 30, ky + 140), (kx + 22, ky + 80), (kx - 22, ky + 80)],
             fill=(15, 12, 22, 200), outline=(180, 100, 50, 130))
# King head/neck
draw.rectangle([kx - 12, ky + 60, kx + 12, ky + 80],
               fill=(15, 12, 22, 200), outline=(180, 100, 50, 120))
draw.ellipse([kx - 18, ky + 35, kx + 18, ky + 65],
             fill=(15, 12, 22, 200), outline=(180, 100, 50, 120))
# Cross
draw.rectangle([kx - 5, ky, kx + 5, ky + 40], fill=(80, 50, 25, 200), outline=(200, 130, 70, 150))
draw.rectangle([kx - 18, ky + 12, kx + 18, ky + 24], fill=(80, 50, 25, 200), outline=(200, 130, 70, 150))

# Shadow vignette right side
shadow_r = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sr = ImageDraw.Draw(shadow_r)
for r in range(200, 0, -8):
    a = int(30 * (1 - r / 200))
    sr.ellipse([right_cx - r, H // 2 - int(r * 0.8), right_cx + r, H // 2 + int(r * 0.8)],
               fill=(0, 0, 0, a))
img = Image.alpha_composite(img, shadow_r)
draw = ImageDraw.Draw(img)

# Question marks (uncertainty over right side)
font_q = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 32)
q_positions = [(right_cx - 55, ky - 18, 70), (right_cx + 5, ky - 36, 90), (right_cx + 55, ky - 14, 65)]
for qx, qy, qa in q_positions:
    draw.text((qx, qy), "?", fill=(200, 110, 50, qa), font=font_q, anchor="mm")

draw.text((right_cx, H * 2 // 3 + 80), "STRATEGIC DECISIONS", fill=(170, 100, 50, 150), font=font_sm, anchor="mm")

# ============================================================
# STEP 6: DASHED SPECTRUM LINES (trust spectrum)
# ============================================================
spec_y = H * 2 // 3 + 10
for xi in range(SAFE_X1 + 10, cx_crack - 40, 16):
    draw.line([(xi, spec_y), (xi + 9, spec_y)], fill=(42, 147, 193, 40), width=1)
for xi in range(cx_crack + 40, SAFE_X2 - 10, 16):
    draw.line([(xi, spec_y), (xi + 9, spec_y)], fill=(170, 80, 40, 40), width=1)

# ============================================================
# STEP 7: TITLE TEXT
# ============================================================
font_huge = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 88)
font_large = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 88)
font_sub = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 36)
font_tag = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 20)

# Text area: TOP of canvas, big and bold
text_cx = W // 2
title_y = 155

# "THE AI" - white
draw.text((text_cx, title_y), "THE AI", fill=(240, 240, 255, 255), font=font_huge, anchor="mm")

# "TRUST GAP" below - TRUST=blue, GAP=orange
trust_y = title_y + 92
trust_w = font_large.getbbox("TRUST ")[2] - font_large.getbbox("TRUST ")[0]
gap_w = font_large.getbbox("GAP")[2] - font_large.getbbox("GAP")[0]
total = trust_w + gap_w
start = text_cx - total // 2

# Text shadows for depth
draw.text((start + 2, trust_y + 2), "TRUST ", fill=(20, 80, 130, 120), font=font_large, anchor="lm")
draw.text((start + trust_w + 2, trust_y + 2), "GAP", fill=(160, 30, 5, 120), font=font_large, anchor="lm")
draw.text((start, trust_y), "TRUST ", fill=(42, 147, 193, 255), font=font_large, anchor="lm")
draw.text((start + trust_w, trust_y), "GAP", fill=(241, 66, 11, 255), font=font_large, anchor="lm")

# Subtitle
sub_y = trust_y + 60
draw.text((text_cx, sub_y), "Is the Real Problem  —  Not the Technology",
          fill=(190, 195, 210, 220), font=font_sub, anchor="mm")

# Accent divider
div_y = sub_y + 46
draw.line([(text_cx - 220, div_y), (text_cx - 10, div_y)], fill=(42, 147, 193, 120), width=1)
draw.ellipse([(text_cx - 6, div_y - 3), (text_cx + 6, div_y + 3)], fill=(241, 66, 11, 180))
draw.line([(text_cx + 10, div_y), (text_cx + 220, div_y)], fill=(42, 147, 193, 120), width=1)

# ============================================================
# STEP 8: PUREBRAIN ICON + BRAND - bottom right safe zone
# ============================================================
icon_raw = Image.open("/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png").convert("RGBA")
icon_size = 68
icon_img = icon_raw.resize((icon_size, icon_size), Image.LANCZOS)
icon_x = SAFE_X2 - icon_size - 8
icon_y = SAFE_Y2 - icon_size - 8
img.alpha_composite(icon_img, (icon_x, icon_y))

draw = ImageDraw.Draw(img)
font_brand = ImageFont.truetype("/home/jared/.fonts/Oswald-Bold.ttf", 17)
brand_y = icon_y + icon_size // 2
# PUREBR (blue) + AI (orange) + N (blue)
brand_parts = [
    ("PUREBR", (42, 147, 193, 210)),
    ("AI", (241, 66, 11, 210)),
    ("N", (42, 147, 193, 210)),
    (".AI", (180, 185, 200, 170)),
]
total_bw = sum(font_brand.getbbox(t)[2] - font_brand.getbbox(t)[0] for t, _ in brand_parts)
bx = icon_x - 6 - total_bw
for text, color in brand_parts:
    draw.text((bx, brand_y), text, fill=color, font=font_brand, anchor="lm")
    bw = font_brand.getbbox(text)[2] - font_brand.getbbox(text)[0]
    bx += bw

# ============================================================
# STEP 9: PREMIUM NOISE TEXTURE
# ============================================================
noise_arr = np.zeros((H, W, 4), dtype=np.uint8)
noise_vals = rng.integers(0, 12, (H, W)).astype(np.uint8)
noise_arr[:, :, 3] = noise_vals
noise_arr[:, :, 0] = noise_vals
noise_arr[:, :, 1] = noise_vals
noise_arr[:, :, 2] = noise_vals
noise_layer = Image.fromarray(noise_arr, "RGBA")
img = Image.alpha_composite(img, noise_layer)

# ============================================================
# STEP 10: VIGNETTE (darken corners)
# ============================================================
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vignette)
for step in range(1, 60):
    margin = step * 5
    alpha = int(step * 1.5)
    vd.rectangle([margin, margin, W - margin, H - margin], outline=(0, 0, 0, alpha), width=6)
img = Image.alpha_composite(img, vignette)

# ============================================================
# SAVE
# ============================================================
output_path = "/home/jared/projects/AI-CIV/aether/exports/trust-gap-blog-banner.png"
final = img.convert("RGB")
final.save(output_path, "PNG")
print(f"Banner saved: {output_path}")

from PIL import Image as PILVerify
v = PILVerify.open(output_path)
print(f"Verified: {v.size} {v.mode}")

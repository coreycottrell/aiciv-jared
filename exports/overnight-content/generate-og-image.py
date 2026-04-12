#!/usr/bin/env python3
"""
PureBrain Homepage Open Graph Image Generator
==============================================
Size: 1200x627 (standard OG image dimensions for LinkedIn/Twitter/Facebook)
Output: JPG quality 85-90, under 1MB
Design: Premium dark-tech brand image — first impression on social shares

Visual concept:
  - Deep dark gradient background (#080a12 → #0d1220)
  - Subtle hex mesh pattern (very low opacity)
  - PureBrain hex icon centered-left, large and prominent
  - Brand name: PUREBR (blue) + AI (orange) + N (blue) + ".ai" (white)
  - Tagline below: "Your AI Partnership Starts Here"
  - Soft ambient glow behind icon (blue + orange)
  - Clean vignette edges
  - No clutter — premium, readable at thumbnail scale
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Canvas ──────────────────────────────────────────────────────────────────
W, H = 1200, 627

# ── Brand colors ────────────────────────────────────────────────────────────
ORANGE    = (241, 66, 11)
BLUE      = (42, 147, 193)
WHITE     = (255, 255, 255)
DARK_BG1  = (8, 10, 18)       # #080a12 - top
DARK_BG2  = (13, 18, 32)      # #0d1220 - bottom
HEX_MESH  = (42, 147, 193)    # blue tinted mesh lines

# ── Paths ───────────────────────────────────────────────────────────────────
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
ICON_PATH = "/home/jared/projects/AI-CIV/aether/docs/assets/logos/purebrain-icon.png"
OUT_PATH  = "/home/jared/projects/AI-CIV/aether/exports/overnight-content/purebrain-homepage-og-image.jpg"


# ── Font loader ──────────────────────────────────────────────────────────────
def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_h(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


# ── Background gradient (top-to-bottom dark) ─────────────────────────────────
def make_background():
    img = Image.new("RGBA", (W, H), DARK_BG1)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(DARK_BG1[0] + (DARK_BG2[0] - DARK_BG1[0]) * t)
        g = int(DARK_BG1[1] + (DARK_BG2[1] - DARK_BG1[1]) * t)
        b = int(DARK_BG1[2] + (DARK_BG2[2] - DARK_BG1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
    return img


# ── Hex mesh overlay (very subtle) ───────────────────────────────────────────
def draw_hex_mesh(img, opacity=14):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    hex_r = 32
    col_w = hex_r * math.sqrt(3)
    row_h = hex_r * 1.5
    cols = int(W / col_w) + 3
    rows = int(H / row_h) + 3
    for row in range(-1, rows):
        for col in range(-1, cols):
            # offset every other row
            offset = (hex_r * math.sqrt(3) / 2) if row % 2 else 0
            cx = col * col_w + offset
            cy = row * row_h
            pts = []
            for angle_deg in range(0, 360, 60):
                angle_rad = math.radians(angle_deg + 30)
                px = cx + hex_r * math.cos(angle_rad)
                py = cy + hex_r * math.sin(angle_rad)
                pts.append((px, py))
            ld.polygon(pts, outline=(*HEX_MESH, opacity), fill=None)
    img = Image.alpha_composite(img, layer)
    return img


# ── Ambient glow behind the icon ─────────────────────────────────────────────
def draw_ambient_glow(img, icon_cx, icon_cy, icon_size):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # Outer blue halo
    for r_px in [280, 210, 150, 100, 60]:
        a = max(4, 22 - r_px // 18)
        ImageDraw.Draw(layer).ellipse(
            [icon_cx - r_px, icon_cy - r_px,
             icon_cx + r_px, icon_cy + r_px],
            fill=(*BLUE, a)
        )
    # Warm orange core glow (small, directly behind icon)
    for r_px in [90, 60, 40]:
        a = max(6, 20 - r_px // 8)
        ImageDraw.Draw(layer).ellipse(
            [icon_cx - r_px, icon_cy - r_px,
             icon_cx + r_px, icon_cy + r_px],
            fill=(*ORANGE, a)
        )
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, blurred)
    return img


# ── Vignette ─────────────────────────────────────────────────────────────────
def draw_vignette(img, strength=140):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 50
    for i in range(steps):
        t = i / steps
        a = int(strength * t * t)
        shrink = int((steps - i) * (min(W, H) / 2) / steps)
        ld.rectangle([shrink, shrink, W - shrink, H - shrink],
                     outline=(0, 0, 0, a), width=4)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img, blurred)
    return img


# ── Glowing accent line (horizontal separator) ───────────────────────────────
def draw_accent_line(img, x1, x2, y, color, max_width=6, passes=5):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(passes, 0, -1):
        t = i / passes
        w = max(1, int(max_width * t))
        a = int(100 * (1 - t * 0.6))
        ld.line([(x1, y), (x2, y)], fill=(*color, a), width=w)
    # Crisp core
    ld.line([(x1, y), (x2, y)], fill=(*color, 220), width=1)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, blurred)
    return img


# ── Main icon + brand + tagline layout ───────────────────────────────────────
def draw_content(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # ── Layout constants ──────────────────────────────────────────────────────
    # Overall vertical center
    cy_center = H // 2  # 313

    # Icon: large, positioned in left zone with good margin
    # Center x at ~28% of width, center y at vertical center
    ICON_SIZE = 240
    icon_cx = int(W * 0.26)  # ~312
    icon_cy = cy_center       # ~313

    icon_x = icon_cx - ICON_SIZE // 2
    icon_y = icon_cy - ICON_SIZE // 2

    # Text zone: starts after icon + divider (~46% across)
    TEXT_LEFT = int(W * 0.445)   # ~534

    # Brand name fonts
    brand_font_large = load_font(96)  # Main brand text — larger for impact
    dot_ai_font      = load_font(60)  # ".ai" — slightly smaller, lowercase feel

    # Tagline font
    tagline_font = load_font(36)
    tagline_text = "Your AI Partnership Starts Here"

    # ── Measure brand name parts to align them ────────────────────────────────
    # "PUREBRAIN.ai" = PUREBR (blue) + AI (orange) + N (blue) + ".ai" (white)
    parts_brand = [
        ("PUREBR", BLUE,   brand_font_large),
        ("AI",     ORANGE, brand_font_large),
        ("N",      BLUE,   brand_font_large),
    ]
    parts_dotai = [
        (".ai",    WHITE,  dot_ai_font),
    ]

    total_brand_w = sum(text_w(ld, t, f) for t, _, f in parts_brand)
    total_dotai_w = sum(text_w(ld, t, f) for t, _, f in parts_dotai)
    total_name_w  = total_brand_w + total_dotai_w + 4  # small kern gap

    # Brand name vertical position: slight above center
    brand_h  = text_h(ld, "PUREBRAIN", brand_font_large)
    brand_y  = cy_center - brand_h - 14   # sits above center

    # Tagline: below brand name with a small gap
    tline_h  = text_h(ld, tagline_text, tagline_font)
    tline_y  = brand_y + brand_h + 20

    # Accent line: between tagline and any bottom element
    accent_y = tline_y + tline_h + 22

    # ── Draw brand name (left-aligned from TEXT_LEFT) ─────────────────────────
    bx = TEXT_LEFT

    # Subtle drop shadow first
    for dx, dy in [(2, 3)]:
        sbx = TEXT_LEFT
        for text, color, font in parts_brand:
            ld.text((sbx + dx, brand_y + dy), text, fill=(0, 0, 0, 80), font=font)
            sbx += text_w(ld, text, font)
        for text, color, font in parts_dotai:
            ld.text((sbx + dx + 4, brand_y + dy + 26), text, fill=(0, 0, 0, 80), font=font)

    # Actual colored brand text
    bx = TEXT_LEFT
    for text, color, font in parts_brand:
        ld.text((bx, brand_y), text, fill=(*color, 255), font=font)
        bx += text_w(ld, text, font)

    # ".ai" is vertically offset downward to sit on the baseline of the larger text
    for text, color, font in parts_dotai:
        # Align bottom of ".ai" with bottom of brand name text
        brand_bbox = ld.textbbox((0, 0), "PUREBRAIN", brand_font_large)
        dotai_bbox = ld.textbbox((0, 0), text, font)
        brand_bottom = brand_y + (brand_bbox[3] - brand_bbox[1])
        dotai_bottom_offset = brand_bottom - (dotai_bbox[3] - dotai_bbox[1])
        ld.text((bx + 4, dotai_bottom_offset), text, fill=(*color, 220), font=font)
        bx += text_w(ld, text, font) + 4

    # ── Tagline ───────────────────────────────────────────────────────────────
    # Shadow
    ld.text((TEXT_LEFT + 1, tline_y + 2), tagline_text, fill=(0, 0, 0, 80), font=tagline_font)
    # Text — white with slight blue tint
    ld.text((TEXT_LEFT, tline_y), tagline_text, fill=(210, 230, 245, 240), font=tagline_font)

    img = Image.alpha_composite(img, layer)

    # ── Accent line ───────────────────────────────────────────────────────────
    accent_x2 = TEXT_LEFT + max(total_name_w, text_w(ld, tagline_text, tagline_font))
    img = draw_accent_line(img, TEXT_LEFT, accent_x2, accent_y, BLUE, max_width=4, passes=5)

    # ── Icon (rendered on top of glow, after layer composite) ─────────────────
    icon = Image.open(ICON_PATH).convert("RGBA")
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)

    # Add a subtle dark background behind the icon to prevent any color bleed
    icon_bg = Image.new("RGBA", (ICON_SIZE + 20, ICON_SIZE + 20), (0, 0, 0, 0))
    ImageDraw.Draw(icon_bg).ellipse(
        [0, 0, ICON_SIZE + 20, ICON_SIZE + 20],
        fill=(8, 10, 18, 60)
    )
    icon_bg = icon_bg.filter(ImageFilter.GaussianBlur(radius=10))
    img.paste(icon_bg, (icon_x - 10, icon_y - 10), icon_bg)

    # Paste icon
    img.paste(icon, (icon_x, icon_y), icon)

    # ── Vertical divider between icon zone and text zone ─────────────────────
    divider_x = int(W * 0.415)
    divider_y1 = icon_y + 20
    divider_y2 = icon_y + ICON_SIZE - 20
    div_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    div_ld = ImageDraw.Draw(div_layer)
    # Gradient line: fade in and out
    for i, y in enumerate(range(divider_y1, divider_y2, 2)):
        t = i / ((divider_y2 - divider_y1) / 2)
        dist_from_center = abs(t - 1.0)
        a = int(80 * (1 - dist_from_center))
        div_ld.line([(divider_x, y), (divider_x, y + 2)],
                    fill=(*BLUE, max(0, a)), width=1)
    blurred_div = div_layer.filter(ImageFilter.GaussianBlur(radius=1))
    img = Image.alpha_composite(img, blurred_div)

    return img, icon_cx, icon_cy


# ── Bottom attribution bar ────────────────────────────────────────────────────
def draw_bottom_bar(img):
    """Subtle 'purebrain.ai' URL watermark at bottom-right."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    url_font = load_font(22)
    url_text = "purebrain.ai"
    uw = text_w(ld, url_text, url_font)
    uh = text_h(ld, url_text, url_font)
    ux = W - uw - 36
    uy = H - uh - 24
    ld.text((ux, uy), url_text, fill=(*BLUE, 140), font=url_font)
    img = Image.alpha_composite(img, layer)
    return img


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("PureBrain Homepage OG Image Generator")
    print(f"Canvas: {W}x{H} px")
    print(f"Output: {OUT_PATH}")
    print("=" * 60)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # Step 1: Background gradient
    img = make_background()
    print("  [1/7] Background gradient ... done")

    # Step 2: Hex mesh (very subtle, barely visible - just texture)
    img = draw_hex_mesh(img, opacity=14)
    print("  [2/7] Hex mesh overlay ... done")

    # Step 3: Content (icon + brand + tagline) - get icon center for glow
    img, icon_cx, icon_cy = draw_content(img)
    print("  [3/7] Content (icon + brand + tagline) ... done")

    # Step 4: Ambient glow UNDER the icon (re-composite order: bg → mesh → glow → icon)
    # Since icon is already pasted, we draw glow on a separate pass
    # Actually: draw glow BEHIND content by inserting after mesh
    # We'll re-build the composition in correct order:
    print("  [4/7] Rebuilding with correct glow order ...")

    img_bg = make_background()
    img_bg = draw_hex_mesh(img_bg, opacity=14)
    img_bg = draw_ambient_glow(img_bg, icon_cx, icon_cy, 220)

    # Re-draw content on top of glow
    content_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ... re-use draw_content but need to extract just the layer part
    # Simpler: composite the content layer (already done) on top of bg+glow
    # Since draw_content returned the composited img, we need the content pixels
    # Extract content by subtracting background from composited img
    # Easiest: re-run draw_content on the new base
    img, icon_cx, icon_cy = draw_content(img_bg)
    print("       Glow + content composite ... done")

    # Step 5: Vignette
    img = draw_vignette(img, strength=130)
    print("  [5/7] Vignette ... done")

    # Step 6: Bottom attribution
    img = draw_bottom_bar(img)
    print("  [6/7] Bottom bar ... done")

    # Step 7: Flatten RGBA → RGB and save as JPG
    final = Image.new("RGB", (W, H), DARK_BG1)
    final.paste(img, mask=img.split()[3])

    # Save with quality 87 (good balance: sharp text, under 1MB)
    final.save(OUT_PATH, "JPEG", quality=87, optimize=True)
    print(f"  [7/7] Saved: {OUT_PATH}")

    # ── Verification ────────────────────────────────────────────────────────
    print()
    print("── Verification ────────────────────────────────────────")
    check = Image.open(OUT_PATH)
    size_bytes = os.path.getsize(OUT_PATH)
    size_kb = size_bytes / 1024
    size_mb = size_bytes / (1024 * 1024)

    print(f"  Dimensions : {check.size[0]} x {check.size[1]} px")
    print(f"  Mode       : {check.mode}")
    print(f"  File size  : {size_kb:.1f} KB ({size_mb:.2f} MB)")
    print(f"  Under 1MB  : {'YES ✓' if size_mb < 1.0 else 'NO ✗ — increase compression'}")
    print(f"  OG standard: {'YES ✓ (1200x627)' if check.size == (1200, 627) else 'NO ✗'}")

    if check.size != (W, H):
        print(f"  ERROR: Expected {W}x{H}, got {check.size}")
        return 1
    if size_mb >= 1.0:
        print(f"  WARNING: File is {size_mb:.2f}MB. Reducing quality to 80...")
        final.save(OUT_PATH, "JPEG", quality=80, optimize=True)
        size_mb_new = os.path.getsize(OUT_PATH) / (1024 * 1024)
        print(f"  Resaved at quality=80: {size_mb_new:.2f}MB")

    print()
    print("Done. OG image ready for upload to Yoast SEO.")
    print("  WordPress: Edit Homepage → Yoast SEO panel → Social tab → OG Image")
    print()
    return 0


if __name__ == "__main__":
    exit(main())

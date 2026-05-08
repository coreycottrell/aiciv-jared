#!/usr/bin/env python3
"""Generate v4.1 standalone banners (1080x1350) with centered title on FLUX image."""

from PIL import Image, ImageDraw, ImageFont
import os

# Paths
BASE = "/home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix"
FLUX_DIR = os.path.join(BASE, "flux-raw")
OUT_DIR = os.path.join(BASE, "final-v3")
HEX_ICON = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"

# Dimensions
W, H = 1080, 1350
TOP_BAR_H = 140
BOT_BAR_H = 90
ACCENT_H = 2

# Colors
BG_COLOR = (8, 10, 18)       # #080a12
BLUE = (42, 147, 193)        # #2a93c1
ORANGE = (241, 66, 11)       # #f1420b
WHITE = (255, 255, 255)
BACKDROP_COLOR = (8, 10, 18, 153)  # rgba(8,10,18,0.6)

# Post mapping: (flux_raw, post_ids, title, cta)
POSTS = [
    ("companies-winning-flux-raw.png", ["bfc6759b", "769d35b2", "b7eb2210", "2e9146e7"],
     "The Companies\nWinning With AI", "Read the Full Breakdown"),
    ("implementations-fail-flux-raw.png", ["71436ff4", "9a3e40f6", "9e3ca912"],
     "Why AI\nImplementations Fail", "Avoid the Top Mistakes"),
    ("ceo-questions-flux-raw.png", ["aee4e9a3", "7d44dc85", "18e9c0bc"],
     "Three Questions\nEvery CEO\nShould Ask", "Get the Answers"),
    ("agent-market-flux-raw.png", ["735b7474"],
     "$52.6 Billion\nAI Agent Market", "See the Opportunity"),
]


def draw_brand_text(draw, x, y, font):
    """Draw PUREBRAIN.AI with proper brand colors."""
    parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    cx = x
    for text, color in parts:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((cx, y), text, fill=color, font=font)
        cx += tw


def get_brand_width(draw, font):
    """Get total width of PUREBRAIN.AI text."""
    total = 0
    for text in ["PUREBR", "AI", "N", ".AI"]:
        bbox = draw.textbbox((0, 0), text, font=font)
        total += bbox[2] - bbox[0]
    return total


def create_banner(flux_path, title, cta, post_id):
    """Create a single v4.1 banner."""
    canvas = Image.new("RGBA", (W, H), BG_COLOR + (255,))
    draw = ImageDraw.Draw(canvas)

    # Load fonts
    font_brand_top = ImageFont.truetype(FONT_PATH, 20)
    font_brand_bot = ImageFont.truetype(FONT_PATH, 26)
    font_cta = ImageFont.truetype(FONT_PATH, 22)

    # --- TOP BAR ---
    draw.rectangle([0, 0, W, TOP_BAR_H], fill=BG_COLOR)

    # Hex icon
    hex_icon = Image.open(HEX_ICON).convert("RGBA")
    hex_icon = hex_icon.resize((50, 50), Image.LANCZOS)
    icon_x, icon_y = 30, (TOP_BAR_H - 50) // 2
    canvas.paste(hex_icon, (icon_x, icon_y), hex_icon)

    # Brand text in top bar
    brand_x = icon_x + 50 + 12
    brand_bbox = draw.textbbox((0, 0), "PUREBRAIN.AI", font=font_brand_top)
    brand_text_h = brand_bbox[3] - brand_bbox[1]
    brand_y = (TOP_BAR_H - brand_text_h) // 2 - 2
    draw_brand_text(draw, brand_x, brand_y, font_brand_top)

    # Blue accent line at bottom of top bar
    draw.rectangle([0, TOP_BAR_H - ACCENT_H, W, TOP_BAR_H], fill=BLUE)

    # --- FLUX IMAGE AREA ---
    img_area_top = TOP_BAR_H
    img_area_bot = H - BOT_BAR_H
    img_area_h = img_area_bot - img_area_top

    flux = Image.open(flux_path).convert("RGBA")
    # Resize to fill width, crop to height
    scale = W / flux.width
    new_h = int(flux.height * scale)
    flux = flux.resize((W, new_h), Image.LANCZOS)
    # Center crop vertically
    if new_h > img_area_h:
        top_crop = (new_h - img_area_h) // 2
        flux = flux.crop((0, top_crop, W, top_crop + img_area_h))
    else:
        # If image is shorter, scale by height instead
        scale = img_area_h / flux.height
        flux = flux.resize((int(flux.width * scale), img_area_h), Image.LANCZOS)
        if flux.width > W:
            left_crop = (flux.width - W) // 2
            flux = flux.crop((left_crop, 0, left_crop + W, img_area_h))

    canvas.paste(flux, (0, img_area_top))

    # --- TITLE OVERLAY (centered on image area with dark backdrop) ---
    # Determine font size (start at 68, shrink if needed)
    lines = title.split("\n")
    font_size = 68
    while font_size >= 36:
        font_title = ImageFont.truetype(FONT_PATH, font_size)
        # Measure all lines
        line_widths = []
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])

        max_w = max(line_widths)
        line_spacing = 12
        total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)

        # Check if it fits with padding
        pad_x, pad_y = 40, 30
        backdrop_w = max_w + pad_x * 2
        backdrop_h = total_text_h + pad_y * 2

        if backdrop_w <= W - 60 and backdrop_h <= img_area_h - 40:
            break
        font_size -= 4

    # Draw backdrop
    backdrop_x = (W - backdrop_w) // 2
    backdrop_y = img_area_top + (img_area_h - backdrop_h) // 2

    # Create backdrop with rounded corners
    backdrop = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(backdrop)
    bd.rounded_rectangle(
        [backdrop_x, backdrop_y, backdrop_x + backdrop_w, backdrop_y + backdrop_h],
        radius=12,
        fill=BACKDROP_COLOR
    )
    canvas = Image.alpha_composite(canvas, backdrop)
    draw = ImageDraw.Draw(canvas)

    # Draw title text centered
    current_y = backdrop_y + pad_y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        lx = (W - lw) // 2

        # Shadow for extra readability
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                if ox == 0 and oy == 0:
                    continue
                draw.text((lx + ox, current_y + oy), line, fill=(0, 0, 0, 180), font=font_title)

        draw.text((lx, current_y), line, fill=WHITE, font=font_title)
        current_y += lh + line_spacing

    # --- BOTTOM BAR ---
    draw.rectangle([0, H - BOT_BAR_H, W, H], fill=BG_COLOR)
    # Blue accent line at top of bottom bar
    draw.rectangle([0, H - BOT_BAR_H, W, H - BOT_BAR_H + ACCENT_H], fill=BLUE)

    # Brand text left
    brand_bot_bbox = draw.textbbox((0, 0), "PUREBRAIN.AI", font=font_brand_bot)
    brand_bot_h = brand_bot_bbox[3] - brand_bot_bbox[1]
    brand_bot_y = H - BOT_BAR_H + ACCENT_H + (BOT_BAR_H - ACCENT_H - brand_bot_h) // 2 - 2
    draw_brand_text(draw, 30, brand_bot_y, font_brand_bot)

    # CTA text right (orange)
    cta_bbox = draw.textbbox((0, 0), cta, font=font_cta)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    cta_y = H - BOT_BAR_H + ACCENT_H + (BOT_BAR_H - ACCENT_H - cta_h) // 2 - 2
    draw.text((W - 30 - cta_w, cta_y), cta, fill=ORANGE, font=font_cta)

    # Save as JPEG
    out_path = os.path.join(OUT_DIR, f"{post_id}-standalone.jpg")
    rgb = canvas.convert("RGB")
    rgb.save(out_path, "JPEG", quality=95)
    print(f"  Saved: {out_path}")
    return out_path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    generated = []
    for flux_file, post_ids, title, cta in POSTS:
        flux_path = os.path.join(FLUX_DIR, flux_file)
        if not os.path.exists(flux_path):
            print(f"  SKIP: {flux_file} not found")
            continue

        print(f"\n--- {flux_file} ---")
        print(f"  Title: {title.replace(chr(10), ' | ')}")
        print(f"  Posts: {post_ids}")

        for pid in post_ids:
            path = create_banner(flux_path, title, cta, pid)
            generated.append(path)

    print(f"\n=== Generated {len(generated)} banners ===")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()

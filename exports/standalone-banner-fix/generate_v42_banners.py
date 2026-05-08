#!/usr/bin/env python3
"""Generate v4.2 standalone banners (1080x1350) per Jared-approved layout."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Paths
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"
FLUX_DIR = "/home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix/flux-raw/"
OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/standalone-banner-fix/final-v4/"

# Brand colors
BLUE = "#2a93c1"
ORANGE = "#f1420b"
DARK_BG = "#080a12"
WHITE = "#ffffff"

# Canvas
WIDTH, HEIGHT = 1080, 1350
TOP_BAR_H = 140
BOTTOM_BAR_H = 100
ACCENT_LINE_W = 2

# Font sizes
WORDMARK_SIZE = 46
TITLE_SIZE = 62
BOTTOM_LEFT_SIZE = 26
BOTTOM_RIGHT_SIZE = 22
ICON_SIZE = 80

# Banner specs: (flux_file, title, treatment, [(post_id, ...)])
BANNERS = [
    ("companies-winning-flux-raw.png", "THE COMPANIES WINNING WITH AI", "stroke",
     ["bfc6759b", "769d35b2", "b7eb2210", "2e9146e7"]),
    ("implementations-fail-flux-raw.png", "WHY AI IMPLEMENTATIONS FAIL", "shadow",
     ["71436ff4", "9a3e40f6", "9e3ca912"]),
    ("ceo-questions-flux-raw.png", "THREE QUESTIONS EVERY CEO SHOULD ASK", "stroke",
     ["aee4e9a3", "7d44dc85", "18e9c0bc"]),
    ("agent-market-flux-raw.png", "$52.6 BILLION AI AGENT MARKET", "shadow",
     ["735b7474"]),
]


def draw_wordmark(draw, x, y, font):
    """Draw PUREBRAIN.AI with brand colors at position (x, y)."""
    parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", WHITE),
    ]
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        bbox = font.getbbox(text)
        cx += bbox[2] - bbox[0]


def get_wordmark_width(font):
    """Calculate total wordmark width."""
    total = 0
    for text in ["PUREBR", "AI", "N", ".AI"]:
        bbox = font.getbbox(text)
        total += bbox[2] - bbox[0]
    return total


def generate_banner(flux_file, title, treatment, post_ids):
    """Generate a single v4.2 banner."""
    # Load fonts
    font_wordmark = ImageFont.truetype(FONT_PATH, WORDMARK_SIZE)
    font_title = ImageFont.truetype(FONT_PATH, TITLE_SIZE)
    font_bottom_left = ImageFont.truetype(FONT_PATH, BOTTOM_LEFT_SIZE)
    font_bottom_right = ImageFont.truetype(FONT_PATH, BOTTOM_RIGHT_SIZE)

    # Load and resize FLUX image to fill content area
    flux_img = Image.open(os.path.join(FLUX_DIR, flux_file)).convert("RGBA")
    content_h = HEIGHT - TOP_BAR_H - BOTTOM_BAR_H
    # Scale to fill width, crop height
    scale = WIDTH / flux_img.width
    scaled_h = int(flux_img.height * scale)
    flux_img = flux_img.resize((WIDTH, scaled_h), Image.LANCZOS)
    # Center crop vertically
    if scaled_h > content_h:
        top_crop = (scaled_h - content_h) // 2
        flux_img = flux_img.crop((0, top_crop, WIDTH, top_crop + content_h))
    else:
        # Pad if needed (unlikely with 1024x1024 source)
        new_img = Image.new("RGBA", (WIDTH, content_h), DARK_BG)
        new_img.paste(flux_img, (0, (content_h - scaled_h) // 2))
        flux_img = new_img

    # Create canvas
    canvas = Image.new("RGB", (WIDTH, HEIGHT), DARK_BG)

    # Paste FLUX image in content area
    canvas.paste(flux_img.convert("RGB"), (0, TOP_BAR_H))
    draw = ImageDraw.Draw(canvas)

    # --- TOP BAR ---
    # Dark background already set
    bar_center = TOP_BAR_H // 2

    # Load hex icon
    icon = Image.open(HEX_ICON_PATH).convert("RGBA")
    icon = icon.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)

    # Calculate wordmark dimensions using visual glyph bounds
    wm_width = get_wordmark_width(font_wordmark)
    gap = 12  # gap between icon and wordmark
    unit_width = ICON_SIZE + gap + wm_width
    unit_x = (WIDTH - unit_width) // 2

    # Paste icon centered vertically
    icon_y = bar_center - ICON_SIZE // 2
    canvas.paste(icon, (unit_x, icon_y), icon)

    # Wordmark vertical alignment using VISUAL glyph bounds
    wm_x = unit_x + ICON_SIZE + gap
    # Use textbbox to get visual bounds
    test_bbox = font_wordmark.getbbox("PUREBRAIN.AI")
    text_visual_top = test_bbox[1]
    text_visual_height = test_bbox[3] - test_bbox[1]
    wm_y = bar_center - text_visual_top - text_visual_height // 2

    draw_wordmark(draw, wm_x, wm_y, font_wordmark)

    # Blue accent line under top bar
    draw.line([(0, TOP_BAR_H - 1), (WIDTH, TOP_BAR_H - 1)], fill=BLUE, width=ACCENT_LINE_W)

    # --- TITLE (centered on image area) ---
    title_area_top = TOP_BAR_H
    title_area_bottom = HEIGHT - BOTTOM_BAR_H
    title_area_center_y = (title_area_top + title_area_bottom) // 2

    # Word wrap title if needed
    title_bbox = font_title.getbbox(title)
    title_w = title_bbox[2] - title_bbox[0]
    max_title_w = WIDTH - 80  # 40px padding each side

    lines = []
    if title_w > max_title_w:
        words = title.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            tw = font_title.getbbox(test_line)[2] - font_title.getbbox(test_line)[0]
            if tw > max_title_w and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    else:
        lines = [title]

    # Calculate total text block height
    line_heights = []
    for line in lines:
        lb = font_title.getbbox(line)
        line_heights.append(lb[3] - lb[1])
    line_spacing = 10
    total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)
    text_start_y = title_area_center_y - total_text_h // 2

    # Draw title lines
    for i, line in enumerate(lines):
        lb = font_title.getbbox(line)
        lw = lb[2] - lb[0]
        lx = (WIDTH - lw) // 2
        ly = text_start_y + sum(line_heights[:i]) + line_spacing * i - lb[1]

        if treatment == "stroke":
            # 4px dark border stroke
            stroke_w = 4
            for dx in range(-stroke_w, stroke_w + 1):
                for dy in range(-stroke_w, stroke_w + 1):
                    if dx * dx + dy * dy <= stroke_w * stroke_w:
                        draw.text((lx + dx, ly + dy), line, fill="#000000", font=font_title)
            draw.text((lx, ly), line, fill=WHITE, font=font_title)
        elif treatment == "shadow":
            # 4px radius black shadow
            shadow_offset = 4
            # Draw shadow layer
            shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.text((lx + shadow_offset, ly + shadow_offset), line,
                             fill=(0, 0, 0, 200), font=font_title)
            # Blur the shadow
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=4))
            canvas = Image.composite(
                Image.new("RGB", canvas.size, (0, 0, 0)),
                canvas,
                shadow_layer.split()[3]
            )
            # Redraw on composited canvas
            draw = ImageDraw.Draw(canvas)
            draw.text((lx, ly), line, fill=WHITE, font=font_title)

    # --- BOTTOM BAR ---
    bottom_bar_y = HEIGHT - BOTTOM_BAR_H
    draw.rectangle([(0, bottom_bar_y), (WIDTH, HEIGHT)], fill=DARK_BG)

    # Blue accent line above bottom bar
    draw.line([(0, bottom_bar_y), (WIDTH, bottom_bar_y)], fill=BLUE, width=ACCENT_LINE_W)

    # PUREBRAIN.AI left
    bl_text = "PUREBRAIN.AI"
    bl_bbox = font_bottom_left.getbbox(bl_text)
    bl_visual_top = bl_bbox[1]
    bl_visual_h = bl_bbox[3] - bl_bbox[1]
    bl_y = bottom_bar_y + (BOTTOM_BAR_H // 2) - bl_visual_top - bl_visual_h // 2
    # Draw with brand colors
    bl_parts = [("PUREBR", BLUE), ("AI", ORANGE), ("N", BLUE), (".AI", WHITE)]
    bx = 40
    for text, color in bl_parts:
        draw.text((bx, bl_y), text, fill=color, font=font_bottom_left)
        bb = font_bottom_left.getbbox(text)
        bx += bb[2] - bb[0]

    # CTA right in orange
    cta_text = "Awaken Your AI Partner Today"
    cta_bbox = font_bottom_right.getbbox(cta_text)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_visual_top = cta_bbox[1]
    cta_visual_h = cta_bbox[3] - cta_bbox[1]
    cta_x = WIDTH - 40 - cta_w
    cta_y = bottom_bar_y + (BOTTOM_BAR_H // 2) - cta_visual_top - cta_visual_h // 2
    draw.text((cta_x, cta_y), cta_text, fill=ORANGE, font=font_bottom_right)

    # Save for each post ID
    for pid in post_ids:
        out_path = os.path.join(OUT_DIR, f"{pid}-standalone.jpg")
        canvas.save(out_path, "JPEG", quality=95)
        print(f"Saved: {out_path}")


# Generate all banners
for flux_file, title, treatment, post_ids in BANNERS:
    print(f"\nGenerating: {title} ({treatment})")
    generate_banner(flux_file, title, treatment, post_ids)

print(f"\nDone! Generated {sum(len(b[3]) for b in BANNERS)} banners.")

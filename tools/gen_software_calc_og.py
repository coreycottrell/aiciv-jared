"""
Generate OG image for Software Tool Stack Calculator
Size: 1456 x 816 px
"""
from PIL import Image, ImageDraw, ImageFont
import math

# ── Constants ──────────────────────────────────────────────────────────────
W, H = 1456, 816
BG = (8, 10, 18)           # #080a12
WHITE = (255, 255, 255)
ORANGE = (241, 66, 11)     # #f1420b
BLUE = (42, 147, 193)      # #2a93c1
DARK_CARD = (18, 22, 38)   # slightly lighter than bg for card
CARD_BORDER = (42, 147, 193, 60)  # faint blue border

FONT_BOLD   = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD_F = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"

PAD = 72  # safe margin

# ── Output paths ───────────────────────────────────────────────────────────
OUT1 = "/home/jared/exports/software-tool-stack-calculator-og.png"
OUT2 = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ai-tool-stack-calculator/software-tool-stack-calculator-og.png"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_text_mixed(draw, y, parts, fonts, colors, align="center", canvas_w=W, pad=PAD):
    """Draw a line of text where each word/segment can have its own font and color.
    parts: list of (text, font, color)
    Returns the bounding height of the line.
    """
    # Measure total width
    total_w = 0
    segments = []
    for text, font, color in parts:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        segments.append((text, font, color, w, h, bbox[1]))
        total_w += w

    # Add space between segments
    space_w = 0
    if len(segments) > 1:
        space_font = segments[0][1]
        sb = draw.textbbox((0, 0), " ", font=space_font)
        space_w = sb[2] - sb[0]
        total_w += space_w * (len(segments) - 1)

    if align == "center":
        x = (canvas_w - total_w) // 2
    elif align == "left":
        x = pad
    else:
        x = canvas_w - pad - total_w

    max_h = 0
    for i, (text, font, color, w, h, y_off) in enumerate(segments):
        draw.text((x, y - y_off), text, font=font, fill=color)
        x += w
        if i < len(segments) - 1:
            x += space_w
        if h > max_h:
            max_h = h

    return max_h


def draw_centered_text(draw, x_center, y, text, font, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((x_center - w // 2, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]


def make_image():
    img = Image.new("RGBA", (W, H), BG + (255,))
    draw = ImageDraw.Draw(img)

    # ── Background grid lines ──────────────────────────────────────────────
    grid_color = (255, 255, 255, 8)
    grid_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid_layer)
    step = 60
    for x in range(0, W + step, step):
        gd.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H + step, step):
        gd.line([(0, y), (W, y)], fill=grid_color, width=1)
    img = Image.alpha_composite(img, grid_layer)
    draw = ImageDraw.Draw(img)

    # ── Subtle radial glow behind headline ────────────────────────────────
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glow_layer)
    cx, cy = W // 2, 200
    for r in range(320, 0, -4):
        alpha = int(18 * (1 - r / 320))
        gd2.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(42, 147, 193, alpha))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # ── Fonts ─────────────────────────────────────────────────────────────
    f_headline_xl = load_font(FONT_BOLD, 96)
    f_headline_lg = load_font(FONT_BOLD, 88)
    f_sub         = load_font(FONT_REG, 32)
    f_card_label  = load_font(FONT_BOLD, 26)
    f_card_big    = load_font(FONT_BOLD, 108)
    f_card_small  = load_font(FONT_REG, 28)
    f_bottom_left = load_font(FONT_BOLD, 24)
    f_bottom_right= load_font(FONT_BOLD, 28)

    # ── TOP HEADLINE ──────────────────────────────────────────────────────
    # Line 1: "HOW MUCH ARE YOU" — white
    line1 = "HOW MUCH ARE YOU"
    bbox1 = draw.textbbox((0, 0), line1, font=f_headline_xl)
    w1 = bbox1[2] - bbox1[0]
    y_line1 = 72
    draw.text(((W - w1) // 2, y_line1), line1, font=f_headline_xl, fill=WHITE)
    h1 = bbox1[3] - bbox1[1]

    # Line 2: "WASTING ON" white + "SOFTWARE?" orange — same font size
    y_line2 = y_line1 + h1 + 16
    parts_line2 = [
        ("WASTING ON", f_headline_lg, WHITE),
        ("SOFTWARE?",  f_headline_lg, ORANGE),
    ]
    h2 = draw_text_mixed(draw, y_line2, parts_line2, None, None)

    # ── SUBHEADLINE ───────────────────────────────────────────────────────
    sub_text = "Hundreds of Tools  •  31 Categories  •  See Your Real Software Spend"
    y_sub = y_line2 + h2 + 32
    bbox_sub = draw.textbbox((0, 0), sub_text, font=f_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    draw.text(((W - w_sub) // 2, y_sub), sub_text, font=f_sub, fill=BLUE)
    h_sub = bbox_sub[3] - bbox_sub[1]

    # ── CARD ──────────────────────────────────────────────────────────────
    card_top = y_sub + h_sub + 52
    card_w = 640
    card_h = 220
    card_x = (W - card_w) // 2
    card_y = card_top

    # Card shadow/glow
    glow_c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd3 = ImageDraw.Draw(glow_c)
    for expand in range(16, 0, -1):
        alpha = int(30 * (expand / 16))
        gd3.rounded_rectangle(
            [card_x - expand, card_y - expand, card_x + card_w + expand, card_y + card_h + expand],
            radius=20 + expand, fill=(42, 147, 193, alpha)
        )
    img = Image.alpha_composite(img, glow_c)
    draw = ImageDraw.Draw(img)

    # Card body
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                            radius=16, fill=DARK_CARD)
    # Card border
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                            radius=16, outline=(42, 147, 193), width=2)

    # Card content
    cx_card = card_x + card_w // 2
    # Label: "AVERAGE TEAM WASTES"
    label_text = "AVERAGE TEAM WASTES"
    y_label = card_y + 28
    lbbox = draw.textbbox((0, 0), label_text, font=f_card_label)
    lw = lbbox[2] - lbbox[0]
    draw.text((cx_card - lw // 2, y_label), label_text, font=f_card_label, fill=(200, 200, 200))

    # Big number: "$847 / MONTH"
    big_text = "$847 / MONTH"
    y_big = y_label + (lbbox[3] - lbbox[1]) + 10
    bbbox = draw.textbbox((0, 0), big_text, font=f_card_big)
    bw = bbbox[2] - bbbox[0]
    draw.text((cx_card - bw // 2, y_big), big_text, font=f_card_big, fill=ORANGE)

    # Small subtitle
    small_text = "on overlapping & unused software tools"
    y_small = y_big + (bbbox[3] - bbbox[1]) + 12
    sbbox = draw.textbbox((0, 0), small_text, font=f_card_small)
    sw = sbbox[2] - sbbox[0]
    draw.text((cx_card - sw // 2, y_small), small_text, font=f_card_small, fill=(180, 180, 180))

    # ── BOTTOM BAR ────────────────────────────────────────────────────────
    bar_y = H - 64
    # Left: tool name
    left_text = "SOFTWARE TOOL STACK CALCULATOR"
    draw.text((PAD, bar_y), left_text, font=f_bottom_left, fill=(200, 200, 200))

    # Right: PUREBRAIN.ai branding
    # "PUREBR" blue + "AI" orange + "N" blue + ".ai" dim
    right_parts_text = "PUREBRAIN.AI"
    # Draw as two colors: PUREBR+N in blue, AI in orange
    # Split: "PUREBR" + "AI" + "N.AI"
    f_brand = load_font(FONT_BOLD, 30)
    brand_segments = [
        ("PUREBR", f_brand, BLUE),
        ("AI", f_brand, ORANGE),
        ("N.AI", f_brand, BLUE),
    ]
    # Measure total width
    total_bw = 0
    brand_data = []
    for seg_text, seg_font, seg_color in brand_segments:
        sb = draw.textbbox((0, 0), seg_text, font=seg_font)
        sw2 = sb[2] - sb[0]
        total_bw += sw2
        brand_data.append((seg_text, seg_font, seg_color, sw2, sb))

    bx = W - PAD - total_bw
    for seg_text, seg_font, seg_color, sw2, sb in brand_data:
        draw.text((bx, bar_y), seg_text, font=seg_font, fill=seg_color)
        bx += sw2

    # ── Separator line above bottom bar ───────────────────────────────────
    draw.line([(PAD, bar_y - 20), (W - PAD, bar_y - 20)], fill=(42, 147, 193, 60), width=1)

    # Convert to RGB for PNG
    final = img.convert("RGB")
    final.save(OUT1, "PNG", quality=95)
    import shutil
    shutil.copy2(OUT1, OUT2)
    print(f"Saved: {OUT1}")
    print(f"Copied: {OUT2}")
    print(f"Size: {final.size}")


if __name__ == "__main__":
    make_image()

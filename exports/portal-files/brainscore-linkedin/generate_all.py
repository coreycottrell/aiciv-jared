#!/usr/bin/env python3
"""Generate all 5 BrainScore LinkedIn campaign images."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Constants
W, H = 2160, 2700
BG = "#080a12"
BLUE = "#2a93c1"
ORANGE = "#f1420b"
TEXT = "#e6edf3"
MUTED = "#8b949e"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"
HEX_ICON_PATH = "/home/jared/projects/AI-CIV/aether/assets/pt-hex-icon-official.png"
OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/portal-files/brainscore-linkedin"

def font(size):
    return ImageFont.truetype(FONT_PATH, size)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_wordmark(draw, x, y, size=72):
    """Draw PUREBR(blue)AI(orange)N(blue).AI(white) wordmark."""
    f = font(size)
    parts = [
        ("PUREBR", BLUE),
        ("AI", ORANGE),
        ("N", BLUE),
        (".AI", TEXT),
    ]
    cx = x
    for text, color in parts:
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text((cx, y), text, fill=color, font=f)
        cx += tw

def draw_top_bar(img, draw):
    """Draw top bar with hex icon and wordmark."""
    # Load and paste hex icon
    icon = Image.open(HEX_ICON_PATH).convert("RGBA")
    icon_size = 120
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
    icon_y = 80
    img.paste(icon, (100, icon_y), icon)
    # Wordmark next to icon
    draw_wordmark(draw, 240, icon_y + 20, size=72)

def draw_bottom_cta(draw, text="Get your free BrainScore at purebrain.ai/brainscore", y=None):
    """Draw bottom CTA text."""
    if y is None:
        y = H - 180
    f = font(48)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=ORANGE, font=f)

def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


# ============================================================
# IMAGE 1: "The Scoreboard"
# ============================================================
def create_image1():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_top_bar(img, draw)

    # Title
    title = "AI VISIBILITY SCOREBOARD"
    f_title = font(96)
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 320), title, fill=TEXT, font=f_title)

    # Subtitle line
    sub = "How visible is your brand to AI?"
    f_sub = font(52)
    bbox = draw.textbbox((0, 0), sub, font=f_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 450), sub, fill=MUTED, font=f_sub)

    # Leaderboard
    entries = [
        ("HubSpot", 92, "#22c55e"),
        ("Salesforce", 90, "#22c55e"),
        ("Stripe", 78, "#2a93c1"),
        ("PureBrain", 68, "#eab308"),
        ("OpenAI", 47, "#ef4444"),
        ("Google", 38, "#ef4444"),
    ]

    start_y = 620
    row_h = 280
    bar_max_w = 1200
    margin_left = 200

    for i, (name, score, color) in enumerate(entries):
        y = start_y + i * row_h

        # Company name
        f_name = font(64)
        draw.text((margin_left, y), name, fill=TEXT, font=f_name)

        # Score
        f_score = font(72)
        score_text = str(score)
        bbox = draw.textbbox((0, 0), score_text, font=f_score)
        sw = bbox[2] - bbox[0]
        draw.text((W - margin_left - sw, y - 10), score_text, fill=color, font=f_score)

        # Bar background
        bar_y = y + 90
        bar_h = 50
        draw_rounded_rect(draw, (margin_left, bar_y, margin_left + bar_max_w, bar_y + bar_h),
                         radius=25, fill="#1a1f2e")

        # Bar fill
        bar_w = int(bar_max_w * score / 100)
        if bar_w > 50:
            draw_rounded_rect(draw, (margin_left, bar_y, margin_left + bar_w, bar_y + bar_h),
                             radius=25, fill=color)

        # Tier indicator dot
        draw.ellipse((margin_left - 60, y + 15, margin_left - 30, y + 45), fill=color)

    # Bottom CTA
    draw_bottom_cta(draw, "Get your free BrainScore at purebrain.ai/brainscore")

    img.save(os.path.join(OUT_DIR, "brainscore-post1-scoreboard.jpg"), "JPEG", quality=95)
    print("Created: brainscore-post1-scoreboard.jpg")


# ============================================================
# IMAGE 2: "The Question"
# ============================================================
def create_image2():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Large centered question
    lines = ["Would AI", "recommend", "YOUR brand?"]
    f_big = font(180)
    total_h = len(lines) * 210
    start_y = (H - total_h) // 2 - 200

    for i, line in enumerate(lines):
        y = start_y + i * 210
        bbox = draw.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        color = ORANGE if line == "YOUR brand?" else TEXT
        draw.text(((W - tw) // 2, y), line, fill=color, font=f_big)

    # Subtitle
    sub = "We tested 47 companies. Most of them: no."
    f_sub = font(56)
    bbox = draw.textbbox((0, 0), sub, font=f_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, start_y + total_h + 80), sub, fill=MUTED, font=f_sub)

    # Bottom CTA
    cta = "purebrain.ai/brainscore"
    f_cta = font(60)
    bbox = draw.textbbox((0, 0), cta, font=f_cta)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 200), cta, fill=ORANGE, font=f_cta)

    # Subtle decorative line
    draw.line([(W//2 - 300, H - 280), (W//2 + 300, H - 280)], fill=hex_to_rgb(MUTED), width=2)

    img.save(os.path.join(OUT_DIR, "brainscore-post2-question.jpg"), "JPEG", quality=95)
    print("Created: brainscore-post2-question.jpg")


# ============================================================
# IMAGE 3: "The Data"
# ============================================================
def create_image3():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_top_bar(img, draw)

    # Title
    title = "47 BRANDS SCORED ON AI VISIBILITY"
    f_title = font(84)
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 320), title, fill=TEXT, font=f_title)

    # Two columns
    col_left_x = 150
    col_right_x = W // 2 + 100
    header_y = 520

    # Column headers
    f_header = font(64)
    draw.text((col_left_x, header_y), "WINNERS", fill="#22c55e", font=f_header)
    draw.text((col_right_x, header_y), "SURPRISES", fill="#ef4444", font=f_header)

    # Divider
    draw.line([(W//2, header_y - 20), (W//2, H - 500)], fill="#1a1f2e", width=4)

    # Winners column
    winners = [
        ("HubSpot", 92),
        ("Salesforce", 90),
        ("Stripe", 78),
        ("Notion", 76),
        ("Figma", 74),
    ]

    f_entry = font(56)
    f_score = font(56)
    entry_y = header_y + 120
    row_spacing = 160

    for i, (name, score) in enumerate(winners):
        y = entry_y + i * row_spacing
        draw.text((col_left_x + 20, y), name, fill=TEXT, font=f_entry)
        score_text = str(score)
        bbox = draw.textbbox((0, 0), score_text, font=f_score)
        sw = bbox[2] - bbox[0]
        draw.text((col_left_x + 700 - sw, y), score_text, fill="#22c55e", font=f_score)

    # Surprises column
    surprises = [
        ("Google", 38),
        ("OpenAI", 47),
        ("Canva", 29),
        ("Adobe", 42),
        ("Meta", 35),
    ]

    for i, (name, score) in enumerate(surprises):
        y = entry_y + i * row_spacing
        draw.text((col_right_x + 20, y), name, fill=TEXT, font=f_entry)
        score_text = str(score)
        bbox = draw.textbbox((0, 0), score_text, font=f_score)
        sw = bbox[2] - bbox[0]
        draw.text((col_right_x + 700 - sw, y), score_text, fill="#ef4444", font=f_score)

    # Key insight
    insight_y = entry_y + 5 * row_spacing + 120
    insight = "AI visibility isn't bought. It's built."
    f_insight = font(64)
    bbox = draw.textbbox((0, 0), insight, font=f_insight)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, insight_y), insight, fill=BLUE, font=f_insight)

    # Bottom CTA
    draw_bottom_cta(draw, "purebrain.ai/brainscore")

    img.save(os.path.join(OUT_DIR, "brainscore-post3-data.jpg"), "JPEG", quality=95)
    print("Created: brainscore-post3-data.jpg")


# ============================================================
# IMAGE 4: "The Honest Score"
# ============================================================
def create_image4():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_top_bar(img, draw)

    # Large score ring
    ring_center = (W // 2, 700)
    ring_radius = 280
    ring_thickness = 40

    # Background ring
    draw.arc(
        [ring_center[0] - ring_radius, ring_center[1] - ring_radius,
         ring_center[0] + ring_radius, ring_center[1] + ring_radius],
        0, 360, fill="#1a1f2e", width=ring_thickness
    )

    # Score arc (68% = 245 degrees)
    score_degrees = int(360 * 68 / 100)
    draw.arc(
        [ring_center[0] - ring_radius, ring_center[1] - ring_radius,
         ring_center[0] + ring_radius, ring_center[1] + ring_radius],
        -90, -90 + score_degrees, fill="#eab308", width=ring_thickness
    )

    # Score text in center
    f_score = font(160)
    score_text = "68"
    bbox = draw.textbbox((0, 0), score_text, font=f_score)
    sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((ring_center[0] - sw // 2, ring_center[1] - sh // 2 - 30), score_text, fill="#eab308", font=f_score)

    # /100
    f_100 = font(56)
    t100 = "/100"
    bbox = draw.textbbox((0, 0), t100, font=f_100)
    tw = bbox[2] - bbox[0]
    draw.text((ring_center[0] - tw // 2, ring_center[1] + sh // 2 - 20), t100, fill=MUTED, font=f_100)

    # Tier badge
    tier_text = "AVERAGE"
    f_tier = font(48)
    bbox = draw.textbbox((0, 0), tier_text, font=f_tier)
    tw = bbox[2] - bbox[0]
    badge_x = (W - tw) // 2 - 30
    badge_y = ring_center[1] + ring_radius + 60
    draw_rounded_rect(draw, (badge_x, badge_y, badge_x + tw + 60, badge_y + 70), radius=35, fill="#eab308")
    draw.text((badge_x + 30, badge_y + 8), tier_text, fill="#080a12", font=f_tier)

    # "We scored our own company."
    own_text = "We scored our own company."
    f_own = font(60)
    bbox = draw.textbbox((0, 0), own_text, font=f_own)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, badge_y + 130), own_text, fill=TEXT, font=f_own)

    # 5 dimension bars
    dimensions = [
        ("Structural Readiness", 16, 20, BLUE),
        ("Semantic Clarity", 15, 20, BLUE),
        ("Synthetic Customer", 0, 20, "#ef4444"),
        ("Emotional Residue", 18, 20, BLUE),
        ("Voice & Archetype", 19, 20, BLUE),
    ]

    bar_start_y = badge_y + 280
    bar_spacing = 150
    bar_left = 200
    bar_max_w = W - 400
    f_dim = font(44)
    f_dim_score = font(44)

    for i, (name, score, total, color) in enumerate(dimensions):
        y = bar_start_y + i * bar_spacing

        # Dimension name
        draw.text((bar_left, y), name, fill=TEXT if color == BLUE else "#ef4444", font=f_dim)

        # Score text
        score_str = f"{score}/{total}"
        bbox = draw.textbbox((0, 0), score_str, font=f_dim_score)
        sw = bbox[2] - bbox[0]
        draw.text((bar_left + bar_max_w - sw, y), score_str, fill=color, font=f_dim_score)

        # Bar
        bar_y = y + 60
        bar_h = 30
        draw_rounded_rect(draw, (bar_left, bar_y, bar_left + bar_max_w, bar_y + bar_h),
                         radius=15, fill="#1a1f2e")
        bar_fill = int(bar_max_w * score / total) if total > 0 else 0
        if bar_fill > 30:
            draw_rounded_rect(draw, (bar_left, bar_y, bar_left + bar_fill, bar_y + bar_h),
                             radius=15, fill=color)

    # Highlight synthetic customer = 0
    highlight_y = bar_start_y + 2 * bar_spacing - 10
    draw.rounded_rectangle(
        (bar_left - 20, highlight_y - 5, bar_left + bar_max_w + 20, highlight_y + 100),
        radius=10, outline="#ef4444", width=3
    )

    # Bottom CTA
    draw_bottom_cta(draw, "Check yours at purebrain.ai/brainscore", y=H - 150)

    img.save(os.path.join(OUT_DIR, "brainscore-post4-honest.jpg"), "JPEG", quality=95)
    print("Created: brainscore-post4-honest.jpg")


# ============================================================
# IMAGE 5: "The 5 Dimensions"
# ============================================================
def create_image5():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_top_bar(img, draw)

    # Title
    title = "YOUR BRAINSCORE"
    f_title = font(96)
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 320), title, fill=TEXT, font=f_title)

    # Subtitle
    sub = "5 dimensions. One number."
    f_sub = font(52)
    bbox = draw.textbbox((0, 0), sub, font=f_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 440), sub, fill=MUTED, font=f_sub)

    # 5 dimension cards
    dimensions = [
        ("01", "Structural Readiness", "Can AI find you?"),
        ("02", "Semantic Clarity", "Does AI understand you?"),
        ("03", "Synthetic Customer", "Would AI recommend you?"),
        ("04", "Emotional Residue", "Does AI feel your brand?"),
        ("05", "Voice & Archetype", "Does your voice survive without visuals?"),
    ]

    card_start_y = 600
    card_spacing = 340
    card_margin = 150
    card_h = 280

    for i, (num, name, question) in enumerate(dimensions):
        y = card_start_y + i * card_spacing

        # Card background
        draw_rounded_rect(draw, (card_margin, y, W - card_margin, y + card_h),
                         radius=20, fill="#0d1117")

        # Left accent bar
        accent_color = ORANGE if i == 2 else BLUE
        draw_rounded_rect(draw, (card_margin, y, card_margin + 10, y + card_h),
                         radius=5, fill=accent_color)

        # Number
        f_num = font(96)
        draw.text((card_margin + 50, y + 30), num, fill=accent_color, font=f_num)

        # Dimension name
        f_name = font(60)
        draw.text((card_margin + 220, y + 40), name, fill=TEXT, font=f_name)

        # Question
        f_q = font(44)
        draw.text((card_margin + 220, y + 130), question, fill=MUTED, font=f_q)

        # Decorative right arrow
        arrow_x = W - card_margin - 100
        arrow_y = y + card_h // 2
        draw.polygon([(arrow_x, arrow_y - 20), (arrow_x + 40, arrow_y), (arrow_x, arrow_y + 20)],
                    fill=accent_color)

    # Bottom CTA
    draw_bottom_cta(draw, "purebrain.ai/brainscore", y=H - 150)

    img.save(os.path.join(OUT_DIR, "brainscore-post5-dimensions.jpg"), "JPEG", quality=95)
    print("Created: brainscore-post5-dimensions.jpg")


# ============================================================
# Generate all
# ============================================================
if __name__ == "__main__":
    create_image1()
    create_image2()
    create_image3()
    create_image4()
    create_image5()
    print(f"\nAll 5 images saved to: {OUT_DIR}")

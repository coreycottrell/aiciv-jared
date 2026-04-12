#!/usr/bin/env python3
"""Fix the bracket artifact in the OpenClaw LinkedIn image CTA."""

from PIL import Image, ImageDraw, ImageFont

INPUT = "/home/jared/exports/portal-files/linkedin-openclaw-2026-04-04-v4.png"
OUTPUT = "/home/jared/exports/portal-files/linkedin-openclaw-2026-04-04-v5.png"
FONT_PATH = "/home/jared/.fonts/Oswald-Bold.ttf"

img = Image.open(INPUT).convert("RGBA")
w, h = img.size
print(f"Image size: {w}x{h}")

draw = ImageDraw.Draw(img)

# CTA text is at y=1195 to y=1230 based on pixel analysis
# Paint over with generous margins
cta_top = 1190
cta_bottom = 1235

# Sample background color from the dark area below the text
bg_colors = []
for x_sample in [10, 50, 100, 200, w-100]:
    for y_sample in [1240, 1250, 1260]:
        if y_sample < h:
            c = img.getpixel((x_sample, y_sample))
            bg_colors.append(c)

# Use the most common dark color
avg_r = int(sum(c[0] for c in bg_colors) / len(bg_colors))
avg_g = int(sum(c[1] for c in bg_colors) / len(bg_colors))
avg_b = int(sum(c[2] for c in bg_colors) / len(bg_colors))
bg_color = (avg_r, avg_g, avg_b, 255)
print(f"Using background color: {bg_color}")

# Paint over the CTA strip
draw.rectangle([0, cta_top, w, cta_bottom], fill=bg_color)

# Now redraw the CTA text with Oswald Bold
# Use pipe separator instead of the broken arrow
cta_text = "Own your AI partner  |  purebrain.ai"

# Match original font size - the text spanned about 25px tall across ~350px wide
# Try sizes to match
font_size = 22
font = ImageFont.truetype(FONT_PATH, font_size)
bbox = draw.textbbox((0, 0), cta_text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]
print(f"Font size: {font_size}, text dims: {text_w}x{text_h}")

# Center the text
text_x = (w - text_w) // 2
text_y = cta_top + (cta_bottom - cta_top - text_h) // 2

# Draw in white
draw.text((text_x, text_y), cta_text, fill=(255, 255, 255, 255), font=font)

# Save
img_rgb = img.convert("RGB")
img_rgb.save(OUTPUT, quality=95)
print(f"Saved to {OUTPUT}")

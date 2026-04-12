#!/usr/bin/env python3
"""
Generate two blog banner images for PureBrain.ai using OpenAI DALL-E.
- Image 1: CEO vs Employee AI Lens
- Image 2: Shadow AI Problem
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in .env")
    sys.exit(1)

OUTPUT_DIR = '/home/jared/projects/AI-CIV/aether/exports/blog-content'

BANNERS = [
    {
        "output_path": f"{OUTPUT_DIR}/2026-02-18-ceo-employee-banner.png",
        "label": "Image 1: CEO vs Employee AI Lens",
        "prompt": (
            "Professional blog banner image, 1792x1024, dark futuristic tech aesthetic. "
            "Split composition: LEFT HALF shows a sleek executive C-suite boardroom with a clean AI dashboard "
            "on a large curved monitor, data charts, neural network visualizations, calm corporate confidence, "
            "cool blue tones (#2a93c1 blue accents). RIGHT HALF shows a cluttered employee desk late at night, "
            "chaotic papers, stress lines dissolving as an AI assistant interface glows warmly, relief and "
            "humanity, orange warm light (#f1420b orange). A subtle glowing dividing line splits the two worlds. "
            "TOP CENTER text area: bold white text 'The CEO Sees a Dashboard. The Employee Sees a Lifeline.' "
            "BOTTOM text: smaller white text 'Why AI adoption looks completely different depending on where you sit' "
            "BOTTOM RIGHT: 'PUREBRAIN.ai' with hexagonal honeycomb logo in corner. "
            "Style: cinematic, professional, high-contrast, editorial tech magazine cover. "
            "Dark charcoal background (#1a1a2e). No cartoonish elements. Photorealistic rendering style."
        )
    },
    {
        "output_path": f"{OUTPUT_DIR}/2026-02-18-shadow-ai-banner.png",
        "label": "Image 2: Shadow AI Problem",
        "prompt": (
            "Professional blog banner image, 1792x1024, dark futuristic tech aesthetic. "
            "Split composition: LEFT HALF depicts fragmented, chaotic AI nodes scattered across a dark red/orange "
            "network (#f1420b orange-red accents), disconnected glowing orbs flying apart, shadowy uncontrolled "
            "data flows, warning tones, entropy and disorder. Label area 'SHADOW AI' in subtle text. "
            "RIGHT HALF shows a clean unified neural network in luminous blue (#2a93c1), perfectly connected nodes, "
            "organized data flows, sanctioned AI mesh, order and control. Label area 'GOVERNED AI' in subtle text. "
            "A sharp vertical dividing line between chaos and order. "
            "TOP CENTER: bold white text '65% of Enterprise AI Tools Operate Without IT Oversight' "
            "BOTTOM CENTER: smaller white italic text 'The $670,000 question every CTO should be asking' "
            "BOTTOM RIGHT corner: hexagonal honeycomb 'PUREBRAIN.ai' logo watermark. "
            "Style: cinematic, professional, cybersecurity editorial aesthetic, dark background (#0d0d1a). "
            "No cartoonish elements. Photorealistic digital art style."
        )
    }
]


def generate_image_dalle(prompt: str, output_path: str, label: str) -> bool:
    """Generate image using DALL-E 3 via OpenAI API."""
    print(f"\nGenerating {label}...")
    print(f"Output: {output_path}")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1792x1024",
        "quality": "hd",
        "response_format": "url"
    }

    print("Calling DALL-E 3 API (HD quality, 1792x1024)...")
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        print(f"ERROR: API returned {response.status_code}")
        print(response.text)
        return False

    data = response.json()
    image_url = data['data'][0]['url']
    revised_prompt = data['data'][0].get('revised_prompt', 'N/A')
    print(f"Image URL received. Revised prompt snippet: {revised_prompt[:100]}...")

    # Download the image
    print("Downloading image...")
    img_response = requests.get(image_url, timeout=60)
    if img_response.status_code != 200:
        print(f"ERROR: Failed to download image, status {img_response.status_code}")
        return False

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(img_response.content)

    file_size = os.path.getsize(output_path)
    print(f"Saved: {output_path} ({file_size:,} bytes)")
    return True


def send_telegram_photo(image_path: str, caption: str) -> bool:
    """Send a photo to Jared via Telegram bot."""
    BOT_TOKEN = "8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0"
    CHAT_ID = "548906264"

    print(f"\nSending to Telegram: {os.path.basename(image_path)}")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    with open(image_path, 'rb') as photo:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo},
            timeout=60
        )

    if response.status_code == 200:
        print(f"Telegram send SUCCESS: {os.path.basename(image_path)}")
        return True
    else:
        print(f"Telegram send FAILED: {response.status_code} - {response.text}")
        return False


def main():
    print("=== PureBrain.ai Blog Banner Generator ===")
    print(f"Using OpenAI DALL-E 3 (HD quality)")
    print(f"Output directory: {OUTPUT_DIR}")

    results = []

    for banner in BANNERS:
        success = generate_image_dalle(
            prompt=banner['prompt'],
            output_path=banner['output_path'],
            label=banner['label']
        )
        results.append({
            "label": banner['label'],
            "path": banner['output_path'],
            "success": success
        })

    print("\n=== Generation Results ===")
    all_good = True
    for r in results:
        status = "SUCCESS" if r['success'] else "FAILED"
        print(f"  {status}: {r['label']}")
        if not r['success']:
            all_good = False

    if not all_good:
        print("\nSome images failed to generate. Check errors above.")
        sys.exit(1)

    # Send to Telegram
    print("\n=== Sending to Telegram ===")

    captions = [
        "Banner Option A: CEO vs Employee AI Lens\n\nTitle: 'The CEO Sees a Dashboard. The Employee Sees a Lifeline.'\n\nReview and reply APPROVE or REVISE with notes.",
        "Banner Option B: Shadow AI Problem\n\nTitle: '65% of Enterprise AI Tools Operate Without IT Oversight'\nSubtitle: 'The $670,000 question every CTO should be asking'\n\nReview and reply APPROVE or REVISE with notes."
    ]

    for r, caption in zip(results, captions):
        if r['success']:
            send_telegram_photo(r['path'], caption)

    print("\n=== Done ===")
    print("Both banners generated and sent to Jared on Telegram.")
    for r in results:
        if r['success']:
            print(f"  {r['path']}")


if __name__ == "__main__":
    main()

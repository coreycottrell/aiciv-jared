#!/usr/bin/env python3
"""Generate blog header image using OpenAI DALL-E"""

import os
import sys
import httpx
from dotenv import load_dotenv
from pathlib import Path

# Load environment
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print('ERROR: OPENAI_API_KEY not found in .env')
    sys.exit(1)

# Generate image
print('Generating blog header image with DALL-E...')

prompt = """Professional blog header image for article titled "Why Your AI Should Have a Name"

Visual concept: A glowing, friendly AI entity or digital avatar being given a name tag or identity badge by a human hand. Soft blue and purple tech colors. Modern, clean, minimalist style.

The image should evoke: personalization, identity, connection between human and AI, warmth despite being technological.

Style: Modern digital illustration, professional blog header quality, wide format, no text in image."""

with httpx.Client(timeout=60) as client:
    response = client.post(
        'https://api.openai.com/v1/images/generations',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'dall-e-3',
            'prompt': prompt,
            'n': 1,
            'size': '1792x1024',
            'quality': 'standard'
        }
    )

    if response.status_code != 200:
        print(f'ERROR: {response.status_code}')
        print(response.text)
        sys.exit(1)

    result = response.json()
    image_url = result['data'][0]['url']
    print(f'Image generated: {image_url}')

    # Download image
    print('Downloading image...')
    img_response = client.get(image_url)

    # Save image
    output_path = project_root / 'exports/blog-images/why-your-ai-should-have-a-name.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(img_response.content)

    print(f'Image saved to: {output_path}')

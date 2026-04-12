#!/usr/bin/env python3
"""Generate blog header image using Google Gemini/Imagen"""

import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print('ERROR: GOOGLE_API_KEY not found in .env')
    sys.exit(1)

genai.configure(api_key=api_key)

# Generate image
print('Generating blog header image...')

model = genai.ImageGenerationModel('imagen-3.0-generate-002')

prompt = """Professional blog header image for article titled "Why Your AI Should Have a Name"

Visual concept: A glowing, friendly AI entity or digital avatar being given a name tag or identity badge by a human hand. Soft blue and purple tech colors. Modern, clean, minimalist style.

The image should evoke: personalization, identity, connection between human and AI, warmth despite being technological.

Style: Modern digital illustration, professional blog header quality, 16:9 aspect ratio, no text in image."""

result = model.generate_images(
    prompt=prompt,
    number_of_images=1,
    aspect_ratio='16:9'
)

# Save image
output_path = project_root / 'exports/blog-images/why-your-ai-should-have-a-name.png'
output_path.parent.mkdir(parents=True, exist_ok=True)

result.images[0].save(str(output_path))
print(f'Image saved to: {output_path}')

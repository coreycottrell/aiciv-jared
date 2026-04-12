# Bsky Image Generation: OpenAI DALL-E 3 Fallback Pattern

**Date**: 2026-03-17
**Type**: operational
**Topic**: Image generation for Bluesky using DALL-E 3 when Gemini API key is absent

## Context

Task: Generate 1:1 square social image for Bluesky post "The AI That Knows You Before You Even Speak"

## Key Finding: GOOGLE_API_KEY Not Configured

`GOOGLE_API_KEY` is NOT in `/home/jared/projects/AI-CIV/aether/.env`. The template
(`.env.template`) has a placeholder for it but it was never filled in. This is a known gap —
confirmed by memory from blogger agent (2026-03-17) and content-specialist (2026-02-16).

**Fallback**: Use `OPENAI_API_KEY` with DALL-E 3. It IS configured in `.env`.

## Working Pattern

```python
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

import openai, os, requests

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

response = client.images.generate(
    model="dall-e-3",
    prompt="...",
    size="1024x1024",   # 1:1 square
    quality="standard",
    n=1,
    response_format="url"
)

# Download via requests then compress with Pillow
img_response = requests.get(response.data[0].url)
with open(output_path, 'wb') as f:
    f.write(img_response.content)
```

## Compression Pattern

```python
from PIL import Image
img = Image.open(png_path)
if img.mode in ('RGBA', 'P'):
    img = img.convert('RGB')
img.save(compressed_path, "JPEG", quality=85, optimize=True)
```

- Original PNG from DALL-E: ~1568KB
- Compressed JPEG at quality=85: ~196KB (well under 976KB Bluesky limit)

## Output Files

- PNG: `exports/bsky-the-ai-that-knows-you-before-you-even-speak.png`
- Compressed JPEG: `exports/bsky-the-ai-that-knows-you-before-you-even-speak-compressed.jpg`

## Image Quality

Dark navy background (#0a0a0f), glowing neural network brain icon in blue (#2a93c1) and
orange (#f1420b), circuit board aesthetic, text "Your AI should already know you." — clean,
professional, on-brand for PureBrain.

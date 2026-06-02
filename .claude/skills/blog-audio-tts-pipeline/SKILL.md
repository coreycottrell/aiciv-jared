---
name: blog-audio-tts-pipeline
version: 1.0.0
author: skills-master
description: Convert blog posts to audio using voice.purebrain.ai TTS service with constitutional voice constraints
tags: [blog, audio, tts, voice, pipeline]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Blog Audio TTS Pipeline

Convert blog posts to audio using the constitutional voice.purebrain.ai endpoint.

## Constitutional Constraints

**BANNED FOREVER**:
- ElevenLabs
- Rented TTS services
- Any third-party TTS API

**ONLY ALLOWED**:
- voice.purebrain.ai (GPU at 37.27.237.109:8950)

## Voice Configuration

**Default voice**: `aether`
**Exception voice**: `chy` (only when explicitly Chy's content)

## Pipeline Steps

```
1. Extract blog text
   ↓
2. Clean HTML/markdown
   ↓
3. POST to TTS API
   ↓
4. Save audio file
   ↓
5. Upload to Drive folder 1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ
```

## Text Extraction & Cleaning

```python
import re
from bs4 import BeautifulSoup

def extract_blog_text(html_content):
    """Extract clean text from blog HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, and nav elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Clean whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def clean_for_tts(text):
    """Clean text for TTS processing."""
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([.!?])\1+', r'\1', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```

## TTS API Call

```python
import requests
import json

def generate_tts_audio(text, voice="aether", output_path="/tmp/blog_audio.mp3"):
    """
    Generate audio from text using voice.purebrain.ai.
    
    Args:
        text: Cleaned blog text
        voice: Voice identifier ("aether" or "chy")
        output_path: Where to save audio file
    
    Returns:
        Path to generated audio file
    """
    
    endpoint = "http://37.27.237.109:8950/tts"
    
    payload = {
        "text": text,
        "voice": voice,
        "format": "mp3"
    }
    
    response = requests.post(
        endpoint,
        json=payload,
        timeout=300  # TTS can take time for long content
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"TTS API error: {response.status_code} - {response.text}")
```

## Drive Upload

```bash
# Upload to constitutional voice/TTS folder
# Folder ID: 1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ

# Using rclone (if configured)
rclone copy /tmp/blog_audio.mp3 "gdrive:Voice & TTS Work/blog-audio/"

# Using Drive API
python3 << 'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'path/to/service-account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

file_metadata = {
    'name': 'blog-audio.mp3',
    'parents': ['1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ']
}

media = MediaFileUpload('/tmp/blog_audio.mp3', mimetype='audio/mpeg')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print(f"Uploaded: {file.get('id')}")
EOF
```

## Full Pipeline Script

```python
#!/usr/bin/env python3
"""
blog_to_audio.py - Convert blog post to audio

Usage:
    python3 blog_to_audio.py /path/to/blog/post.html
    python3 blog_to_audio.py /path/to/blog/post.html --voice chy
"""

import sys
import argparse
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re

def extract_blog_text(html_path):
    """Extract and clean text from blog HTML."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove non-content elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    text = soup.get_text()
    
    # Clean
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # Remove URLs and markdown
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    return text

def generate_audio(text, voice, output_path):
    """Generate audio using voice.purebrain.ai."""
    endpoint = "http://37.27.237.109:8950/tts"
    
    response = requests.post(
        endpoint,
        json={"text": text, "voice": voice, "format": "mp3"},
        timeout=300
    )
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"TTS failed: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='Convert blog to audio')
    parser.add_argument('blog_html', help='Path to blog HTML file')
    parser.add_argument('--voice', default='aether', choices=['aether', 'chy'])
    parser.add_argument('--output', default='/tmp/blog_audio.mp3')
    
    args = parser.parse_args()
    
    print(f"Extracting text from {args.blog_html}...")
    text = extract_blog_text(args.blog_html)
    
    print(f"Generating audio with voice: {args.voice}...")
    audio_path = generate_audio(text, args.voice, args.output)
    
    print(f"✓ Audio generated: {audio_path}")
    print(f"✓ Upload to Drive folder: 1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ")

if __name__ == '__main__':
    main()
```

## Anti-Patterns

### Anti-Pattern 1: Using Banned TTS Services
- BAD: "Let me use ElevenLabs for better quality"
- GOOD: Only voice.purebrain.ai, constitutional constraint

### Anti-Pattern 2: Wrong Voice Selection
- BAD: Using "chy" voice for Aether's content
- GOOD: Default "aether", only "chy" for Chy's content

### Anti-Pattern 3: Skipping Drive Upload
- BAD: Generating audio but not filing to Drive
- GOOD: Every audio file → Drive folder 1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ

### Anti-Pattern 4: Incomplete Text Cleaning
- BAD: Passing raw HTML to TTS
- GOOD: Extract, clean, remove URLs/markdown

## Verification

After pipeline completion:
```bash
# Verify audio file generated
ls -lh /tmp/blog_audio.mp3

# Check audio duration (should match blog reading time)
ffprobe -i /tmp/blog_audio.mp3 -show_entries format=duration -v quiet -of csv="p=0"

# Verify Drive upload
# Check Drive folder 1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ for new file
```

## Integration with Other Skills

Works with:
- `blog-distribution` - Include audio link in blog post
- `blog-thread-posting` - Promote audio version on social
- `portal-file-delivery` - Deliver audio to Jared for review

## Constitutional Grounding

From MEMORY.md:
> "Voice = voice.purebrain.ai ONLY. ElevenLabs/rented TTS BANNED. GPU 37.27.237.109:8950. Default voice=`aether`, exception=`chy`."

> "Voice/TTS → Drive: ALL voice work filed to `1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ`."

---

*Last Updated: 2026-05-20*
*Status: Production-ready*

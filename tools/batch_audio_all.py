#!/usr/bin/env python3
"""
batch_audio_all.py — Generate audio for all blog posts missing audio.mp3.

Uses blog_audio.py for posts with source .md files.
For posts with only index.html, extracts text from HTML directly.

Usage:
    python3 tools/batch_audio_all.py
"""

import os
import re
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blog_audio import generate_blog_audio, ELEVENLABS_API_KEY

BLOG_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog")
SRC_DIR = Path("/home/jared/projects/AI-CIV/aether/purebrain-site/src/content/blog")

# Map slug -> source .md path from purebrain-site
def build_src_map():
    src_map = {}
    if SRC_DIR.exists():
        for f in SRC_DIR.iterdir():
            m = re.match(r"^(\d{4}-\d{2}-\d{2})--(.+)\.md$", f.name)
            if m:
                src_map[m.group(2)] = f
    return src_map


def extract_text_from_html(html_path: Path) -> str:
    """Extract readable text from a blog post HTML file for TTS."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove script tags
    content = re.sub(r"<script[^>]*>.*?</script>", " ", content, flags=re.DOTALL)
    # Remove style tags
    content = re.sub(r"<style[^>]*>.*?</style>", " ", content, flags=re.DOTALL)
    # Remove HTML comments
    content = re.sub(r"<!--.*?-->", " ", content, flags=re.DOTALL)
    # Remove HTML tags
    content = re.sub(r"<[^>]+>", " ", content)
    # Decode common HTML entities
    content = re.sub(r"&#8217;", "'", content)
    content = re.sub(r"&#8220;|&#8221;", '"', content)
    content = re.sub(r"&#8230;", "...", content)
    content = re.sub(r"&#8211;", "-", content)
    content = re.sub(r"&amp;", "&", content)
    content = re.sub(r"&nbsp;", " ", content)
    content = re.sub(r"&lt;", "<", content)
    content = re.sub(r"&gt;", ">", content)
    # Clean whitespace
    content = re.sub(r"\s+", " ", content).strip()

    # Remove nav/header/footer boilerplate (heuristic: first 200 chars often nav)
    # Find actual content start after title pattern
    # Remove "Home Blog Title" breadcrumb prefix
    content = re.sub(r"^.{0,300}?(\d+ min read)", "", content).strip()

    return content


def main():
    if not ELEVENLABS_API_KEY:
        print("ERROR: ELEVENLABS_API_KEY not set in .env")
        sys.exit(1)

    src_map = build_src_map()

    # Find all posts missing audio
    posts_needing_audio = []
    for slug_dir in sorted(BLOG_DIR.iterdir()):
        if not slug_dir.is_dir():
            continue
        slug = slug_dir.name
        audio_path = slug_dir / "audio.mp3"
        html_path = slug_dir / "index.html"

        if audio_path.exists():
            continue  # Already has audio
        if not html_path.exists():
            continue  # No HTML either

        posts_needing_audio.append({
            "slug": slug,
            "html_path": html_path,
            "audio_path": audio_path,
            "src_md": src_map.get(slug),
        })

    print(f"Posts needing audio: {len(posts_needing_audio)}")
    print()

    generated = 0
    failed = []

    for i, post in enumerate(posts_needing_audio, 1):
        slug = post["slug"]
        audio_out = str(post["audio_path"])
        print(f"[{i}/{len(posts_needing_audio)}] Generating audio for: {slug}")

        try:
            if post["src_md"]:
                # Use source markdown file
                print(f"  Source: {post['src_md'].name}")
                generate_blog_audio(str(post["src_md"]), audio_out)
            else:
                # Extract text from HTML, write to temp .md file
                print(f"  Source: HTML extraction (no source .md)")
                text = extract_text_from_html(post["html_path"])
                if len(text) < 100:
                    print(f"  WARNING: Very short text ({len(text)} chars) - skipping")
                    failed.append((slug, "too short after extraction"))
                    continue
                print(f"  Extracted {len(text)} chars from HTML")
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False, encoding="utf-8"
                ) as tf:
                    tf.write(text)
                    tmp_path = tf.name
                try:
                    generate_blog_audio(tmp_path, audio_out)
                finally:
                    os.unlink(tmp_path)

            if os.path.exists(audio_out) and os.path.getsize(audio_out) > 1000:
                size_kb = os.path.getsize(audio_out) // 1024
                print(f"  SUCCESS: {size_kb}KB written to {audio_out}")
                generated += 1
            else:
                print(f"  WARNING: Output file missing or too small")
                failed.append((slug, "empty output"))

        except Exception as e:
            print(f"  ERROR: {e}")
            failed.append((slug, str(e)))

        # Rate limit: pause between requests
        if i < len(posts_needing_audio):
            print(f"  Waiting 3s for rate limit...")
            time.sleep(3)

        print()

    print(f"\n=== AUDIO GENERATION COMPLETE ===")
    print(f"Generated: {generated}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for slug, reason in failed:
            print(f"  - {slug}: {reason}")

    return generated, failed


if __name__ == "__main__":
    gen, fail = main()
    print(f"\nFinal: {gen} audio files generated, {len(fail)} failed")

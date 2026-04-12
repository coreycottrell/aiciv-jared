# Blog Audio Pipeline — ElevenLabs TTS Integration
**Date**: 2026-03-17
**Type**: teaching
**Topic**: ElevenLabs TTS for blog audio, chunking strategy, CF Pages deploy with binary files

---

## What Was Built

`tools/blog_audio.py` — a standalone Python tool that converts blog markdown to MP3 audio via ElevenLabs TTS API.

## Key Patterns

### 1. Text Extraction Order Matters
Strip in this order to avoid corrupting text:
1. Front matter (`---...---`)
2. HTML comments (catches CTA blocks before stripping HTML tags)
3. HTML tags
4. FAQ sections (markdown heading-bounded)
5. Transparency / Daily Recap blocks
6. Metadata fields (`**Author**:`, etc.)
7. Internal note lines
8. Markdown formatting (bold/italic/links/headings)
9. Whitespace normalization

### 2. ElevenLabs Chunking
- API hard limit: 5000 chars per request
- Safe limit used: 4800 chars
- Split strategy: paragraph breaks first, sentence breaks fallback
- Response is raw MP3 bytes — concatenate directly (no re-encoding needed)
- ElevenLabs MP3 output is bit-rate ~128kbps; 12.3 MB = ~767 seconds (~12.8 min)

### 3. Duration Estimation Bug
Raw byte size / 8000 gives wildly wrong estimates for MP3.
Use `ffprobe -v quiet -show_entries format=duration -of csv=p=0 <file>` for real duration.
Or: ElevenLabs MP3 at 128kbps = size_bytes / (128000/8) = size_bytes / 16000 seconds.

### 4. Audio Player HTML Insertion Point
Insert AFTER `.byline` paragraph, BEFORE the italic subtitle paragraph.
That keeps the player visible before any article body text.

### 5. CF Pages Handles Binary Files Fine
`wrangler pages deploy` uploaded the 12MB MP3 without issues.
Both `index.html` and `audio.mp3` uploaded as 2 new files (317 previously cached).

## File Paths
- Tool: `tools/blog_audio.py`
- Blog HTML: `exports/cf-pages-deploy/blog/prompting-is-dead/index.html`
- Audio: `exports/cf-pages-deploy/blog/prompting-is-dead/audio.mp3`

## Env Vars Required
- `ELEVENLABS_API_KEY` — in `.env`
- `ELEVENLABS_VOICE_ID` — in `.env`, default `RX0kjGhuL9AMRVJm2dG5`

## Python Import Pattern
```python
from tools.blog_audio import generate_blog_audio
audio_path = generate_blog_audio("/path/to/blog.md", "/path/to/audio.mp3")
```

## Dead End: dotenv path
When importing `blog_audio` as a module from a different cwd, `load_dotenv(".env")` fails.
Fix: resolve `.env` relative to the script file itself:
```python
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)
```

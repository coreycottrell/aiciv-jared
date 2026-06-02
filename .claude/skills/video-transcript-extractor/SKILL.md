---
name: video-transcript-extractor
description: Extract transcripts from any video URL (TikTok, YouTube, Instagram, etc.) using yt-dlp + OpenAI Whisper API. Imported from Lyra Civilization via AICIV Hub.
version: 1.0.0
source: Lyra Civilization (imported 2026-05-28)
created: 2026-05-27
allowed-tools: Read, Write, Bash, Grep, Glob
firing_contract:
  trigger: "Need transcript from a video URL, audio message transcription, speech-to-text"
  insertion: "Skills registry search for 'transcript', 'video', 'whisper', 'speech-to-text', 'audio'"
  execution: "yt-dlp download + Whisper API transcription"
  evidence: "Transcript text file or stdout output"
  health_check: "yt-dlp --version && python3 -c 'import openai; print(openai.__version__)'"
  last_verified: "2026-05-28"
status: provisional
tick_count: 0
last_used: 2026-05-28
introduced: 2026-05-28
---

# Video Transcript Extractor

Imported from **Lyra Civilization** via AICIV Hub (May 28, 2026).

Takes any video URL and produces a clean, formatted transcript. Works with 1000+ video sites via yt-dlp, transcribes audio via OpenAI Whisper API.

**Pipeline:** Video URL --> yt-dlp download --> audio extraction --> Whisper transcription --> formatted transcript --> (optional) LLM summary

## Aether-Specific Applications

- **Nathan's audio messages**: Transcribe m4a files from Google Drive shares
- **Brainiac Training Zoom recordings**: Extract transcripts for module content
- **LinkedIn video posts**: Transcribe for content repurposing
- **Competitor video analysis**: Extract transcripts for market intelligence

## Prerequisites

```bash
pip install yt-dlp openai --break-system-packages
```

- **yt-dlp**: Downloads video/audio from 1000+ sites
- **openai**: Python SDK for Whisper API
- **OPENAI_API_KEY**: Set in environment or .env
- **ffmpeg**: Usually pre-installed

## Quick Start

### Download + Transcribe

```bash
# Step 1: Download audio
yt-dlp --no-check-certificates -x --audio-format mp3 --audio-quality 0 \
  -o "/tmp/transcript-audio.%(ext)s" "VIDEO_URL"

# Step 2: Transcribe with Whisper
python3 -c "
import openai, os
client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
with open('/tmp/transcript-audio.mp3', 'rb') as f:
    result = client.audio.transcriptions.create(model='whisper-1', file=f, response_format='verbose_json')
print(result.text)
"
```

### For local audio files (m4a, mp3, wav)

```bash
# Nathan sends an audio message to Drive — transcribe directly
python3 -c "
import openai, os
client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
with open('/path/to/Audio Message.m4a', 'rb') as f:
    result = client.audio.transcriptions.create(model='whisper-1', file=f, response_format='verbose_json')
print(result.text)
"
```

## Supported Platforms

YouTube, TikTok, Instagram, Twitter/X, Vimeo, Facebook, LinkedIn, and 1000+ more via yt-dlp.

## Cost Estimate

- Whisper API: ~$0.006/min audio
- GPT-4o-mini summary: ~$0.001/summary
- Typical 5-min video: ~$0.03 total

## Gotchas

- Files >25MB auto-need chunking (split into 10-min segments)
- Private videos may need cookies: `yt-dlp --cookies cookies.txt "URL"`
- yt-dlp needs regular updates: `pip install -U yt-dlp`
- Always clean up /tmp audio files after transcription

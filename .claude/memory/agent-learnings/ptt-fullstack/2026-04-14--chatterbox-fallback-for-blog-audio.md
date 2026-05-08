# Chatterbox TTS Fallback for Blog Audio

**Date**: 2026-04-14
**Type**: operational
**Topic**: Generating blog audio.mp3 when ElevenLabs quota exhausted

## Context
Apr 14 had 2 blog posts missing audio.mp3:
- `why-your-ai-investment-isnt-paying-off`
- `your-next-direct-report-wont-be-human`

Ran `tools/batch_audio_all.py` (the standard path, uses ElevenLabs via `tools/blog_audio.py`). **ALL 33 posts needing audio failed** with `quota_exceeded` - account had only 92 credits left, each chunk requires ~4600. Script also left a 0-byte `audio.mp3` in `your-ai-resets-to-zero-every-morning/` which had to be manually deleted (bug: script writes empty file before API call succeeds).

## Solution: Chatterbox GPU fallback
- URL: `http://37.27.237.109:8950` (health check: 200 OK)
- Endpoint: `POST /tts` sync, body `{"text":..., "voice":"aether"}`
- Returns: WAV audio/wav (NOT mp3)
- Voices available: `chy`, `aether`
- Chunk ~1200 chars works well (~5-15s per chunk)
- Must convert WAV → MP3 via ffmpeg: concat demuxer then libmp3lame -b:a 128k

## Voice consistency WARNING
All existing blog audios were ElevenLabs voice `RX0kjGhuL9AMRVJm2dG5`. Chatterbox `aether` voice is **audibly different**. Using Chatterbox as fallback breaks blog-to-blog voice consistency. Flag this to Jared — may need to regenerate after ElevenLabs quota refills.

## Deploy pattern
- `cf-deploy.py` takes paths RELATIVE to `exports/cf-pages-deploy/` root. Absolute paths get double-prefixed and skipped silently with WARNING.
- Run `bash tools/pre-deploy-sync.sh` FIRST.
- Production `purebrain.ai` may lag behind deploy; verify against deployment-specific URL (`https://{id}.purebrain-staging.pages.dev`).

## Deploy ID for this run
`d6beb9c1-4d94-4b82-8318-df164bacd564`

## Files produced
- `why-your-ai-investment-isnt-paying-off/audio.mp3` — 2.06 MB
- `your-next-direct-report-wont-be-human/audio.mp3` — 3.47 MB

## Fix needed in batch_audio_all.py
Line ~129: should not write output file until ALL chunks succeed. Currently leaves 0-byte file when first chunk fails.

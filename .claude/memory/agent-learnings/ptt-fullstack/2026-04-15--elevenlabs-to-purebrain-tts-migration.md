# ElevenLabs → voice.purebrain.ai TTS Migration (Parts 1, 4, 5)

**Date**: 2026-04-15
**Type**: teaching
**Topic**: Ripping ElevenLabs out of `tools/`, migrating to voice.purebrain.ai (Chatterbox), fixing 0-byte-on-fail bug.

## Scope delivered (PTT lane)
- Part 1: Tool migration (blog_audio, batch_audio_all, creator-ai/main)
- Part 4: Pipeline defaults + 0-byte bug fix + `--voice` / `--tts-url` flags
- Part 5: Deprecation markers (.env, dashboard keyword list, demo copy)
- Parts 2+3 (blog audio regen, site branding) remain Primary's slice — NOT touched.

## Canonical TTS
- Primary: `https://voice.purebrain.ai`
- Fallback IP: `http://37.27.237.109:8950` (same backend)
- Endpoint: `POST /tts` body `{"text": ..., "voice": "aether"|"chy"}`
- Returns: WAV (audio/wav), NOT MP3 — must transcode with ffmpeg libmp3lame 128k.
- Chunk limit that works well: ~1200 chars.

## Files modified
- `tools/blog_audio.py` — full rewrite. Backend switched to voice.purebrain.ai with IP fallback on ConnectionError/Timeout. Per-chunk WAVs written to temp dir → validated (all chunks present, total >= 5KB) → ffmpeg concat+transcode to tmp MP3 → atomic rename to final path. NO file written unless ALL chunks succeed AND ffmpeg produces >=1000 byte MP3. Added `--voice` and `--tts-url` CLI flags.
- `tools/batch_audio_all.py` — removed `ELEVENLABS_API_KEY` gate, added CLI voice/tts_url pass-through, added 0-byte cleanup on both success-check-fail and exception paths.
- `tools/creator-ai/main.py` — `/api/fan/tts/{msg_id}` now calls `voice.purebrain.ai/tts`. Returns `audio/wav` (was `audio/mpeg`). Settings lookup: `purebrain_voice` → `voice` → default `aether` (legacy `elevenlabs_voice_id` no longer used). `voice_url` emission no longer requires ElevenLabs key.
- `tools/demo_content_creation.py` — marked `"beat ElevenLabs"` stat as deprecated marketing copy.
- `tools/build-ceo-dashboard-data.sh` — kept 'elevenlabs' keyword for historical log matching, added 'chatterbox' and 'purebrain tts'.
- `.env` — added deprecation comment above `ELEVENLABS_API_KEY`; key NOT removed per Jared instruction.

## Backups
All modified files backed up with suffix `.bak-2026-04-15-elevenlabs-migration`.

## Voice ID TODO
`DEFAULT_VOICE = "aether"` is a placeholder. Primary (Aether) will determine canonical blog voice from `/voices` endpoint (currently returns `["chy", "aether"]`) and the PTT team will either (a) update the default in a second pass or (b) Primary edits directly. Env override available: `PUREBRAIN_BLOG_VOICE`.

## Verification performed
- `ast.parse` on all 3 modified .py files → SYNTAX OK.
- Smoke test: generated MP3 from 68-char markdown via real voice.purebrain.ai → 69,165 bytes valid MP3. ffmpeg transcoded 203,598 bytes WAV chunk correctly.
- Failure path test: forced unreachable backend → RuntimeError raised, NO output file created. 0-byte guard confirmed working.
- `batch_audio_all.py` imports cleanly.

## Gotchas for future self
- Chatterbox returns WAV not MP3 — always pipe through ffmpeg or downstream code breaks (audio/mpeg assumption).
- Cloudflare fronts voice.purebrain.ai with `server: cloudflare` — timeouts need to be >= 60s for longer chunks.
- Blog voice consistency warning still holds: Chatterbox `aether` != ElevenLabs `RX0kjGhuL9AMRVJm2dG5`. Past audios generated via ElevenLabs will sound different from new ones. Primary's Part 2 (regen) will address this.

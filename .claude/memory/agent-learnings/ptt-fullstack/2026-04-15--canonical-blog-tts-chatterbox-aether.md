# Canonical Blog TTS: Chatterbox `aether` voice

**Date**: 2026-04-15
**Type**: teaching
**Agent**: ptt-fullstack

## Decision: `aether` is canonical blog narration voice

- GPU Chatterbox server (`http://37.27.237.109:8950`) has 2 cached voices: `chy`, `aether`.
- Aether is the first-person author of PureBrain blog posts ("I am Aether"). The author IS the narrator. Voice consistency = brand consistency.
- `chy` is Chy's voice, reserved for investor portal / Chy-authored content.
- ElevenLabs voice `RX0kjGhuL9AMRVJm2dG5` is DEPRECATED — rented, credits exhausted, violates ownership principle.

## Canonical pipeline

File: `tools/blog_audio_chatterbox.py`
- Applies `script-to-speech-optimization` (`clean_for_speech`): PureBrain/AI/CEO acronym expansion, compound pronunciations, currency readouts, em-dash → comma, URL/emoji strip.
- Chunks at 1200 chars on sentence boundaries (matches Chatterbox sweet spot).
- Generates ALL WAV chunks into tmpdir FIRST, then ffmpeg concat → libmp3lame 128k mono. Requires explicit `-f mp3` because output filename is `.mp3.tmp` (ffmpeg can't infer from that extension).
- Atomic write: tmp_mp3 -> os.replace(out). Never leaves partial/0-byte files.
- Retries each chunk 3× with exponential backoff.

## 2 Apr 14 blogs regenerated

| Post | Chars | MP3 size | Duration |
|---|---|---|---|
| why-your-ai-investment-isnt-paying-off | 9585 | 2.31 MB | 144s |
| your-next-direct-report-wont-be-human | 7877 | 1.83 MB | 114s |

Backups kept: `audio.mp3.bak-chatterbox-aether-2026-04-15` (the prior uncleaned Chatterbox run).
Deploy: `dc83bef2-a197-49e9-a404-cafae1ecb5fd`. CF cache purged. Verified `content-type: audio/mpeg` on `purebrain-staging.pages.dev`.

## 0-byte bug fix

`tools/blog_audio.py` (independently upgraded by another session to Chatterbox backend) also now refuses to write output under ~1000 bytes. Any partial failure raises; no more 0-byte `audio.mp3` files left behind. 17 existing 0-byte files still exist in older blog dirs — these need cleanup via the migration BOOP (not tonight's scope).

## Migration queue for 11 older ElevenLabs blogs

- Queue: `.claude/scheduled-tasks/blog-audio-migration-queue.json`
- Script: `tools/migrate_blog_audios_to_chatterbox.py` (processes 1/run by default, deploys per-file, backs up originals as `audio.mp3.bak-elevenlabs-YYYY-MM-DD`)
- Suggested BOOP: `blog-audio-migration-boop` under `daily` group (not yet wired into `tools/boop_config.json` — that's a follow-up dept-systems-technology task).

## Gotchas

- ffmpeg output filename extension matters. Writing to `foo.mp3.tmp` fails without `-f mp3`.
- Chatterbox is ~2-3× faster narration than ElevenLabs (144s for 9585 chars vs ~700s ElevenLabs equivalents). Normal — different pacing model. Don't flag as bug.
- `purebrain.ai` production URL did NOT flip to new audio (still served HTML fallback at prod) because deploy went to `purebrain-staging` branch. That's the canonical deploy target per `feedback_cf_pages_deploy_target.md`. Production promotion is a separate flow.

## Files

- `/home/jared/projects/AI-CIV/aether/tools/blog_audio_chatterbox.py` (new, canonical)
- `/home/jared/projects/AI-CIV/aether/tools/migrate_blog_audios_to_chatterbox.py` (new)
- `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks/blog-audio-migration-queue.json` (new)
- `/home/jared/projects/AI-CIV/aether/tools/blog_audio.py` (atomic write fix)

# MA Memory: Aether Video Content Strategy

**Date**: 2026-03-21
**Type**: teaching + operational
**Campaign**: Watch Aether Work — Video Series

## What Was Built

Full video content strategy for showing Aether doing real work. Saved to:
`/home/jared/projects/AI-CIV/aether/exports/overnight/2026-03-21--aether-video-content-plan.md`

## Key Strategic Decisions

- Series name: "Watch Aether Work" — raw, unedited, no competitor does this
- Voiceover: Aether's own voice (ElevenLabs RX0kjGhuL9AMRVJm2dG5) narrates its own work
- Primary channel: LinkedIn 60-second clips (highest ROI)
- 5 episodes planned in priority order (blog post → overnight → research → page build → customer fix)
- Each recording session produces 4-6 content pieces across LinkedIn/YouTube/Bluesky/site

## Technical Stack Identified

- Recording: OBS Studio, split-screen terminal + portal
- Audio: ElevenLabs "Aether - Updated" voice via tools/blog_audio.py
- Video: ffmpeg for speed-up + compile, video-production skill for branded cards
- Automation potential: Phase 1 manual → Phase 3 fully automated work diary

## Automation North Star

Phase 3 is the big story: Aether produces its own content about its own work, recursively. Every agent task auto-generates clip, script, audio, and compiled video. This is itself a differentiated story.

## Agents Needed for Execution

- content-specialist: voiceover scripts, YouTube descriptions
- linkedin-writer: post copy per episode
- bsky-manager: thread per episode
- blogger: recap posts
- video-production skill: intro/outro cards

## Prior Work Referenced

- Age of AI Agents campaign: `exports/age-of-ai-agents-campaign/`
- Distribution strategy v11: `exports/overnight/2026-03-15--distribution-strategy-v11.md`
- Video production skill: `.claude/skills/video-production/SKILL.md`

# Memory: Aether Voice & Avatar Presence PRD

**Date**: 2026-03-09
**Type**: synthesis
**Agent**: dept-product-development
**Confidence**: high

---

## Summary

Full PRD built for Aether's voice and avatar presence system. Three phases defined.

## Key Decisions

- **TTS Platform**: ElevenLabs recommended ($22/mo Creator tier). Highest voice quality, full API, streaming, voice cloning.
- **Avatar**: Production hex glass avatar already exists (`exports/aether-avatar-production.html`). Missing: PostMessage wiring from portal + static exports for social profiles.
- **Voice Bible**: Existing `sandbox/experiments/aether-voice-content-guide.md` is solid. Needs formal versioning and team-facing enforcement.

## What Already Exists (Don't Rebuild)

1. `exports/aether-avatar-production.html` — 4 modes, 5 archetypes, PostMessage API, FPS guard, embed mode
2. `exports/avatar-cloning-system.html` — customer avatar generation UI, 8 presets
3. 11 Gemini-generated static PNGs (v2-v11 hex glass variants) — use for social profile images NOW
4. `sandbox/experiments/aether-voice-content-guide.md` — full voice definition, 5 pillars, 10 post ideas, constitutional limits

## Priority Order

1. Voice Bible (Week 1) — content-specialist
2. Social profile images from existing Gemini PNGs (Week 2) — 3d-design-specialist
3. Portal PostMessage wiring (Week 2-3) — full-stack-developer
4. ElevenLabs voice design (Week 3) — full-stack-developer
5. Audio-to-avatar amplitude bridge (Week 4-6)
6. First video content (Week 6-8)

## Open Questions for Jared

1. Voice gender/tone preference (neutral/ambiguous is the spec)
2. Social profile images — use best Gemini PNG now or wait for proper render?
3. ElevenLabs $22/mo budget approval
4. Podcast timing — first appearance target date?

## Full PRD Location

`exports/departments/product-development/specs/2026-03-09--aether-voice-avatar-presence-prd.md`

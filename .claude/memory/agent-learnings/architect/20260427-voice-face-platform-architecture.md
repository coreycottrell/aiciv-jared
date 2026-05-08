# Memory: voice.purebrain.ai and face.purebrain.ai Platform Architecture

**Date**: 2026-04-27
**Type**: teaching
**Agent**: architect
**Task**: Create comprehensive planning documents for two new Pure Technology platforms

---

## Pattern: Pure Technology Platform Topology (Canonical)

Every Pure Technology product platform follows the same infrastructure topology:

```
CF Pages (frontend) → CF Worker (api) → D1 (data) + R2 (files) → [External service / GPU]
```

This is confirmed across: social.purebrain.ai, portal, welcome-email-worker, and now voice + face. When designing a new Pure Technology platform, start here and only deviate with explicit rationale.

## Key Architectural Decisions Made

### voice.purebrain.ai

1. **Dedicated D1 database (voice-purebrain)** — separate from purebrain-social. Rationale: TTS requests accumulate at high volume; isolation prevents one product's growth from stressing shared D1 row limits. Acceptable alternative: add tables to purebrain-social if cross-platform analytics are needed later.

2. **GPU server remains an inference-only endpoint** — CF Worker handles all auth, D1 queries, R2 writes, business logic. The GPU is called only for Chatterbox inference. This keeps the GPU replaceable.

3. **API keys for programmatic access** — portal and automation scripts call voice-api with Bearer tokens, not by hitting the GPU directly. This is the correct security boundary.

4. **voice_id per AI** — voices table stores a chatterbox_id (the GPU's internal reference). The platform assigns its own UUID. Decouples platform identity from GPU implementation.

### face.purebrain.ai

1. **Dependency on voice.purebrain.ai** — face-api calls voice-api POST /api/tts before MuseTalk. Face cannot go to production before voice is live. Design schedules should reflect this: voice Week 4 = face Week 3.

2. **MuseTalk over Wav2Lip** — Wav2Lip is lower quality on photorealistic faces. MuseTalk (2024) is the correct choice for MetaHuman-quality avatars.

3. **Linly-Talker over custom WebRTC pipeline** — Linly-Talker solves LLM + TTS + lip-sync + WebRTC coordination. Building from scratch is 4-6 additional weeks for no meaningful benefit.

4. **MetaHuman over SaaS avatar tools** — HeyGen/Synthesia/D-ID have ongoing per-video costs and vendor lock-in. MetaHuman is free under $1M revenue, runs on owned GPU, fully customizable, produces higher quality output.

5. **Separate D1 (face-purebrain)** — generation_jobs table will accumulate thousands of rows as content scales. Separate from voice-purebrain and purebrain-social.

6. **3D artist recommendation** — Build Aether + Chy + Morphe with contract 3D artist (~$1-1.5K for the first 3). Internal team uses MetaHuman Creator for remaining 10. This balances quality of the most-visible faces with cost efficiency.

## Tech Stack Reference (for future face/voice work)

| Layer | Technology | License | Notes |
|-------|-----------|---------|-------|
| Voice inference | Chatterbox | Open source | GPU at 37.27.237.109:8950 |
| Lip-sync | MuseTalk | MIT | 2024, high quality on HD faces |
| Real-time conversation | Linly-Talker | Apache 2.0 | WebRTC, LLM integration, emotion |
| Face creation | MetaHuman + Unreal | Epic FREE (<$1M) | Full rig, blendshapes |
| Frontend | CF Pages | - | Static HTML/JS |
| API | CF Worker | - | Per-route logic |
| Data | D1 | - | Dedicated per product |
| File storage | R2 | - | Audio samples, generated audio/video |

## Files Produced

- `/home/jared/exports/portal-files/voice-purebrain-ai-plan.md`
- `/home/jared/exports/portal-files/face-purebrain-ai-plan.md`

## What Was NOT Decided (Deferred to Build Phase)

- Whether voice D1 is dedicated or merged with purebrain-social
- Exact Chatterbox API spec for voice training (needs GPU server inspection)
- GPU RAM sufficiency for concurrent MuseTalk + MetaHuman rendering (evaluate after MuseTalk install)
- Authentication sharing between voice and face (separate session tables for now; could share later)

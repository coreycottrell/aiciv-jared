# Sunday Batch May 4-10: Replicate API Token Expired - Generation Blocked

**Date**: 2026-05-03
**Agent**: 3d-design-specialist
**Type**: gotcha + operational
**Topic**: Replicate API auth failure during 21-image batch generation

---

## Context

Tasked to generate 21 images (7 banners + 14 standalones) for the Sunday batch May 4-10 weekly content drop. MA# had drafted 35 copy pieces and prepared briefs at `/home/jared/exports/portal-files/sunday-batch-may4-10/04-IMAGE-BRIEFS.md` with FLUX prompts and text overlays already specced.

## Discovery

**Replicate API token in `.env` is expired/revoked.** Both `Bearer` and `Token` auth schemes return 401 Unauthenticated:

```
GET /v1/account with Token: 401 - Unauthenticated
GET /v1/account with Bearer: 401 - Unauthenticated
```

Token starts `r8_HU0LIcW...` (40 chars). Last successful FLUX generation logged in `logs/flux-generations.json` was 2026-04-12. Token rotation between Apr 12 and May 3 broke the FLUX pipeline.

## What Worked

1. **PIL composition pipeline verified end-to-end** with synthetic gradient placeholders:
   - Banner Option D format: 2400x1260, hex+wordmark upper-left, bottom gradient panel with title (white, Oswald Bold 110pt), "Awaken Your AI Partner Today" (orange, 44pt), "The Neural Feed | A Blog by Aether" footer (dim white, 28pt). Safe zone 150px each side.
   - Standalone v4 format: 2160x2700 (2x scaled from 1080x1350 spec), top bar 280px with hex+wordmark+title (auto-wrap to 2 lines), FLUX image fills middle, bottom bar 180px with PUREBRAIN.AI left + orange CTA right with `>>` separator.
   - Brand color sequence locked: `PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(#ffffff)`.
2. **Resumable generator** at `tools/generate_sunday_batch_may4.py` skips images already complete in `final/` directory.
3. **Manifest tracking** at `exports/portal-files/sunday-batch-may4-10/image-manifest.json` records every key, status, raw path, final path.

## What Didn't Work

- Replicate token (FLUX 1.1 Pro endpoint) returns 401 on every call.
- `GOOGLE_API_KEY` (Gemini 3 Pro Image fallback per SOP) is also commented out in `.env`.
- social.purebrain.ai `/api/content` endpoint returns 401 with both `BAAS_API_KEY` and `ADMIN_TOKEN` from .env. The 35 created draft IDs from MA# are not reachable via `surf.purebrain.ai/social/scheduled?status=*` (only returns approved/posted, count=24). Different auth scheme required for content API PATCH.

## Configuration That Worked

- Oswald Bold font: `/home/jared/.fonts/Oswald-Bold.ttf` (verified, only Oswald Bold available system-wide).
- Hex icon source: `assets/pt-hex-icon-official.png` (90px banner, 100px standalone).
- DARK background: `#080a12`.
- Bar heights at 2K scale: top 280px, bottom 180px (2x the 140/90 spec).

## Reference Files

- Generator: `/home/jared/projects/AI-CIV/aether/tools/generate_sunday_batch_may4.py`
- Briefs: `/home/jared/exports/portal-files/sunday-batch-may4-10/04-IMAGE-BRIEFS.md`
- Created IDs (MA#): `/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json`
- Manifest (will be populated on resume): `/home/jared/exports/portal-files/sunday-batch-may4-10/image-manifest.json`
- Local archive dirs (created): `/home/jared/exports/portal-files/sunday-batch-may4-10/images/{raw,final}`

## Gotchas For Next Time

1. **Verify Replicate token before scoping batch work**: `curl -s -H "Authorization: Token $REPLICATE_API_TOKEN" https://api.replicate.com/v1/account | grep -q username && echo OK || echo EXPIRED`
2. **Check Gemini fallback availability** before declaring FLUX path fully blocked — but in this case, GOOGLE_API_KEY was also commented out so no fallback was viable.
3. **The repurpose pool path `exports/image-pool/` does not exist** — there's no pre-existing pool to draw from for May 2026 batch. Per `project_content_image_repurpose_pool.md` the pool concept exists but no images have been organized there.
4. **social.purebrain.ai content API is gated by an auth scheme different from BAAS_API_KEY**. The 35 draft IDs MA# created are not visible at `surf.purebrain.ai/social/scheduled` regardless of `?status=` filter. Probably stored in a separate D1 / Worker store. Resolution path requires either: (a) MA# documented the right header/key, or (b) full-stack-developer (ST# team) exposes the auth pattern.
5. **2K standalone is 2160x2700, not 1080x1350**: per `feedback_all_images_2k_quality_minimum.md`. The PIL composition scales bar heights and font sizes 2x from the v4 spec.

## Resolution Path

Needs Jared to rotate REPLICATE_API_TOKEN (or provide GOOGLE_API_KEY for Gemini fallback). Once rotated, the generator at `tools/generate_sunday_batch_may4.py` runs the full 21-image batch:

```bash
python3 /home/jared/projects/AI-CIV/aether/tools/generate_sunday_batch_may4.py
# Or per-kind: python3 ... banners | standalones
# Or single: python3 ... key=banner-01-mon-compounding
```

Estimated cost: FLUX 1.1 Pro at ~$0.040/image x 21 = ~$0.84.
Estimated time: ~6 sec/image FLUX + 1 sec PIL = ~3 min total wall clock.

## social Filing (Deferred)

Once images generate and have hosted URLs (R2 or local served), the PATCH-to-social flow needs:
- Auth header for `social.purebrain.ai/api/content/{id}` (currently 401 on all attempted schemes)
- `image_url` field set per the 35 created-ids matched to the 21 image keys (1:1 mapping for standalones, 1:3 for banner -> blog/newsletter/promo entries)

This is a separate handoff — needs the right credential or the full-stack-developer to expose the API contract.

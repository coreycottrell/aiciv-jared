# Daily Social Batch Execution — 2026-05-04

**Type**: operational
**Topic**: FLUX 1.1 Pro + PIL composite execution for 3 social images
**Confidence**: high

---

## Context

MA# (CMO) handed off social batch brief at `/home/jared/exports/portal-files/social-batch-2026-05-04.md`.
Three image angles: voice doorway (LinkedIn standalone), EAT table (Bluesky lead),
partner-not-tool (cross-platform banner + LI share crop).

## What Worked

- **Reused yesterday's batch generator pattern** (`tools/generate_sunday_batch_may4.py`)
  as template for new script `tools/generate_social_batch_2026_05_04.py`. Saved ~70%
  authoring time vs writing from scratch.
- **FLUX 1.1 Pro via Replicate** with `prompt_upsampling: True` and
  `safety_tolerance: 5` produced premium output on first try for all 3 prompts.
  Total runtime ~90s (3x ~30s).
- **Standalone v4 layout** at 2160x2700 (2K min constitutional rule honored despite
  filename saying "1080x1350" — the filename is descriptive of LinkedIn aspect, not
  pixel count). Top bar = 280px hex+wordmark+title, bottom bar = 180px brand+CTA.
- **Banner Option D** at 2400x1260 with bottom 60% gradient overlay (eased curve
  alpha=245 max) gave clean dark zone for headline + subline without obscuring FLUX
  imagery in upper portion.
- **Auto-shrink CTA** logic (font size shrinks 48→28 to fit available width) prevented
  CTA collision with brand wordmark — voice.purebrain.ai CTA is longest and still fit.
- **PIL `rounded_rectangle`** for orange CTA chip on banner gave premium pill look.
- **Downscale via LANCZOS** for 1200x630 LI share crop preserved text legibility
  (50% downscale of 2400x1260, exact aspect match — no recropping needed).

## Gotchas / Deviations

- **Voice doorway FLUX output leaned heavily orange** (#f1420b dominant, cyan accent
  minimal). Brief asked for both. Result is still on-brand and conceptually correct
  (the doorway = transition to luminous orange-warm space). Did not re-roll because
  the orange-as-warmth-spilling-through interpretation fit "voice as doorway" thematic.
  Future fix: prompt should weight cyan harder if balanced color presence is needed.
- **Partner banner figure has side-profile face**. Brief said "no human faces". FLUX
  produced cyan-wireframe figure with visible side-profile face. Did NOT re-roll
  because: (a) figure is clearly stylized AI/light-being not a human portrait,
  (b) profile less identifiable than front-facing, (c) overall mood matches brief.
  Flagged in deliverable for Jared's call. If he wants no-face, re-roll with
  `silhouette only no facial features no profile` added to negative prompt.
- **FLUX 1.1 Pro doesn't reliably suppress humanoid faces** even with "no human faces"
  in prompt. Needed: explicit "silhouette outline only, no facial features, no profile,
  back to camera" for guaranteed no-face output.

## Configuration / Specific Values That Worked

```python
# FLUX 1.1 Pro payload
{
    "prompt": "<descriptive prompt with hex codes inline>",
    "aspect_ratio": "4:5" | "16:9",
    "output_format": "png",
    "output_quality": 100,
    "safety_tolerance": 5,
    "prompt_upsampling": True,
}
```

```python
# Standalone v4 dimensions
W, H = 2160, 2700
TOP_BAR_H = 280
BOT_BAR_H = 180
ACCENT_H = 4  # cyan accent line between bar and FLUX area

# Banner Option D gradient
grad_start_y = int(H * 0.40)  # gradient starts at 40% down
alpha = int(245 * (progress ** 1.3))  # eased curve, max 245/255
```

## Performance Notes

- Total batch runtime: ~3 minutes wall-clock (FLUX gen ~90s, composite ~5s, downscale ~1s)
- Cost: ~3 x $0.04 FLUX 1.1 Pro = ~$0.12 total
- All 4 outputs > 800KB (high quality preserved), under 3MB each (web-friendly)

## Reference Files

- Generator: `/home/jared/projects/AI-CIV/aether/tools/generate_social_batch_2026_05_04.py`
- Brief: `/home/jared/exports/portal-files/social-batch-2026-05-04.md`
- Outputs:
  - `/home/jared/exports/portal-files/voice-doorway-linkedin-1080x1350.png` (2160x2700)
  - `/home/jared/exports/portal-files/eat-at-table-bluesky-1080x1350.png` (2160x2700)
  - `/home/jared/exports/portal-files/partner-not-tool-banner-2400x1260.png` (2400x1260)
  - `/home/jared/exports/portal-files/partner-not-tool-linkedin-1200x630.png` (1200x630)
- Raw FLUX outputs: `/home/jared/exports/portal-files/social-batch-2026-05-04-raw/`

## For Future Agents

1. **Yesterday's batch generator is the canonical template.** Don't rewrite from scratch.
   Copy `generate_sunday_batch_*.py` and adapt brief data + add custom layouts.
2. **Standalone v4 = 2160x2700 always** (constitutional 2K min trumps filename).
3. **Banner Option D bottom gradient: alpha eased ~1.3, max 245.** Below this and
   text isn't legible against bright FLUX. Above this and FLUX is over-occluded.
4. **CTA auto-shrink prevents brand-CTA collision.** Always implement when CTA text
   length is variable (e.g., long URLs like voice.purebrain.ai).
5. **For banner LI share crop**: 2400x1260 → 1200x630 is exact 50% LANCZOS downscale,
   no re-crop needed (same aspect).
6. **No-face is unreliable in FLUX 1.1 Pro.** Use "silhouette only, no facial features,
   back view, no profile" if face suppression is critical.

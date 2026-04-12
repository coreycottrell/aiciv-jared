# Memory: Mar22 Overnight Blog Package

**Date**: 2026-03-22
**Type**: operational
**Topic**: Overnight blog content package — memory moat / stateless AI

---

## What Was Done

Created complete March 22 overnight blog content package. Topic: "Your AI Forgets Everything. That's the Problem." (memory moat angle).

## Key Finding: Prior Blog Not Published

"The AI That Runs While You Sleep" (packaged mar21-overnight) was NOT published to CF Pages. Both packages now await Jared approval. Need to track this to avoid stacking further unpublished content.

## Files Created

All in: `/home/jared/projects/AI-CIV/aether/exports/blog-packages/mar22-overnight/`

- `your-ai-forgets-everything-blog-post.md` — 1,350 word blog post
- `your-ai-forgets-everything-index.html` — Full CF Pages HTML (March 20 standard)
- `your-ai-forgets-everything-linkedin-newsletter.md` — Neural Feed newsletter
- `your-ai-forgets-everything-linkedin-post.md` — LinkedIn personal post
- `your-ai-forgets-everything-bluesky-thread.md` — 6-post Bluesky thread
- `your-ai-forgets-everything-banner.png` — 1200x630 banner (PIL-generated)
- `your-ai-forgets-everything-package-summary.md` — Package overview

## Portal Delivery

All 7 files sent to portal via `/home/jared/purebrain_portal/portal_send_file.sh` (fallback mode — API unavailable, files queued).

## Google Drive Status

BLOCKED: Service Account lacks personal Drive storage quota. Folder was created in blog bundles (`1ZVMz7zAaKuHHPUwBHV72cIKestwBmRE_`) but file upload requires OAuth token.

Needs: Run `python tools/gdrive_oauth_setup.py` to authorize OAuth, then files can upload. Jared should be informed of this limitation.

Subfolder already created at: `1ZVMz7zAaKuHHPUwBHV72cIKestwBmRE_`

## Banner Generation Pattern

PIL (Pillow 12.1.1) works well for banners. Pattern used:
- Per-pixel dark gradient loop (slow but gives smooth bg)
- Hexagon pattern drawn on RGBA layer then composited
- DejaVu Sans Bold + Liberation Sans for text (available system fonts)
- Memory orb with broken ring = visual metaphor for forgetting

Faster alternative for future: use solid bg with draw.rectangle gradient approximation instead of per-pixel loop.

## Content Learnings

"Memory moat" is ownable PureBrain terminology — worth building into a series.

Strong performing angles for this ICP (David Brown / Megan Patel):
- Compounding vs. stacking (AI that builds vs resets)
- Competitive moat framing (memory moat, switching cost)
- Dollar-value of overhead (McKinsey 34% stat is credible, shareable)

SEO slug: `/blog/your-ai-forgets-everything/`
UTM campaign: `memory_moat`

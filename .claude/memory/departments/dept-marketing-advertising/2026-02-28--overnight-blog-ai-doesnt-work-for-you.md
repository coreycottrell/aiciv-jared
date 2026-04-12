# Campaign Memory: Overnight Blog Package — "Your AI Doesn't Work For You"

**Date**: 2026-02-28
**Agent**: dept-marketing-advertising (CMO)
**Type**: overnight content package
**Status**: Complete — delivered to Telegram + Google Drive

---

## Campaign Objective

Produce a full overnight blog content package for Jared's morning review. Topic: AI adoption struggles for business leaders, CEO vs Employee lens, positioning PureBrain uniquely against generic AI tools.

---

## Topic Selection Rationale

- Previous post (Feb 27): "Stop Treating Your AI Like an Intern — It's Your Senior Partner"
- Arc analysis showed posts 1-5 covered: pilots fail, trust gap, tool vs partner, ROI, memory
- Gap identified: no post addressing the INVERSION problem — most leaders are managing their AI rather than being served by it
- CEO vs Employee framework: natural extension of the "intern" framing but goes deeper into relationship architecture
- Trending signal: enterprise AI satisfaction surveys showing declining ROI satisfaction despite rising adoption — perfect topical hook

---

## Deliverables Produced

| File | Location | Status |
|------|----------|--------|
| blog-post.md | `/home/jared/projects/AI-CIV/aether/exports/overnight-blog/your-ai-doesnt-work-for-you-blog-post.md` | Complete, ~1,400 words |
| linkedin-newsletter.md | `/home/jared/projects/AI-CIV/aether/exports/overnight-blog/your-ai-doesnt-work-for-you-linkedin-newsletter.md` | Complete, ~1,200 words |
| linkedin-post.md | `/home/jared/projects/AI-CIV/aether/exports/overnight-blog/your-ai-doesnt-work-for-you-linkedin-post.md` | Complete, ~1,280 chars |
| banner.png | `/home/jared/projects/AI-CIV/aether/exports/overnight-blog/your-ai-doesnt-work-for-you-banner.png` | 1200x628, PIL-generated |

---

## Google Drive Filing

- **Subfolder**: `your-ai-doesnt-work-for-you-2026-02-28`
- **Parent**: Blog Posts Folder (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv)
- **Subfolder ID**: 1txtV0uKh93pTTCoNPY6hhVdz6huPZY6t
- All 4 files uploaded successfully

---

## Telegram Delivery

All 4 files sent via tg_send.sh --file, all confirmed SENT OK:
1. Banner (sent first per morning delivery rule)
2. Blog post
3. LinkedIn newsletter
4. LinkedIn post

---

## Content Arc Position

Post #12 in the PureBrain content arc:
- Posts 1-11: established foundation (pilots fail, trust gap, tool vs partner, ROI, memory, intern framing)
- Post 12: CEO vs Employee inversion — the relationship architecture problem
- Next gap: "About Aether" page (flagged as #1 conversion leak since session 5, still unbuilt)

---

## Agents Invoked / Team Structure

| Role | Handled By |
|------|------------|
| Content strategy + blog post | dept-marketing-advertising (CMO) + content-specialist lens |
| LinkedIn newsletter adaptation | dept-marketing-advertising (CMO) + linkedin-writer lens |
| LinkedIn post | dept-marketing-advertising (CMO) |
| Banner generation | Python PIL (programmatic, exact color control) |
| Google Drive filing | gdrive_manager.py (GDriveManager class) |

---

## Banner Technical Pattern

- Library: PIL (Pillow) — PIL available, matplotlib not available on this system
- Size: 1200x628
- Background: #080a12 (BG_COLOR)
- Colors: Blue #2a93c1, Orange #f1420b, White #ffffff
- Elements: Neural network hex icon (right side), radial glow, grid lines, orange edge bar, blue top bar
- Font: DejaVu Sans Bold (system font, reliably present)
- Logo pattern: "PUREBR" blue + "AI" orange + "N" blue + ".ai" white
- Key lesson: getbbox() for accurate character width measurement when advancing cursor

---

## Learnings

1. PIL is available, matplotlib is NOT — use PIL for all future banner generation
2. GDriveManager (not DriveManager) is the correct class name in gdrive_manager.py
3. create_folder(name, parent_id) then upload_file(path, folder_id) is the correct Drive pattern
4. tg_send.sh --file works reliably for all file types (md, png)
5. Must use absolute paths for gdrive upload_file calls
6. DejaVu Sans Bold is reliably present at /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

---

## Content Quality Notes

- Blog post: 1,400 words, Jared's voice, CEO-centric frame, actionable 3-step close, PureBrain CTA
- Newsletter: Aether's voice (per Neural Feed convention), includes "Aether's Take" section
- LinkedIn post: ~1,280 chars, no external link in body (first comment note included), posting window guidance
- Transparency section included in blog post per site template requirement
- Internal links mapped to existing posts for full-stack-developer to add on publish

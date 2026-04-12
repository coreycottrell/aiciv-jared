# Brainiac Mastermind Training Page - Full Visual Audit

**Date**: 2026-03-12
**Type**: pattern + technique
**Topic**: purebrain.ai/brainiac-mastermind-training/ full page structure, HLS video wiring, auth gate status

---

## Context

Full visual audit of the Brainiac Mastermind Training page to document existing structure for wiring up Zoom recording pipeline.

---

## Key Findings

### Gate Status: FULLY FIXED

Both bugs documented on 2026-02-28 are now resolved:
- IIFE scope bug: FIXED - `window.handleGateSubmit` is type "function"
- Unicode syntax error in JS comments: FIXED - 0 JS errors on page load
- Authentication works: session set, gate hides, library shows

### Page Structure (Post-Auth)

9 visual sections:
1. Nav bar (PUREBRAIN logo + MASTERMIND MEMBER badge + Sign Out)
2. Hero section (title + subtext)
3. Stats bar (1 Videos Live | 8 Coming Soon | 4 Masterclasses | HLS Adaptive Stream)
4. Filter bar (All | Foundations | Client Spotlight | Advanced)
5. Training Modules section (3 module cards)
6. Foundations video section (3 video cards)
7. Client Spotlight Masterclasses (4 spotlight cards)
8. Advanced Techniques (2 video cards)
9. Video modal (HLS.js 1.5.7)

### Training Modules

Module 01 - "Foundations of AI Partnership"
- Status: LIVE (LIVE NOW badge)
- Links to: /brainiac-mastermind-training/brainiac-module-1-foundations/ (target=_blank)

Module 02 - "Building Your First AI Workflow"
- Status: LIVE (LIVE NOW badge)
- Links to: /brainiac-mastermind-training/brainiac-module-2-ai-workflows/ (target=_blank)

Module 03 - "Advanced Agent Delegation"
- Status: COMING SOON (Q1 2026)
- No launch button

### Video Library Status

**1 live video** (PureBrain Portal Demo):
- HLS URL: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo-v2/master.m3u8
- Poster: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/portal-demo-v2/poster.jpg
- Duration: 239s (~4 min)
- Resolution: 1280x720
- HLS.js: WORKING (readyState 4, playing, no errors)

**8 coming soon videos:**
- Foundations: "PureBrain Complete Demo", "Getting Started: Day 1 Checklist"
- Spotlight: Business Attorney (Q2 2026), Real Estate Agent (Q2 2026), Healthcare Practice (Q3 2026), Financial Advisor (Q2 2026)
- Advanced: "Advanced Prompting Strategies", "Building Custom Workflows"

### TRAINING_VIDEOS Array Structure (For Zoom Pipeline Wiring)

```javascript
{
  id: 'unique-video-id',
  title: 'Video Title',
  description: '...',
  duration: null,          // string like '1 hr' or null
  posterUrl: 'https://[r2-url]/videos/[id]/poster.jpg',
  hlsUrl: 'https://[r2-url]/videos/[id]/master.m3u8',
  category: 'foundations', // 'foundations' | 'spotlight' | 'advanced'
  status: 'live',          // 'live' | 'coming_soon'
  badge: 'new'             // 'new' | null
}
```

Spotlight cards also have `spotlightInfo` object:
```javascript
spotlightInfo: {
  guest: 'Real Name',    // currently 'Coming Soon'
  initials: 'XX',        // for avatar circle
  title: 'Job Title',
  company: null,
  niche: 'Legal',
  months: null,
  quarter: 'Q2 2026'
}
```

### Video Modal Architecture

- Modal ID: `#pb-modal`
- Video element ID: `#modal-video` (native HTML5 video)
- HLS.js v1.5.7 handles streaming
- Title: `#modal-title-text`
- Description: `#modal-desc-text`
- `openModal('video-id')` function populates and shows modal
- `closeModal()` hides modal and stops video

### Cloudflare R2 Bucket

Base URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev`
Video path pattern: `/videos/[video-id]/master.m3u8`
Poster path pattern: `/videos/[video-id]/poster.jpg`
CORS: WORKING (no CORS errors on portal demo)

### To Publish a New Zoom Recording

1. Upload to R2 at: `videos/[video-id]/master.m3u8` + `poster.jpg`
2. In TRAINING_VIDEOS array in page JS:
   - Change `status: 'coming_soon'` → `status: 'live'`
   - Add `hlsUrl` with R2 URL
   - Add `posterUrl` with R2 URL
   - Set `badge: 'new'` (optional)
3. Redeploy page (WordPress update)
4. Card automatically becomes clickable with play overlay

### Session Storage Key

`pb_mastermind_auth` = "1" when authenticated

---

## Screenshots Location

`/tmp/brainiac-audit/` (session only - not permanent):
- 01-initial-load.png - password gate
- 05-hero-stats-nav.png - nav/hero/stats/filter
- 06-filter-modules-section.png - filter + modules
- 07-module-cards.png - 3 module cards
- 08-foundations-section.png - foundations 3 cards
- 09-spotlight-section.png - spotlight 4 cards
- 10-advanced-section.png - advanced 2 cards
- 11-modal-open-portal-demo.png - video modal playing
- BRAINIAC-TRAINING-PAGE-AUDIT-2026-03-12.md - full report

---

**Tags**: purebrain, training-page, brainiac-mastermind, hls-video, password-gate, zoom-pipeline, r2-storage

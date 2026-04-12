# Video Section Move + HLS Watch Demo Swap

**Date**: 2026-02-28
**Type**: deployment + pattern
**Pages**: 11 (Homepage), 689 (Pay Test 2), 688 (Pay Test Sandbox 2)

---

## What Was Done

### Task 1: Moved pb-demo-section on homepage (page 11)
- FROM: between hero section and marquee
- TO: after the 3-card features section (after "Executes Autonomously" </section>), before value-pyramid section

### Task 2: Swapped Watch Demo popup video on pages 689 + 688
- FROM: static MP4 (`/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4`)
- TO: HLS streaming (`https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/eaf39ae1_Portal_demo/master.m3u8`)
- Also replaced `openVideoModal()` / `closeVideoModal()` with HLS.js dynamic loading + `window._pbHls` destroy on close

### Task 3: Moved pb-demo-section on pages 689 + 688 to same after-features position

---

## Correct Section Order (all 3 pages after this deployment)
1. Hero section
2. pb-demo-section (was here BEFORE this change, now removed from here)
3. Marquee
4. ... content sections ...
5. Features section ("AN AI THAT BECOMES YOURS" with 3 cards including "Executes Autonomously")
6. **pb-demo-section** (NEW position after this change)
7. Value Pyramid ("WHY THIS FEELS DIFFERENT")

---

## Key Landmarks Used

| Marker | Description |
|--------|-------------|
| `<!-- DEMO VIDEO EMBED SECTION -->` | Start of pb-demo-section block to remove |
| `<section class="pb-demo-section" id="pb-demo-section"` | HTML element marker (not CSS) |
| `Executes Autonomously` | Last text in features section |
| `</section>` after EA | Features section close = insertion point |
| `<div class="marquee">` | Marquee HTML element for order verification |
| `id="value-pyramid"` | Value pyramid HTML element for order verification |

**CRITICAL**: Always use HTML element markers for position verification, NOT CSS class names.
CSS classes appear in the `<style>` block too, giving false early positions.

---

## Verification Pattern (Final Numbers)

```
Homepage (11):   marquee=159510, EA=164604, pb-demo=165235, VP=166789
Pay Test 2 (689): marquee=159529, EA=164623, pb-demo=165254, VP=166808
PT Sandbox (688): marquee=159777, EA=164871, pb-demo=165502, VP=167056
```

---

## REST API Verification Gotcha

When checking `_elementor_data` via `GET /wp-json/wp/v2/pages/{id}?context=edit`,
the returned `_elementor_data` string has double-escaped quotes (`\\"`) because it's
JSON-within-JSON. Searching for `<section class="pb-demo-section"` fails against the
raw string - you MUST `json.loads(ed)` first to get the parsed elementor data, then
extract the `settings.html` widget string, then search.

---

## Old MP4 Pattern for Pages 689/688

```
OLD video tag:
<video
    class="video-modal__video"
    id="demoVideo"
    muted
    playsinline
>
    <source src="https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4" type="video/mp4">
</video>

OLD openVideoModal function separator between open/close:
"        }\n        \n        function closeVideoModal() {"
(note: 8 trailing spaces on the blank line - NOT a clean empty line)
```

---

## Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_video_move_and_hls_swap.py`

## Backups

- `/home/jared/projects/AI-CIV/aether/exports/backup_page_11_elementor_data_2026-02-28-video-move.json`
- `/home/jared/projects/AI-CIV/aether/exports/backup_page_689_elementor_data_2026-02-28-video-move.json`
- `/home/jared/projects/AI-CIV/aether/exports/backup_page_688_elementor_data_2026-02-28-video-move.json`

## Tags

purebrain, homepage, video, hls, elementor, demo, embed, page-11, page-689, page-688, move, reposition, watch-demo-modal

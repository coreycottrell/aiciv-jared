# Blog Banner Audit - 2026-03-18

## Task
Investigate why blog post banners on blog listing pages show wrong images.

## Findings

### What Is NOT Wrong
- All 31 banner image files exist in `/exports/cf-pages-deploy/blog/[slug]/banner.*`
- All `src` references in `blog/index.html` correctly point to `/blog/[slug]/banner.ext`
- All `src` references in `blog-neural-feed-memories/index.html` correctly point to `/blog/[slug]/banner.ext`
- No duplicate image hashes (all 31 are distinct files)
- Extensions match (`.jpg` where file is `.jpg`, `.png` where `.png`)

### What IS Wrong — Image File Content
Two banner image files contain wrong/mismatched image content:

1. **`exports/cf-pages-deploy/blog/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/banner.jpg`**
   - Post title: "Why Most AI Agents Break When You Ask About Data Security"
   - Image content: Shows "Enterprise AI That Learns How Your Business Runs" — completely wrong post
   - Size: 170,146 bytes

2. **`exports/cf-pages-deploy/blog/why-your-ai-should-have-a-name/banner.png`**
   - Post title: "Why Your AI Should Have a Name"
   - Image content: Generic abstract nebula/flower image with NO post title text
   - This is likely a placeholder/wrong image that was never replaced
   - Size: 2,705,508 bytes

### What Cannot Be Fixed Without New Images
These are binary image files. The correct images need to be regenerated or sourced.
The HTML references are already correct — no HTML changes needed.

## Architecture Notes
- Blog pages at CF Pages: `/blog/` and `/blog-neural-feed-memories/`
- Both reference banners at `/blog/[slug]/banner.*` (relative to CF Pages root)
- Blog posts are in `exports/cf-pages-deploy/blog/[slug]/`
- `blog-neural-feed-memories/index.html` is untracked in git (new file, not yet committed)
- Binary banner files are also not tracked in git

## Action Required
Jared or designer needs to provide correct banner images for:
1. `most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2` — need "Why Most AI Agents Break When You Ask About Data Security" banner
2. `why-your-ai-should-have-a-name` — need proper "Why Your AI Should Have a Name" banner

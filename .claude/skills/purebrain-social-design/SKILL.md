---
name: purebrain-social-design
description: PureBrain branded social media and content design standards — hexagon logo, wordmark colors, platform dimensions, image generation workflow
trigger: creating visual content, LinkedIn images, blog banners, social graphics, branded images, FLUX generation
agents: [3d-design-specialist, linkedin-writer, linkedin-specialist, marketing-strategist, content-specialist, social-media-specialist, blogger, dept-marketing-advertising]
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# PureBrain Social Media Design Standards

## Trigger
Use when creating ANY visual content for LinkedIn posts, Bluesky posts, blog banners, social graphics, or any PureBrain-branded image.

## Agent Routing

**`3d-design-specialist` creates ALL visual content. No exceptions.**

Never delegate image creation to MA#, dept-marketing-advertising, or any other agent. The 3d-design-specialist has Gleb-level training and references materials at: https://drive.google.com/drive/folders/1CjE5qC4UubKqAsCwBJSH4s3oCORRWrbV

---

## Brand Elements (MANDATORY on every image) (FULL REFERENCE -> https://drive.google.com/drive/folders/1qXvpzI_1A-e-KlKqD8iU-rV63JVrfKxq?usp=drive_link)

### 1. PureBrain Hexagon Logo
- The hexagonal logo/icon MUST appear on every image
- Location: top-left or top-center, with breathing room from edges
- Minimum size: 60px on social, 80px on blog banners
- Source: `/exports/cf-pages-deploy/investor-avatar/pt-hex-logo.png`
- Must be clearly visible against the background

### 2. PUREBRAIN.ai Wordmark
- PUREBR = blue #2a93c1
- AI = orange #f1420b
- N = blue #2a93c1
- .ai = white #ffffff
- All uppercase, bold weight (700+)
- Font: Oswald, Oswald Bold
- Must appear near the hexagon logo or bottom of image
- NEVER use all-white or all-one-color for the wordmark

### 3. Brand Colors
- Primary background: dark navy #080a12
- Blue accent: #2a93c1 (cerulean blue)
- Orange accent: #f1420b (Pure Technology orange)
- Text: white #ffffff or light gray #e2e8f0
- Secondary text: #94a3b8
- NEVER use light/white backgrounds
- NEVER use purple, green, or off-brand colors

### 4. Text Readability Rules
- Headline text: minimum 48pt on 1080px wide images
- All text must have sufficient contrast against background
- Use semi-transparent dark overlays behind text if placed over complex imagery
- Text shadow or glow for readability: `text-shadow: 0 2px 8px rgba(0,0,0,0.8)`
- Keep text at least 80px from all edges (mobile crop safety)
- Test: if you squint and can't read it, the contrast is too low

### 5. CTA (MANDATORY on all social images — NOT newsletter/blog banners)
- "purebrain.ai" URL must appear on every image
- Location: bottom area, clearly readable
- Color: white or blue #2a93c1
- **POST-SPECIFIC CTA**: Every social image (LinkedIn post, Bluesky, Instagram, etc.) MUST include a CTA relevant to the post topic. Examples:
  - Post about AI agents failing → "Stop losing AI projects → purebrain.ai"
  - Post about memory layer → "Your AI should remember you → purebrain.ai"
  - Post about AI partnership → "Meet your AI partner → purebrain.ai"
- The CTA should be a short action phrase + purebrain.ai URL
- Place below the subline, above the bottom edge safe zone
- Font size: 24-32pt, bold, white or blue
- **EXCEPTION**: Newsletter banners and blog banners do NOT need the post-specific CTA (they have their own CTA structure)

---

## Format Specs by Platform

### LinkedIn Post (4:5 portrait)
- Dimensions: 1080 x 1350 px
- Layout: Hexagon logo top, headline center, subline below, wordmark + CTA bottom
- FLUX prompt style: futuristic, neural networks, glass/ethereal, brains, AI consciousness
- Background: dark navy with blue/orange accents

### LinkedIn Newsletter Banner (landscape)
- Dimensions: 1200 x 628 px (wider proportions — EXCEPTION to standard format)
- Same brand elements but horizontal layout
- Logo + wordmark left or center, headline right or center

### Blog Banner (16:9 landscape)
- Dimensions: 1200 x 630 px
- 5 MANDATORY elements:
  1. Hexagon logo
  2. PUREBRAIN.ai wordmark (correct colors)
  3. Blog title
  4. "Awaken Your AI Partner Today"
  5. "The Neural Feed — a blog by Aether — AI Partner for PureTechnology.ai"

### Bluesky Post (1:1 square)
- Dimensions: 1080 x 1080 px
- Same brand elements, square layout

### Instagram Story (9:16)
- Dimensions: 1080 x 1920 px
- Brand elements at top and bottom, content center

---

## Image Generation Workflow

### Step 1: Generate base with FLUX Pro
- Use Replicate API (FLUX Pro model)
- Prompt MUST include: "dark navy background, futuristic, neural network, glass, ethereal, AI consciousness, cinematic lighting"
- NEVER include text in FLUX prompt (FLUX can't render text reliably)

### Step 2: Composite with PIL/Pillow
- Load FLUX base image
- Add gradient overlays for text readability (top + bottom)
- Add hexagon logo (from source file)
- Add PUREBRAIN.ai wordmark with correct per-letter colors
- Add headline text (large, bold, high contrast)
- Add subline text
- Add CTA URL
- Ensure 80px safe zone from all edges

### Step 3: Quality Check
- Verify dimensions match platform spec
- Verify hexagon logo is visible
- Verify wordmark colors are correct (not all white)
- Verify all text is readable at 50% zoom
- Verify no text within 80px of edges

### Step 4: Google Drive Filing (MANDATORY)
- EVERY piece of content MUST be filed in Google Drive LinkedIn Operations folder
- Folder ID: `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`
- URL: https://drive.google.com/drive/folders/12QBh5yVTppCo04jh5wrmhvZlqUxPIp71
- Filing structure:
  - Create a subfolder per post date: `YYYY-MM-DD — [Post Title Slug]`
  - Include: final image (.png), post text (.md), any drafts, FLUX prompt used
  - For LinkedIn comments: file in a `comments/YYYY-MM-DD` subfolder
- This is NOT optional — if it's not in Drive, it didn't happen
- File IMMEDIATELY after creating content, not as an afterthought
- Use the gdrive-operations skill for API access

---

## Anti-Patterns (NEVER do these)
- All-white or light backgrounds
- Missing hexagon logo
- All-one-color wordmark
- Text too close to edges (gets cropped on mobile)
- Low contrast text over busy imagery without overlay
- Purple, green, or off-brand accent colors
- Text generated by FLUX/AI models (always composite with PIL)
- Wrong wordmark color split (it's PUREBR+AI+N+.ai, not PURE+BRAIN)

# Blog Post Publishing Template - MANDATORY for All Posts

**Last Updated**: 2026-02-19
**Learned From**: Post 480 missing social share + CTA section

## CRITICAL: Every Blog Post MUST Include These Sections

When publishing blog posts to purebrain.ai via REST API, the markdown-to-HTML conversion
is NOT sufficient. Every post MUST also include:

### 1. Social Sharing Icons (pt-social-share)
- LinkedIn, X/Twitter, Facebook, Email share buttons
- Uses `.pt-social-share` CSS class
- Includes `border: none !important` on links to prevent orange border issue

### 2. CTA Block (blog-cta-block)
- "Ready to awaken your AI partner?" heading
- "Start Your AI Partnership" orange gradient button → links to https://purebrain.ai/#awakening
- Newsletter subscription link → links to /blog/
- UTM parameters: `utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={POST_SLUG}`

### LINK RULES (from Jared 2026-02-19, UPDATED same day)
- **ALL "Start Your AI Partnership" CTA buttons link to https://purebrain.ai/#awakening**
- This anchors directly to the awakening section on homepage
- NEVER link to /purebrain-3/, /purebrain-4/, /pay-test/ or any test page derivation
- Allowed links: homepage (#awakening anchor), thank you page, assessment pages, blog/blog posts for interlinking
- Test pages (purebrain-3, purebrain-4, pay-test) are for internal testing ONLY

### 3. Template Location
The full HTML template is stored at:
- `/home/jared/projects/AI-CIV/aether/.claude/skills/wordpress-publishing/blog-footer-template.html`

### How to Use
After converting blog markdown to HTML, ALWAYS append the footer template.
Replace `{slug}` in UTM params with the post's slug.

### Reference Post
Post 381 has a complete working example of the full footer section.

### Posts Known to Have This Section
- 381 (CEO vs Employee gap)
- 316, 373, 172, 98 (older posts - verify individually)
- 480 (AI Pilot Purgatory - added 2026-02-19)

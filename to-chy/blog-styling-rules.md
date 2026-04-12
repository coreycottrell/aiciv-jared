# Blog Styling Rules (PERMANENT - LOCKED IN 2026-02-22)

## Content Rules (ALL Blog Posts, Both Sites)

### Transparency/Work Breakdown Section
- **NO proper names EVER** - no product names, no people names, no personal pronouns for people
- "Loosely describe what was done and the end result" - no specifics
- Example BAD: "Used Gleb Kuznetsov's glass sphere technique with Three.js"
- Example GOOD: "Applied premium glass-morphism visual design techniques"
- This is a PERMANENT RULE for all future blog posts
- Jared: "MAKE THIS A RULE FOR THIS SECTION GOING FORWARD!!!"

### CTA Buttons
- Default: orange bg (#f1420b) + WHITE text (#ffffff)
- Hover: blue bg (#2a93c1) + white text (#ffffff)
- NEVER have invisible text on buttons

### Tags
- Default: blue bg (#2a93c1) + white text (#ffffff)
- Hover: orange bg (#f1420b) + white text (#ffffff)

### In-Text Links
- Default: orange text (#f1420b), no background
- Hover: orange background (#f1420b) + WHITE text (#ffffff)
- CRITICAL: Text MUST swap to white on hover (currently text stays orange = invisible)
- This applies to ALL `<a>` tags within blog post content

### Neural Feed Subscribe Form
- Must be connected to Brevo List 3 (The Neural Feed)
- Verify form submission works on every blog post

## CSS Implementation Notes
- These rules apply to BOTH purebrain.ai AND jareddsanborn.com
- Deployed via WordPress plugin (purebrain-security plugin with inline CSS)
- Use `!important` for specificity against theme/Elementor overrides
- Blog content links selector: `.entry-content a`, `.elementor-widget-theme-post-content a`
- CTA button selector: `.blog-cta-button`, `a.blog-cta-button`
- Tag selector: `.blog-tag`, `a[rel="tag"]`

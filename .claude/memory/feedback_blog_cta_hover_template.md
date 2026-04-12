---
name: Blog CTA hover states locked as template
description: Blog post CTA button goes blue on hover, newsletter link goes white on hover - permanent template rule
type: feedback
---

Blog CTA hover states are LOCKED as permanent blog template (Jared approved 2026-03-12, said "BEAUTIFUL lock this in as blog template!"):

1. **"Start Your AI Partnership" button** → turns Pure Tech Blue (#2a93c1) on hover (normally orange #f1420b)
2. **"subscribe to our newsletter" link** → text goes WHITE on hover (normally default link color)

**Why:** Jared tested and loved the visual polish. These hover states apply to ALL blog posts.

**How to apply:**
- TWO-LAYER update required: WordPress plugin (pb-blog-styling.php) AND CF Pages static HTML files
- CSS selectors: `a[href*="awakening"]:hover` for button, `.pb-blog-post a[href*="subscribe"]:hover` for newsletter link
- Every new blog post must include these hover states in the CTA section
- When deploying CF Pages blog posts, include the hover CSS in the `<style>` block

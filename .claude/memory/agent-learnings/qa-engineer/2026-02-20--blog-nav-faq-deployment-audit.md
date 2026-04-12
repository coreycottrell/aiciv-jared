# QA Audit: Blog Nav Menu + FAQ + Newsletter CSS - 2026-02-20

**Type**: operational
**Topic**: Full QA audit of Plugin v2.4.0 - blog nav menu, FAQ sections, newsletter CSS, thank-you page

## Test Results Summary

### Nav Menu (Plugin v2.4.0)
- ALL 7 blog posts: pb-blog-nav CSS present, all 3 links functional
- Nav is JS-injected at runtime (not server-rendered HTML) - curl sees JS code, not rendered DOM
- Home link uses FULL URL: `href="https://purebrain.ai/"` (not relative `/`) - this is correct
- The earlier `link_home: FAIL` in testing was a false positive (tested for `href="/"` but actual is full URL)
- Posts confirmed passing: all 6 accessible posts have nav + FAQ

### Post 5 URL Issue
- URL provided: `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-/`
- Actual live slug: `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/` (with `-2` suffix)
- 301 redirect exists from provided URL to `-2` slug
- When followed via `curl -sL`, post passes all checks

### Category Pages
- `for-teams` and `for-individuals`: pb-blog-nav CSS present, all 3 nav links present
- "All Posts" text found ONLY in plugin comment (`Replaces "← All Posts" with full nav menu`) - not in rendered content
- No `← All Posts` back arrow in rendered content - PASS

### FAQ Sections
- All 6 accessible posts: `faq-section` class present - PASS

### Newsletter Link CSS
- `.blog-cta-block p a` rule exists with `color: #2a93c1`
- Hover rule: `color: #ffffff !important` - turns white on hover - PASS

### Thank-You Page
- Hexagon icon: `purebrain-hexagon-icon.jpg` (48x48px, displayed)
- PUREBRAIN color split: `PUREBR<span style="color: #f1420b;">AI</span>N` - orange AI confirmed x2
- "being set up" text: PASS (not "full set up")
- Login details text: "Email with log in details will be sent..." - PASS
- Personalization script: `URLSearchParams` present - PASS

## Key Patterns for Future QA

1. **JS-injected nav**: Plugin injects nav via document.createElement at runtime. curl sees the JS source code, not rendered DOM. Check for: (a) pb-blog-nav in CSS, (b) nav.innerHTML JS block, (c) actual anchor tags in JS string
2. **Home link is full URL**: `href="https://purebrain.ai/"` not `href="/"` - test accordingly
3. **Post slug `-2` issue**: Some posts have `-2` suffix due to WordPress slug deduplication. The provided URL redirects - follow with `-L` flag
4. **All Posts in plugin comment**: Plugin code has comment `Replaces "← All Posts"` - this is NOT rendered content, test for absence in actual DOM

## Testing Approach That Works

```python
# For JS-injected nav, check for the JS string that builds the nav
'nav.innerHTML' in content  # confirms nav injection code present
'href="https://purebrain.ai/"' in content  # confirms home link in JS
'href="https://purebrain.ai/blog/"' in content  # confirms blog link
'href="https://purebrain.ai/ai-adoption-review/"' in content  # confirms assessment link
```

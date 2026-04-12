# LinkedIn Newsletter CTA Component for WordPress/Divi

**Date**: 2026-02-13
**Type**: operational
**Topic**: Blog footer CTA for LinkedIn newsletter subscription

---

## Task

Created HTML/CSS component for blog footer promoting LinkedIn newsletter subscription.

## Solution

**File**: `/home/jared/projects/AI-CIV/aether/exports/website/blog-footer-cta.html`

**Approach:**
- Self-contained HTML with inline CSS
- Dark neural theme matching Aether aesthetic
- LinkedIn brand colors (#0a66c2)
- Mobile responsive with media queries
- Hover effects using inline onmouseover/onmouseout

## Key Technical Decisions

1. **Inline CSS**: WordPress Custom HTML blocks and Divi Code modules work best with inline styles
2. **Inline hover effects**: Used `onmouseover`/`onmouseout` instead of CSS :hover to keep everything inline
3. **Mobile breakpoints**: 768px (tablet) and 480px (phone)
4. **SVG icon**: Embedded LinkedIn logo as SVG to avoid external dependencies
5. **Security**: Added `rel="noopener noreferrer"` to external link

## Design Elements

- Gradient background: #1a1a2e → #16213e
- Border/button: LinkedIn blue #0a66c2
- Hover: Darker blue #004182
- Text colors: White (#ffffff), gray (#b8c5d6), muted (#8892a0)
- Border radius: 12px (card), 8px (button)
- Shadow: Subtle glow effect

## WordPress/Divi Usage

**WordPress Custom HTML Block:**
- Add block → Custom HTML
- Paste entire file contents
- Works immediately

**Divi Code Module:**
- Add Code module
- Paste HTML
- No additional configuration needed

## Patterns Worth Remembering

- Inline styles + media queries work well for WordPress
- Button hover effects can be done inline with JS
- SVG icons avoid image upload requirements
- Self-contained components are easier for clients to implement

## Newsletter URL

`https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7428125791609192449`

This URL is specific to Jared's LinkedIn newsletter.

# Blog Restoration Lessons - 2026-02-14

**Context**: Afternoon session attempting to fix purebrain.ai/blog styling, which escalated into breaking and restoring the blog.

## Key Learnings

### 1. WordPress Reading Settings Can Break Blog Display
- **Symptom**: Blog page shows header but no posts
- **Root Cause**: Settings > Reading > "Posts page" dropdown was set to "-- Select --" instead of "Blog"
- **Fix**: Set Posts page to the correct page (ID 95)
- **Lesson**: This is NOT a CSS issue - check WordPress settings before assuming CSS broke things

### 2. Elementor Page Content ≠ Additional CSS
- **Additional CSS** (Appearance > Customize > Additional CSS): Theme-wide styling like cursor, preloader
- **Elementor Page Content**: The actual design widgets on a specific page
- **Lesson**: Clearing Additional CSS won't delete Elementor page designs, but if page template/content changes, the design is lost

### 3. Browser Automation for WordPress Customizer is Unreliable
- Multiple attempts to automate Customizer (Additional CSS, Footer Options, Widget Areas) failed
- Elements consistently "not visible" to Playwright even after page loads
- **Lesson**: WordPress Customizer uses complex JavaScript that doesn't play well with automation. Manual paste is often faster than debugging automation.

### 4. Always Capture Working State BEFORE Changes
- Jared had to manually save the working HTML to a docx file
- We didn't have a local backup of the working Elementor design
- **Lesson**: Before touching styling, screenshot + save HTML of working state

### 5. Distinguish Between Template and Content Issues
- Current page shows default Awaiken theme blog template
- Working version used `page-template-elementor_canvas` with custom widgets
- **Lesson**: If design looks completely different (not just colors), it's likely a template or content issue, not CSS

## What Broke and Why

1. **Footer social icons automation**: Repeatedly failed because Customizer/Elementor UI is unpredictable
2. **Blog posts disappeared**: WordPress Reading Settings got changed (possibly during one of the automation attempts)
3. **Custom design lost**: The Elementor page template/content was different from what Jared expected

## Restoration Path

The working HTML shows the custom design was built with:
- Text-editor widget containing inline CSS + HTML for the blog design
- HTML widget for brain animation background
- elementor_canvas page template

To restore: Need to either find WordPress revision OR recreate from saved HTML.

## Tags
- wordpress
- elementor
- restoration
- debugging
- browser-automation

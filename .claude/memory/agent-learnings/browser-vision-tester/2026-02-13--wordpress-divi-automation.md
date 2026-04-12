# WordPress Divi Visual Builder Automation Learning

**Date**: 2026-02-13
**Agent**: browser-vision-tester
**Type**: technique
**Topic**: WordPress Divi automation patterns and limitations

---

## Context

Attempted to automate adding a blog section to jareddsanborn.com homepage using Playwright. Site runs WordPress 6.9.1 with Divi theme.

---

## Key Learnings

### 1. Divi Visual Builder is Complex to Automate

**Challenge**: Divi Visual Builder uses a React-based interface with dynamic element rendering that makes traditional selector-based automation difficult.

**Specific issues**:
- Controls appear on hover, not in static DOM
- Elements rendered inside iframes
- Class names include dynamic hashes
- Asynchronous loading with no clear "ready" state

**What worked**: Opening Visual Builder via direct URL `?et_fb=1&PageSpeed=off`
**What didn't work**: Clicking dynamically-rendered add section/module buttons

### 2. Use `domcontentloaded` Instead of `networkidle`

WordPress admin pages with many plugins never reach `networkidle` state. The `networkidle` timeout causes automation to fail even when pages are functionally loaded.

```python
# BAD - times out
await page.goto(url, wait_until="networkidle")

# GOOD - works reliably
await page.goto(url, wait_until="domcontentloaded")
await page.wait_for_timeout(3000)  # Allow scripts to init
```

### 3. WordPress Admin Selectors That Work

**Login page**:
- `#user_login` - username field
- `#user_pass` - password field
- `#wp-submit` - login button

**Pages list**:
- `a.row-title:has-text('PageName')` - click on specific page

**Categories page**:
- `#tag-name` - category name input
- `#tag-slug` - category slug input
- `#submit` - add category button

**Page editor (Gutenberg)**:
- `[aria-label='Add title']` - title input
- `button:has-text('Publish')` - publish button

**Divi buttons**:
- `a:has-text('Edit With The Divi Builder')` - edit existing page
- `button:has-text('Use Divi Builder')` - new page builder choice

### 4. Screenshot-Driven Debugging is Essential

Taking screenshots at every step revealed:
- Categories already existed (preventing duplicate creation)
- Divi modal states (Build from Scratch, Premade Layout, AI)
- Visual Builder selection states (cyan outlines)
- Control toolbar positions

Always capture full_page=True for scrollable content.

### 5. WordPress Categories Can Be Created Programmatically

Categories are straightforward to automate:
```python
await page.fill("#tag-name", "Category Name")
await page.fill("#tag-slug", "category-slug")
await page.click("#submit")
```

### 6. Blog Archive Works Without Divi Page

WordPress default blog archive at `/blog` functions even without a dedicated Divi-built page. The archive template shows posts, sidebar widgets, and is functional.

---

## Recommended Approach for Divi Automation

1. **Use Divi JSON import/export** for layout changes instead of Visual Builder interaction
2. **Use WordPress REST API** for content creation with Divi shortcodes
3. **Create Divi Global Modules** manually, then duplicate programmatically
4. **Consider browser extension** with direct React state access for Visual Builder

---

## Files Created

**Automation scripts**:
- `/home/jared/projects/AI-CIV/aether/tools/divi_blog_setup.py` (v1)
- `/home/jared/projects/AI-CIV/aether/tools/divi_blog_setup_v2.py` (v2)
- `/home/jared/projects/AI-CIV/aether/tools/divi_blog_setup_v3.py` (v3, production-ready)
- `/home/jared/projects/AI-CIV/aether/tools/divi_add_blog_module.py`
- `/home/jared/projects/AI-CIV/aether/tools/divi_click_add_section.py`

**Documentation**:
- `/home/jared/projects/AI-CIV/aether/exports/divi-blog-setup/SETUP-REPORT.md`

**Screenshots**:
- 48 screenshots in `/home/jared/projects/AI-CIV/aether/exports/divi-blog-setup/`

---

## When to Apply This Learning

- Any WordPress Divi automation task
- Visual page builder automation (Elementor, WPBakery similar challenges)
- WordPress admin automation with many plugins
- Long-running page loads in automation

---

## Confidence

High - Based on direct testing with multiple iterations and clear failure/success patterns observed.

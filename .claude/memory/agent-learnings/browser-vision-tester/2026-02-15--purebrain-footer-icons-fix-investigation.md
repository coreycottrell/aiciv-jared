# PureBrain.ai Footer Icons Fix Investigation

**Date**: 2026-02-15
**Agent**: browser-vision-tester
**Type**: operational
**Topic**: WordPress footer social icons - automation blocked, manual fix documented

## Context

Task: Fix footer social icons on purebrain.ai blog pages
- Position 3 (Globe) -> should be X/Twitter icon
- Position 5 (YouTube) -> should be Globe/Website linking to purebrain.ai

## Key Findings

### 1. Root Cause Identified
The theme (Artistics v1.0.15) doesn't recognize `x.com` as Twitter. Its URL pattern matching only looks for `twitter.com`:
- URLs containing `twitter.com` -> Twitter icon + `class="twitter"`
- URLs containing `x.com` -> Globe icon + `class="nosocial"`

### 2. Simple Fix: Use twitter.com
Twitter redirects `twitter.com/username` to `x.com/username` automatically.
- Change URL from `https://x.com/PureBrainAI` to `https://twitter.com/PureBrainAI`
- Theme will recognize it and show Twitter icon
- Link still works correctly

### 3. GoDaddy CAPTCHA Blocks Automation
GoDaddy hosting triggers reCAPTCHA after multiple headless browser login attempts:
- First few logins work
- After ~5-10 automated sessions, CAPTCHA appears
- CAPTCHA persists for IP address for several minutes
- No programmatic way to bypass

### 4. REST API Limitations
WordPress REST API does NOT expose theme customizer settings:
- `/wp-json/wp/v2/settings` - only basic site settings
- Theme mods stored in `wp_options` table as `theme_mods_artistics`
- No standard endpoint to modify these
- Application password works for auth but not for customizer access

### 5. XML-RPC Disabled
GoDaddy disables XML-RPC by default (returns 403 Forbidden).

## Solutions Documented

### Primary Fix (Manual)
1. Login to WordPress admin manually
2. Appearance > Customize > Footer Options
3. Change X URL from `x.com` to `twitter.com`
4. Clear YouTube URL, add Website URL with `purebrain.ai`
5. Publish

### CSS Fallback
If theme doesn't support proper icon, use CSS to swap icons:
```css
.social-icons .nosocial i.fa-globe::before {
    content: "\f099";  /* Twitter bird */
}
```

## Files Created

```
/home/jared/projects/AI-CIV/aether/sandbox/wp-screenshots/footer-icons-fix/
  - MANUAL-FIX-INSTRUCTIONS.md (detailed manual steps)
  - 01_blog_fullpage.png
  - 02_blog_footer.png (current state)
  - 03-08_*.png (login/customizer screenshots)
  - page_content.html (full HTML)
```

## Pattern Learned

### For X/Twitter Icon Issues in WordPress Themes
1. Check if theme recognizes `x.com` (many don't - written pre-rebrand)
2. Try using `twitter.com` URL instead (redirects automatically)
3. If that fails, use CSS to swap Font Awesome icon codes
4. Theme class `nosocial` indicates unrecognized social platform

### For GoDaddy-Hosted WordPress
1. Browser automation works initially but triggers CAPTCHA
2. REST API good for content, not for theme/customizer settings
3. XML-RPC likely disabled
4. Manual intervention often required for theme settings

## Dead Ends

- REST API customizer endpoint: doesn't exist
- XML-RPC: disabled (403)
- Elementor templates: footer not in Elementor
- WP File Manager: could edit theme PHP but not recommended

## Memory Written

Path: .claude/memory/agent-learnings/browser-vision-tester/2026-02-15--purebrain-footer-icons-fix-investigation.md
Type: operational
Topic: WordPress footer social icons automation investigation

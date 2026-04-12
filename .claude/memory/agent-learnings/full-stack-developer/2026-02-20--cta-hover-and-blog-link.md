# Memory: CTA Button Hover Effect + Blog Link on Pricing Page

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer

## Tasks Completed

### 1. CTA Button Hover Effect ("Start Your AI Partnership")
**Requirement**: On hover, blue (#2a93c1) highlight/glow around the orange button's white text.

**Key Learning**: There was an EXISTING conflicting CSS rule in WordPress Additional CSS (`id="wp-custom-css"`) from a previous session (Feb 18) that made the button background transparent on hover:
```css
/* FIX 3: Newsletter / subscribe link - no orange background, white border on hover */
body.single-post .blog-cta-block a:hover {
    background: transparent !important;
    ...
}
```

**Fix Applied**:
1. Updated `tools/security/purebrain-security-plugin.php` from v2.0.0 to v2.1.0 with new CSS section `j)` that adds `box-shadow` glow on hover
2. Replaced the conflicting FIX 3 rule in WordPress Additional CSS (via Playwright Customizer) with the new blue glow CSS

**New CSS behavior**:
```css
body.single-post .blog-cta-block a:hover {
    box-shadow: 0 0 0 3px #2a93c1, 0 0 18px rgba(42,147,193,0.55), 0 6px 20px rgba(0,0,0,0.35) !important;
    transform: translateY(-2px) !important;
    color: #ffffff !important;
}
```

**Deployment method**:
- Plugin upload via Playwright (browser automation)
- Additional CSS via Playwright + WordPress Customizer CodeMirror editor
- When CodeMirror CSS found: `cm.CodeMirror.getValue()` to read, `cm.CodeMirror.setValue(css)` to write

### 2. Blog Link on Pricing/Teams Section (Homepage)
**Requirement**: Add "blog link on teams/individual pages" - interpreted as pricing section on homepage (page 11).

**Location**: Added after the `pricing__steps` div (the 5-step setup guide), before the closing of the pricing section container.

**HTML added**:
```html
<div class="pricing-blog-link" style="text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.08);">
    <p style="color: rgba(255,255,255,0.5); ...">Want to learn more about AI partnerships before diving in?</p>
    <a href="https://purebrain.ai/blog/?utm_source=pricing&utm_medium=link&utm_campaign=pricing_blog" style="color: #2a93c1; ...">Read Our Blog →</a>
</div>
```

**Deployment method**:
1. First updated `content.raw` via REST API (but this doesn't affect live Elementor page)
2. Then updated `_elementor_data` in meta via REST API (this IS what renders on live page)
3. Called `DELETE /wp-json/elementor/v1/cache` to clear Elementor's PHP cache

**Critical reminder**: Homepage (page 11) uses Elementor (`_elementor_edit_mode: builder`). ALWAYS update `_elementor_data` meta, not just `content.raw` for Elementor pages!

## GoDaddy reCAPTCHA Lockout

**Problem**: Multiple browser login attempts from same IP triggered GoDaddy's reCAPTCHA bot detection. Shows "Please verify you are human" page with Google reCAPTCHA checkbox.

**Cause**: Repeated failed/partial Playwright login attempts (script errors causing multiple login attempts in quick succession).

**Solution**: Wait 15-30 minutes for lockout to clear. The REST API (curl) still works during the lockout - only the browser login (wp-login.php) is affected.

**Prevention**:
- Test scripts carefully before running multiple times
- Use REST API (app password) for as many operations as possible
- Avoid Playwright login loops

## WP Plugin Activation via REST API

**Works**: `POST /wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin` with `{"status": "active"}`
- Uses the literal path from `plugin` field, NOT URL-encoded
- Correct URL: `https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin`
- Incorrect (fails): `purebrain-security%2Fpurebrain-security-plugin`

**Can't do via REST API**: Update plugin PHP file content (no file-write endpoint)

## Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` - v2.1.0 with CTA hover CSS
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip` - Updated zip
- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security.php` - Updated copy
- `purebrain.ai` Additional CSS (via Customizer) - FIX 3 replaced with blue glow CSS
- Homepage page 11 `_elementor_data` - Blog link added to pricing section

## Tools Created
- `/home/jared/projects/AI-CIV/aether/tools/deploy_security_plugin_v2.py` - Plugin deployment script
- `/home/jared/projects/AI-CIV/aether/tools/fix_blog_cta_hover.py` - Additional CSS fix via Customizer
- `/home/jared/projects/AI-CIV/aether/tools/add_blog_link_to_pricing.py` - Blog link deployment script

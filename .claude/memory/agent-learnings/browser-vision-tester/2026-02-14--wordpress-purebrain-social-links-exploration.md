# WordPress Social Links Exploration - PureBrain.ai

**Date**: 2026-02-14
**Agent**: browser-vision-tester
**Type**: operational
**Topic**: WordPress/Elementor social media profile links configuration

## Context

Explored purebrain.ai/wp-admin to find options for adding social media profile links (LinkedIn, Facebook, X, Instagram, Bluesky) to the single post template.

## Key Findings

### Theme: Artistics

The site uses "Artistics" (Creative Digital Agency WordPress Theme) with Elementor Free (v3.35.4).

### Social Profile Links Location

**Theme Customizer > Footer Options > Social URLs**
- Theme has built-in fields for social profile URLs
- Fields visible: Facebook URL, YouTube URL
- These display in the footer area
- May be limited to specific platforms (need to verify if LinkedIn, Instagram, Bluesky are supported)

### Social Sharing (Different from Profile Links)

**Theme Customizer > Blog Options > Social Sharing**
- Checkboxes for share buttons: Facebook, WhatsApp, Reddit, Twitter, Pinterest, Email, Instagram
- These are SHARE buttons (to share posts to social media)
- NOT the same as profile links (follow us)

### Elementor Limitations (Free vs Pro)

- **Single Post Template**: Requires Elementor Pro to create custom single post template
- Theme Builder shows "Upgrade" button on Single Post card
- No existing single post templates found ("No Single Post found")

### GoDaddy Login Flow

The WordPress login has GoDaddy integration:
1. Default shows "Log in with GoDaddy" button
2. Must click "Log in with username and password" link to reveal traditional login form
3. Then standard #user_login, #user_pass, #wp-submit selectors work

## Automation Pattern Learned

```python
# GoDaddy WordPress login handling
try:
    link = await page.query_selector("text='Log in with username and password'")
    if link:
        await link.click()
        await page.wait_for_timeout(2000)
except:
    pass

await page.wait_for_selector("#user_login", state="visible", timeout=10000)
await page.fill("#user_login", username)
await page.fill("#user_pass", password)
await page.click("#wp-submit")
```

## Screenshots Saved

Location: `/home/jared/projects/AI-CIV/aether/exports/wp-social-links/`

Key files:
- `*_footer_options_direct.png` - Shows Social URLs section
- `*_blog_options_direct.png` - Shows Social Sharing checkboxes
- `*_single_post_direct.png` - Frontend blog post view
- `*_post_editor.png` - WordPress post editor

## Recommended Next Steps

1. **Easiest**: Configure Footer Options > Social URLs in Customizer
2. **For single post**: Consider Elementor Pro upgrade for custom templates
3. **Alternative**: Install dedicated social icons plugin
4. **Bluesky**: May need custom solution (new platform, limited theme support)

## Dead Ends Documented

- `admin.php?page=artistics` - Returns "not allowed to access"
- `admin.php?page=wpseo_social` - Yoast social settings not accessible
- Elementor Theme Builder Single Post - Requires Pro upgrade

## Future Reference

When working with WordPress sites:
1. Check Theme Customizer panels first (Footer, Header, Blog Options)
2. Check for GoDaddy login integration (common with GoDaddy-hosted sites)
3. Elementor Free has limited Theme Builder (Pro required for custom templates)
4. Social "sharing" vs social "profile links" are different features

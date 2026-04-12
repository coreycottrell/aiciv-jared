# WordPress + Elementor Backend Reconnaissance Pattern

**Type**: technique
**Topic**: Navigating WordPress admin and Elementor editor via Playwright
**Date**: 2026-02-15
**Agent**: browser-vision-tester

---

## Context

Performed reconnaissance on purebrain.ai WordPress backend to analyze the "PureBrain 2.0" draft page before Stripe integration.

## Key Learnings

### 1. GoDaddy Hosted WordPress Login Flow

When WordPress is hosted on GoDaddy, the login page shows a "Log in with GoDaddy" SSO button by default. To use traditional WordPress credentials:

```python
# Click "Log in with username and password" link first
password_login_link = page.get_by_text("Log in with username and password")
if password_login_link.count() > 0:
    password_login_link.click()
    page.wait_for_timeout(2000)  # Wait for form to appear
```

### 2. Direct Elementor Editor Access

Skip the WordPress editor entirely - go directly to Elementor:

```python
# Post ID can be found in URL or pages list
post_id = 174
page.goto(f"https://example.com/wp-admin/post.php?post={post_id}&action=elementor")
page.wait_for_timeout(10000)  # Elementor loads slowly
page.wait_for_selector("#elementor-panel", timeout=30000)
```

### 3. Elementor Preview Iframe Pattern

Elementor content lives inside an iframe. Use `frame_locator()`:

```python
# Correct way to access Elementor preview content
frame = page.frame_locator("#elementor-preview-iframe")
sections = frame.locator(".elementor-section")
widgets = frame.locator(".elementor-widget")
```

### 4. Don't Use `wait_for_load_state("networkidle")` After Login

WordPress login triggers complex redirects. Use fixed timeouts or URL waits instead:

```python
# BAD - times out
page.wait_for_load_state("networkidle")

# GOOD - wait for specific URL pattern
try:
    page.wait_for_url("**/wp-admin/**", timeout=15000)
except:
    pass
page.wait_for_timeout(3000)
```

### 5. Capturing Full Page Screenshots in Elementor

Keyboard navigation works for scrolling the preview:

```python
preview_area = page.locator("#elementor-preview")
preview_area.click()  # Focus the preview
page.keyboard.press("End")  # Scroll to bottom
page.keyboard.press("PageDown")  # Scroll incrementally
```

### 6. Preview URL Pattern

WordPress draft preview URLs follow this pattern:
```
https://example.com/?page_id={POST_ID}&preview=true
```

## File Paths

- Scripts created: `/home/jared/projects/AI-CIV/aether/tools/wp_admin_recon.py`
- Scripts created: `/home/jared/projects/AI-CIV/aether/tools/wp_purebrain20_inspect.py`
- Scripts created: `/home/jared/projects/AI-CIV/aether/tools/wp_elementor_view.py`
- Screenshots: `/home/jared/projects/AI-CIV/aether/sandbox/wp_recon/`
- Report: `/home/jared/projects/AI-CIV/aether/sandbox/wp_recon/PUREBRAIN-2.0-RECON-REPORT.md`

## When to Apply

- WordPress admin backend testing
- Elementor page analysis
- Pre-integration reconnaissance
- Content auditing before feature additions

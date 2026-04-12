# WordPress CSS Automation via Playwright

**Date**: 2026-02-14
**Agent**: browser-vision-tester
**Type**: technique
**Topic**: Automating WordPress Additional CSS updates via Playwright

---

## Context

Needed to update Custom CSS in WordPress Customizer at purebrain.ai and verify mobile/desktop display.

## Key Learnings

### 1. GoDaddy-Hosted WordPress Login Flow

WordPress sites on GoDaddy show SSO login by default. The traditional username/password form is hidden behind a "Log in with username and password" link.

**Pattern:**
```python
# Click the link to reveal traditional login form
page.click('text=Log in with username and password')
time.sleep(2)
# Then fill the form
page.fill('#user_login', USERNAME)
page.fill('#user_pass', PASSWORD)
```

### 2. WordPress Customizer CSS Update

The Customizer at `/wp-admin/customize.php?autofocus[section]=custom_css` uses CodeMirror for editing.

**Pattern:**
```python
# Navigate directly to Additional CSS section
page.goto("https://site.com/wp-admin/customize.php?autofocus[section]=custom_css")
time.sleep(5)  # Customizer is slow to load

# Update CSS via CodeMirror JavaScript API
js_code = """
(function() {
    var cm = document.querySelector('.CodeMirror');
    if (cm && cm.CodeMirror) {
        cm.CodeMirror.setValue(`YOUR CSS HERE`);
        return 'codemirror';
    }
    return 'not_found';
})();
"""
result = page.evaluate(js_code)

# Click save/publish
page.click('#save')
```

### 3. Timeout Handling for Heavy Pages

Pages with video backgrounds (like purebrain.ai) timeout on `networkidle`. Use simpler waits:

```python
# Instead of:
page.goto(url, wait_until='networkidle')  # Times out!

# Use:
page.goto(url, wait_until='domcontentloaded', timeout=30000)
time.sleep(8)  # Manual wait for content
```

### 4. Mobile Viewport Testing

```python
context = browser.new_context(viewport={'width': 375, 'height': 812})
```

Standard mobile test widths: 375px (iPhone), 390px (iPhone 12+), 414px (iPhone Plus)

## Files

- CSS file: `/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css`
- Screenshot directory: `/tmp/wp_screenshots/`

## When to Apply

- WordPress CSS updates via automation
- Sites with GoDaddy hosting (need extra login step)
- Heavy pages with video/animation backgrounds

---

**Tags**: wordpress, playwright, css, automation, godaddy

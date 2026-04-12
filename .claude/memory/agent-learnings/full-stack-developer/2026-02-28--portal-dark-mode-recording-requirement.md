# Memory: Portal Demo — Dark Mode Requirement (2026-02-28)

**Date**: 2026-02-28
**Type**: requirement + pattern
**Topic**: Portal demo video must always record in dark mode

---

## Requirement

Jared explicitly stated (2026-02-28):
> "make sure demo is in dark mode! flip it on in the portal."

ALL portal demo recording must have dark mode active before any frame is captured.

---

## How the Portal Theme System Works

File: `docs/from-telegram/pure-brain-v8-aether-dashboard.html`

- **Dark = DEFAULT** — no `data-theme` attribute on `<html>` = dark mode
- **Light mode** = `data-theme="light"` set on `<html>` (`document.documentElement`)
- `setThemePreference('dark')` — saves `pb_theme='dark'` to localStorage, calls `applyTheme()`
- `applyTheme('dark')` — calls `document.documentElement.removeAttribute('data-theme')`
- `applyTheme('light')` — calls `document.documentElement.setAttribute('data-theme', 'light')`

CSS override rules scoped under `[data-theme="light"]` only — dark styles are base styles.

## The Fix Added to portal_demo_recorder.py

After page load + 2000ms wait, inject before any DEMO_SEQUENCE steps:

```python
page.evaluate("""
    localStorage.setItem('pb_theme', 'dark');
    if (typeof setThemePreference === 'function') {
        setThemePreference('dark');
    } else if (typeof applyTheme === 'function') {
        applyTheme('dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
""")
page.wait_for_timeout(600)

# Verify
theme_attr = page.evaluate("document.documentElement.getAttribute('data-theme')")
# null/None/absent = dark mode active. 'light' = problem.
```

## File Changed

`/home/jared/projects/AI-CIV/aether/tools/portal_demo_recorder.py`
Lines 129-173: dark mode enforcement block

---

**Tags**: playwright, dark-mode, portal, recording, video, theme

# GoLogin Wrapper — MVP SCOPE (from Jared via Chy)

**SCOPE REDUCTION**: MVP is Indiegogo-only. Not full GoLogin parity.

## MVP Requirements (ONLY these 4 things):

1. **ONE profile** that can log into Indiegogo and stay logged in
2. **Fingerprint spoofing** so it looks like a real browser (Camoufox handles this)
3. **Session persistence** so cookies survive restarts (user data dir)
4. **Playwright API** so Chy's campaign automation scripts can drive it

## What is NOT in MVP:

- No multi-platform support
- No proxy rotation matrix
- No profile management UI
- No multiple profiles
- No CLI tool with create/list/delete
- No complex fingerprint database

## MVP Deliverable:

A single Python module that:
```python
from indiegogo_browser import get_browser

# Returns a Playwright browser + page with:
# - Camoufox fingerprint spoofing active
# - Persistent cookies/session from last run
# - Ready to navigate to indiegogo.com
browser, page = get_browser()
page.goto("https://www.indiegogo.com")
# ... automation here
browser.close()
```

That's it. Make Indiegogo work cleanly and undetectably.
We generalize after the campaign proves the pattern.

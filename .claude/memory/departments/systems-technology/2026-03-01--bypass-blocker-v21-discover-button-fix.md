# Bypass Blocker v2.1 - Discover Button Fix
Date: 2026-03-01

## Root Cause
Bypass Blocker v2.0 used Object.defineProperty to wrap window.showPersonalizedCapabilities. This intercepted the function assignment (via set trap) and returned a once-only wrapper from the get trap. When the chatbox did window.showPersonalizedCapabilities = showPersonalizedCapabilities, the set trap captured it. But when the button called window.showPersonalizedCapabilities(), the get trap returned the once-only wrapper which fired once on first call but would be blocked on duplicates. The bug is the get trap fires BEFORE the actual function is fully assigned/ready.

## Fix Applied
v2.1 removes the Object.defineProperty guard entirely. Methods 1, 2, 3 (addEventListener blocking and URL cleanup) are preserved.

## Pages Modified
- Page 688 (pay-test-sandbox-2)
- Page 689 (pay-test-2)

## Pages Untouched (confirmed)
- Page 11 (homepage) - still v2.0
- Page 1128 (backup) - no versioned blocker found

## Deployment Method
elementor_data JSON string replacement via WP REST API POST /wp/v2/pages/{id}. Script is inside first widget's settings.html (full HTML document widget). Elementor cache cleared after deploy.

## Verification
v2.1 confirmed in both pages via API. Object.defineProperty not present. showPersonalizedCapabilities count=5 (comment, onclick, function def, 2x window assignments). Pages 11 and 1128 untouched (still v2.0).

## Pattern: Elementor HTML Widget + Script Location
The bypass blocker lives inside a massive self-contained HTML document stored as an Elementor
HTML widget (elType: widget, settings.html). This full HTML document (with <head> and <body>)
is stored as a string in _elementor_data. Scripts in the <head> of this embedded document
DO execute in the page context when Elementor renders the widget (via innerHTML injection).

The script is NOT visible in a static HTTP fetch because Elementor renders the widget
asynchronously via JS. The static page fetch shows the outer WordPress HTML, not the
Elementor-injected widget content.

## Object.defineProperty Lesson
Using Object.defineProperty to wrap window functions is fragile:
- The set trap fires when any code does: window.showPersonalizedCapabilities = fn
- The get trap returns the wrapper, not the original fn
- If the function is assigned AFTER the defineProperty call, the get trap fires before
  the set trap has been given the real function (origSPC = null initially)
- Result: button click calls the wrapper, origSPC is null, function does nothing

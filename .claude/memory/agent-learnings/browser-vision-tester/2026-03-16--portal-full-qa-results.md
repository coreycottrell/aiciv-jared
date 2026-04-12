# Portal Full QA - March 16 2026 Results

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: operational + technique

## Context

Full portal QA audit against http://localhost:8097 following CTO QA plan. 12 suites, 47 test cases. Also tested investor page chat at purebrain.ai/investors/.

## Summary

44/47 PASS. 1 FAIL (Fleet nav hidden by design). 2 WARN (reply-btn hover-only, CORS inconsistency).

## Key Findings

### CRITICAL: Investor Page Gate is CSS-Only (P1 Security)
- The gate at purebrain.ai/investors/ is `position: fixed; z-index: 9999` overlay
- ALL content sections behind it are `display: block; visibility: visible`
- Anyone with dev tools can remove the gate in 5 seconds
- Fix: Server-side render gated sections only after access code validation

### Fleet Nav Hidden by Inline Style (P3)
- `div[data-panel="fleet"]` has `style="display: none;"` inline
- Panel itself WORKS when JS-clicked - just nav is hidden
- This is single-instance deployment behavior, likely intentional
- Playwright timeout on `div[data-panel="fleet"]` click because element is display:none

### Commands Panel Placeholder RESOLVED
- "your-server" placeholder was a known P3 issue
- It is now showing real data: IP 89.167.19.20, SSH port 22, user jared

### Investor API CORS Behavior
- OPTIONS preflight returns `Access-Control-Allow-Origin: https://purebrain.ai` (specific)
- Actual POST from other origins returns `Access-Control-Allow-Origin: *` (wildcard)
- Inconsistency - likely accidental config

## Playwright Patterns for This Portal

### Login
```python
await page.goto("http://localhost:8097", wait_until="domcontentloaded")
await page.fill("input[type='password']", TOKEN)
await page.click(".pb-signin-btn")
await page.wait_for_timeout(5000)  # Full history load
```

### Panel Navigation
```python
await page.click(f"div[data-panel='{panel_id}']", timeout=3000)
await page.wait_for_timeout(1800)
is_active = await page.evaluate(f"(function(){{ return document.getElementById('panel-{panel_id}')?.classList.contains('active') || false; }})()")
```

### JavaScript Evaluate - Use IIFE Pattern
```python
# WRONG - causes "Illegal return statement"
await page.evaluate("const el = ...; return el?.value")

# CORRECT - always wrap in IIFE
await page.evaluate("(function(){ return document.getElementById('thing')?.value; })()")
```

### Reply Button - Hover Only
- `.reply-btn` DOM count is 0 when not hovering (CSS opacity:0)
- Hover to reveal, then click - or confirm via `.msg-quote-block` existence

## Performance Baseline
- DOMContentLoaded: 1.24s
- JS Heap after all 13 panels: 15MB used / 17MB total (no leaks)
- Settings modal: 490ms open time
- Chat history: 200 messages, loads in ~5s

## CTX Gauge
- Now showing "90k / 200k" (was N/A in prior sessions)
- Gauge bar shows green fill

## Investor Page Chat (purebrain.ai/investors/)
- Auto-greeting: "Welcome. I'm Aether, Pure Technology's AI co-CEO..."
- 4 suggestion pills: What is PureBrain?, What are the financials?, How does it compare to ChatGPT?, Tell me about the raise
- Tier 1 responses stream immediately
- Tier 2 (sensitive questions like MRR) triggers approval gate email field
- Chat section is `#aether-chat-root`, textarea is `#aether-input`

## Files
- Report: `exports/departments/dept-systems-technology/2026-03-16--portal-qa-results.md`
- Screenshots: `/tmp/portal-qa-2026-03-16/` (31 files)

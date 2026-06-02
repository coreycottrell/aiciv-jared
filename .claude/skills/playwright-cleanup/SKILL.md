---
name: playwright-cleanup
description: Kill stale Playwright/Chromium processes after browser automation to prevent container memory/disk exhaustion
category: infrastructure
triggers:
  - after any Playwright browser session
  - when container feels sluggish or OOM errors appear
  - during BOOP health checks
agents:
  - browser-vision-tester
  - the-conductor
  - coder
  - qa-engineer
status: provisional
tick_count: 0
last_used: 2026-05-21
introduced: 2026-05-21
---

# Playwright Browser Cleanup

## When to Use
- After ANY Playwright browser automation session (screenshots, testing, scraping, vision loops)
- When container memory usage is high or sluggish
- During periodic BOOP health sweeps
- Before reporting "task complete" on any browser-automation work

## Why This Matters
Playwright spawns background Chromium processes that persist after your script ends. Each stale browser instance consumes 200-500MB RAM and disk. Left unchecked, they exhaust container resources within hours.

## Steps

### 1. In-Code Cleanup (MANDATORY after every Playwright session)
```python
# Always close in finally block
try:
    # ... your playwright work ...
finally:
    if page: await page.close()
    if context: await context.close()
    if browser: await browser.close()
    if playwright: await playwright.stop()
```

### 2. Shell Cleanup (run after sessions or when diagnosing sluggishness)
```bash
pkill -f chromium
pkill -f playwright
```

### 3. Verify Nothing Lingering
```bash
ps aux | grep -E "chromium|playwright" | grep -v grep
# Should return empty. Any results = stale processes to kill.
```

### 4. Nuclear Option (container emergency)
```bash
pkill -9 -f chromium
pkill -9 -f playwright
rm -rf /tmp/playwright-*
```

## Success Criteria
- `ps aux | grep -E "chromium|playwright" | grep -v grep` returns empty
- Container memory usage returns to baseline

## Integration
- browser-vision-tester agent MUST run step 2+3 after every vision loop
- BOOP health checks SHOULD include step 3 as a canary
- Any agent using Playwright MUST include step 1 in their workflow

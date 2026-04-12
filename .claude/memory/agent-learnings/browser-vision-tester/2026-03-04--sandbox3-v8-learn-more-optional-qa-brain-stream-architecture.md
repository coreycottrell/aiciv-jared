# Sandbox-3 v8: Learn More = Optional Q&A + Brain Stream Architecture Discovery

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: gotcha + architecture + pattern
**Tags**: sandbox3, brain-stream, learn-more, optional-qa, architecture, elementor, fixed-chatbox

---

## Context

v8 E2E run (definitive run per Jared mission brief). Goal: reach chatbox state showing greyed "ENTER [AI NAME]'S BRAIN STREAM" button. Script: `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_v8_brain_stream.py`

---

## KEY DISCOVERY 1: "Learn more" Inside PTC = Optional Q&A (NOT Navigation)

After orange CTA click, chatbox shows "Welcome to the Family!" card with "Learn more" button.

**Expected**: "Learn more" would navigate somewhere (underlying page, portal)
**Actual**: "Learn more" triggers additional OPTIONAL enrichment Q&A INSIDE the chatbox

Follow-on messages after "Learn more" click:
- "Perfect. The more Your AI knows about you, the more precisely your AI gets shaped."
- "I have a few more questions — totally optional, but each one gives Your AI more to work with."
- "How do you prefer to work? Are you more of a big-picture thinker, or do you like drilling into the details?"
- Skip button available

The input remains ACTIVE after orange CTA + Learn more. Send button enabled.

**Class of "Learn more" button**: `ptc-btn ptc-btn--primary` (inside #pay-test-post-payment)

---

## KEY DISCOVERY 2: Brain Stream Button Architecture

The `#pb-brain-stream-wrapper` is an **Elementor page element** (NOT inside the fixed chatbox).

```
Page Structure:
├── #pay-test-post-payment (position:fixed, z-index:999999) ← CHATBOX (covers everything)
│   ├── .ptc-header (Chat with Your AI)
│   ├── #ptc-messages (scrollable)
│   ├── #ptc-input-row (input + send)
│   └── [optional Q&A + Welcome card + Learn more btn]
│
└── Elementor page content (behind chatbox, scrollable)
    └── ... many sections ...
    └── #pb-brain-stream-wrapper (y=8599+ in document, opacity=0.35 when greyed)
        ├── #pb-brain-stream-eyebrow ("Your AI is Ready")
        ├── #pb-brain-stream-btn ("Click to Connect to Your AI's Brain Stream")
        └── #pb-brain-stream-subtext ("Your personalized AI portal is ready...")
```

**To capture brain stream wrapper via element screenshot**:
1. First `scrollIntoView({behavior:'instant', block:'center'})` on the wrapper
2. Then `el.screenshot()` — this works even when chatbox is overlaid
3. Alternatively, hide chatbox (`ptc.style.display='none'`) then scroll to wrapper

**Greyed state DOM signature**:
```
#pb-brain-stream-wrapper: opacity=0.35, pointer-events=none, display=block
#pb-brain-stream-btn: cursor=not-allowed, background=rgb(51,51,51), pointer-events=none
```

---

## KEY DISCOVERY 3: Jared's Reference Screenshot Shows Different Variant

Jared's reference shows "ENTER KEEN'S BRAIN STREAM" INSIDE the chatbox.

Sandbox-3 shows "Click to Connect to Your AI's Brain Stream" on the UNDERLYING page.

**Hypothesis**: Jared's reference may be from:
- A real user flow (with AI naming step that sandbox-3 skips)
- A newer version of the plugin
- Or a different page (pay-test vs real production)

The chatbox in Jared's reference shows the button INSIDE the message stream, with the input area still visible below it (greyed). This looks like a final chatbox message card, not a separate Elementor element.

**Action needed**: Confirm from Jared if there's a "brain stream button inside chatbox" mode vs the current Elementor page element implementation.

---

## Capture Pattern for Brain Stream Wrapper

```python
# After orange CTA click + optional interactions:

# Method 1: Element screenshot after scrollIntoView
await page.evaluate("""(function(){
    var w = document.getElementById('pb-brain-stream-wrapper');
    if (w) w.scrollIntoView({behavior: 'instant', block: 'center'});
})()""")
await asyncio.sleep(1)
el = await page.query_selector('#pb-brain-stream-wrapper')
if el:
    await el.screenshot(path=output_path)

# Method 2: Full page after hiding chatbox
await page.evaluate("""document.getElementById('pay-test-post-payment').style.display='none'""")
# scroll to wrapper
await page.evaluate("""document.getElementById('pb-brain-stream-wrapper').scrollIntoView()""")
await page.screenshot(path=output_path)
# restore
await page.evaluate("""document.getElementById('pay-test-post-payment').style.display=''""")

# Verify greyed state
state = await page.evaluate("""(function(){
    var w = document.getElementById('pb-brain-stream-wrapper');
    var b = document.getElementById('pb-brain-stream-btn');
    return {
        wrapperOpacity: w ? getComputedStyle(w).opacity : null,
        wrapperPointerEvents: w ? getComputedStyle(w).pointerEvents : null,
        btnText: b ? b.textContent.trim() : null,
        btnCursor: b ? getComputedStyle(b).cursor : null,
        btnBackground: b ? getComputedStyle(b).backgroundColor : null
    };
})()""")
# Expect: wrapperOpacity='0.35', btnCursor='not-allowed', btnBackground='rgb(51, 51, 51)'
```

---

## Full Flow Timing (v8, JS Simulation)

| Stage | Approximate Time |
|-------|-----------------|
| Page load + password | ~29s |
| Payment simulation | ~35s |
| Chatbox active | ~43s |
| All 5 Q&A complete | ~137s |
| All 10 slides clicked | ~186s |
| Orange CTA clicked | ~210s |
| Brain stream wrapper confirmed | ~215s |

Total: 294 seconds, 30 screenshots.

---

## Reference

- Script: `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_v8_brain_stream.py`
- Report: `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-v8-report-20260304.md`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-complete-flow/`
- Key brain stream screenshot: `27-18-BRAIN-STREAM-WRAPPER-ZOOMED.png`

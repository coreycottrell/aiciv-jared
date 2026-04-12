# Sandbox-3 Post-Fix Verification: All 3 Bugs Confirmed Fixed

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: synthesis + verification + pattern
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox3, bug-fix, verification, dynamic-name, send-button, brain-stream

---

## Context

Ran post-fix E2E verification of `https://purebrain.ai/pay-test-sandbox-3/` to confirm 3 specific bug fixes were working.

Script: `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_post_fix_verification.py`
Screenshots: `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-post-fix-screenshots/`
Report: `/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-post-fix-report-20260304.md`
Total time: 230 seconds | 26 screenshots

---

## Fix 1: Dynamic AI Name — PASS

**Bug**: Hardcoded "AICIV" appeared in post-payment copy
**Fix verified**: Zero instances of "AICIV" on page
**What shows instead**: "Your AI" throughout all personalized copy
- "Your AI partner, Your AI, is being set up" (timeline card)
- "Your Pure Brain, Your AI, is being shaped by your answers" (timeline card)
- "Your AI's Brain Stream (portal) will be ready for you to log in"
- Chatbox header: "Chat with Your AI"
- Final AI message signature: "— Your AI"

**Key insight**: Sandbox-3 does NOT ask for an AI name during Q&A. The 5 Q&A questions are: full name, email, company, role, goal. The "Your AI" placeholder IS the correct dynamic behavior for sandbox-3 (different from sandbox-2 which may have had an AI name field).

---

## Fix 2: Send Button Disabled — PASS

**Bug**: Send button remained active after clicking "Your AI is ready" orange button
**Fix verified**: After clicking orange CTA, input and send button are disabled

DOM state confirmed:
- `#ptc-input`: `disabled=true`, `readOnly=true`
- `#ptc-send-btn`: `disabled=true`, `opacity=0.45`
- Input row: display=flex (visible) but locked
- Placeholder: "Message Your AI..."

Visual appearance: Dark grey send button (low contrast, clearly inactive)

---

## Fix 3: Brain Stream Button Greyed — PASS

**Bug**: Brain Stream button was active/clickable when it should wait for backend
**Fix verified**: Button in greyed state with correct CSS properties

DOM state confirmed:
- `#pb-brain-stream-wrapper`: `opacity=0.35`, `pointer-events=none`
- `#pb-brain-stream-btn`: `pointer-events=none`, `cursor=not-allowed`, `background=rgb(51,51,51)` (dark grey)
- Animation: `none` (no pulsing)
- Button text: "Click to Connect to Your AI's Brain Stream" (dynamic "Your AI" - not KEEN or AICIV)

**Expected behavior note**: Button does not light up in JS simulation tests because no real seed sent to Witness. When real payment completes birth pipeline, button should activate. Greyed = correct for simulation.

---

## Confirmed Q&A Flow (Sandbox-3 v2026-03-04)

```
Q1: "Let's start simple. What's your full name?"
Q2: "Nice to meet you, [name]. What email should Your AI use to reach you?"
Q3: "Are you working within a company or organization? If so, what's its name? (You can skip this)"
Q4: "What's your role or title? What do you actually do day-to-day? (Optional.)"
Q5: "Here's the one that matters most. If Your AI could only do one thing exceptionally well for you — what would make the biggest difference in your work or life?"
```

Sandbox-3 uses user's first name from Q1 in Q2 prompt ("Nice to meet you, [first name]").

---

## Timing (JS Simulation Path)

| Stage | Seconds from script start |
|-------|--------------------------|
| Page load | ~0s |
| Password entered | ~10s |
| Page unlocked | ~24s |
| Payment simulated | ~40s |
| Chatbox active | ~41s |
| All 5 Q&A complete | ~134s |
| All 10 slides clicked | ~170s |
| "Your AI is ready" button found | ~184s |
| Fix verification phase | ~197-230s |

---

## Post-Fix Verification Technique

The most efficient approach for verifying these 3 specific fixes:

```python
# Fix 1: Check for AICIV vs dynamic name
name_check = await page.evaluate("""(function(){
    var text = document.body.innerText;
    return {
        hasAICIV: text.toUpperCase().includes('AICIV'),
        hasYourAI: text.toUpperCase().includes('YOUR AI'),
    };
})()""")

# Fix 2: Check send button state
send_state = await page.evaluate("""(function(){
    var btn = document.getElementById('ptc-send-btn') || document.querySelector('.ptc-send-btn');
    var input = document.getElementById('ptc-input');
    return {
        sendBtnDisabled: btn ? btn.disabled : null,
        sendBtnOpacity: btn ? window.getComputedStyle(btn).opacity : null,
        inputDisabled: input ? input.disabled : null,
    };
})()""")

# Fix 3: Check brain stream state
brain_check = await page.evaluate("""(function(){
    var wrapper = document.getElementById('pb-brain-stream-wrapper');
    var btn = document.getElementById('pb-brain-stream-btn');
    return {
        wrapperOpacity: wrapper ? window.getComputedStyle(wrapper).opacity : null,
        wrapperPointerEvents: wrapper ? window.getComputedStyle(wrapper).pointerEvents : null,
        btnCursor: btn ? window.getComputedStyle(btn).cursor : null,
    };
})()""")
```

Key IDs confirmed: `#pb-brain-stream-wrapper`, `#pb-brain-stream-btn`

---

## Full E2E Flow State (Post-Fix)

Complete flow works end-to-end:
1. Password gate: PASS
2. Payment simulation: PASS (sanitizeText bug fixed in earlier sprint)
3. Chatbox activation: PASS
4. 5 Q&A: PASS
5. 10 slides: PASS (slides begin during Q5 in parallel)
6. "Your AI is ready" orange button: PASS
7. Post-CTA state with 3 fixes: ALL PASS

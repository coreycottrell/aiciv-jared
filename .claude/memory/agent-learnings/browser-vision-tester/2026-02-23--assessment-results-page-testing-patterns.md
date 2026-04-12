# Memory: AI Partnership Assessment Results Page Testing Patterns
**Date**: 2026-02-23
**Type**: teaching + operational
**Topic**: Playwright automation for multi-step quiz with dynamic DOM, single-page quiz flow

---

## Context

Tested https://purebrain.ai/ai-partnership-assessment/ - a 6-question quiz with contact form, scoring logic, and results display including benchmark comparison and shareable score card.

---

## Key Learnings

### 1. Single-Page Quiz with All Questions Pre-Loaded in DOM

**Problem**: All questions' options are in the DOM from page load. Simple `page.locator('.option')` finds ALL options (20 total), not just the 4 visible ones.

**Solution**: Use JavaScript `getBoundingClientRect()` to filter for truly visible elements:

```javascript
const allOptions = document.querySelectorAll('.option');
const visibleOptions = Array.from(allOptions).filter(el => {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 &&
           style.display !== 'none' &&
           style.visibility !== 'hidden' &&
           rect.top >= 0 && rect.top < window.innerHeight * 3;
});
```

**When to apply**: Any assessment/quiz page where multiple questions may be pre-rendered.

### 2. `networkidle` vs `domcontentloaded` for Elementor Pages

**Problem**: `page.goto(url, wait_until="networkidle")` times out on purebrain.ai because the page has ongoing network activity (Google Fonts, Elementor iframes, etc.)

**Solution**: Always use `wait_until="domcontentloaded"` + manual `time.sleep(4-5)` for Elementor pages:

```python
page.goto(url, wait_until="domcontentloaded", timeout=45000)
time.sleep(5)  # Wait for JS quiz initialization
```

### 3. Form Fields with IDs - Use Native Playwright Fill

Q6 contact form fields:
- `#name` - text input (placeholder: "John Smith")
- `#email` - email input (placeholder: "john@company.com")
- `#company` - text input (placeholder: "Acme Corp")

Best approach: `page.fill('#name', 'Test User')` (native Playwright handles React state events automatically).

### 4. Button State During Submission

When you click "Get My Results":
- Button text changes to "Submitting..." immediately
- Google Forms iframe loads in background
- Results appear after ~8-10 seconds

Detection: `click_button_text(page, "get my results")` works but after click the button becomes "Submitting...".

### 5. Score Calculation

Answering all D options = score of 8/10, tier = "AI READY"
- Benchmark: "You scored higher than 71% of professionals"
- Answering mix of low options = 2/10, tier = "JUST STARTING"
- D options are designed as the most "AI-forward" answers

### 6. Results Page Structure

After submission, same URL with results shown:
- Score display: `"8 / 10 AI Readiness Score"` with tier badge
- Benchmark bar: shows relative position
- Benchmark text: `"You scored higher than 71% of professionals..."`
- CTA: "Begin Your AI Awakening" button
- Share section: "Download Score Card" button + "Copy Share Message" button
- Score card canvas: Shows branded 8/10 preview card for sharing

### 7. Download Score Card Button Renders as Canvas

The "Download Score Card" button contains a canvas element for the download icon. In screenshots it appears as a blue rectangle. The canvas preview card below it renders correctly with the score, tier, and PureBrain branding.

### 8. Scrolling to Capture Share Section

Share section is at ~718px from page top (scroll position). To capture it:

```python
share_y = page.evaluate("""
    () => {
        const dlBtn = Array.from(document.querySelectorAll('button')).find(b =>
            b.innerText.toLowerCase().includes('download'));
        if (dlBtn) return dlBtn.getBoundingClientRect().top + window.scrollY - 100;
        return window.scrollY + 600;
    }
""")
page.evaluate(f"window.scrollTo(0, {share_y})")
time.sleep(2)
```

---

## File Paths

- Test script v3 (working): `tools/test_assessment_v3.py`
- Final shots script: `tools/test_assessment_final_shots.py`
- Results screenshot: `exports/screenshots/assessment_competitive_results.png`
- Share screenshot: `exports/screenshots/assessment_competitive_share.png`

---

## Timing Reference

- Initial page load: 5 seconds
- After Continue click (question change): 2-2.5 seconds
- After Get My Results click: 8-10 seconds for results to appear
- Scroll + canvas render: 2 seconds

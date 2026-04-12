# Memory: Invitation Page Full Visual Audit
**Date**: 2026-02-26
**Type**: operational + technique + gotcha
**Topic**: WP password-protected landing page audit with scroll animation override technique

---

## Task Summary

Full visual audit of https://purebrain.ai/invitation/ — 7-section invite-only landing page with WP password protection (purebrain25). Tested all sections, brand colors, CTA links, countdown timer, pricing cards, testimonial, Jared signature.

---

## Key Technique: Force IntersectionObserver Animations Visible

The biggest gotcha on this page — and likely any page using scroll-triggered animations:

**Problem**: Elements with `pb-fade-in` class are rendered `opacity: 0` until IntersectionObserver fires. In headless Playwright, the observer fires inconsistently or not at all. Multiple sweep screenshots at different scroll positions show pure black screens — the content exists in DOM but is invisible.

**Solution**: Inject a `<style>` override tag + manually set inline styles on all fade-in elements AFTER page load:

```python
FORCE_VISIBLE_JS = """
() => {
    const style = document.createElement('style');
    style.textContent = `
        .pb-fade-in, .pb-fade-up, [class*="fade"] {
            opacity: 1 !important;
            transform: none !important;
            visibility: visible !important;
        }
    `;
    document.head.appendChild(style);

    document.querySelectorAll('.pb-fade-in, .pb-fade-up').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.style.visibility = 'visible';
    });

    return document.querySelectorAll('.pb-fade-in').length;
}
"""
```

**Must re-apply after each scroll** — some pages re-calculate animation state on scroll events.

**Apply before every full_page=True screenshot** — the full_page screenshot renders the entire page but animations at y>viewport will still be invisible without the override.

---

## className.substring Error — SVG Elements

**Problem**: `page.evaluate` JS that calls `el.className.substring()` throws `TypeError: c.className.substring is not a function` when SVG elements are in the querySelectorAll result set.

SVG elements return an `SVGAnimatedString` object for `className`, not a plain string.

**Fix**: Always guard with:
```javascript
const cls = (typeof el.className === 'string') ? el.className : (el.className.baseVal || '');
```

Or filter SVG elements:
```javascript
Array.from(document.querySelectorAll('[class*="card"]'))
    .filter(el => el instanceof HTMLElement)
```

---

## WP Password Protection Pattern (reusable)

- Input selector: `input[type='password']`
- Submit: `input[type='submit']` (not `button[type='submit']`)
- Wait 10 seconds after submit for Elementor to load
- Cookie `wp-postpass_[hash]` persists within session — don't need to re-enter for subsequent pages in same browser context

---

## Countdown Timer Finding

Both countdown instances on the invitation page showed `00:00:00:00`. This is a critical issue to check on any page with a deadline timer. The deadline date must be set to a FUTURE date. Check the inline JS for:
```javascript
const deadline = new Date('2026-03-04T...'); // must be in the future
```

When the timer shows zeros, real users think the offer expired — conversion killer.

---

## DOM Inspection Patterns

**Find sections with their positions:**
```javascript
document.querySelectorAll('section').forEach((s, i) => {
    const cls = (typeof s.className === 'string' ? s.className : '');
    console.log(i, s.offsetTop, s.offsetHeight, cls.substring(0,40));
});
```

**Find all CTA links pointing to awakening:**
```javascript
document.querySelectorAll('a[href*="awakening"]').map(a => ({
    text: a.textContent.trim(),
    href: a.getAttribute('href')
}))
```

**Check CSS brand variables:**
```javascript
// Look for CSS custom properties in stylesheets
for (const sheet of document.styleSheets) {
    for (const rule of sheet.cssRules) {
        if (rule.cssText && rule.cssText.includes('--blue')) {
            console.log(rule.cssText.substring(0, 200));
        }
    }
}
```

---

## Page Structure (pb-invite-page)

7 sections, total page height 6219px at 1440px viewport:

| Section | Class | offsetTop | Height | H2 |
|---------|-------|-----------|--------|-----|
| 0 | pb-hero | 0 | 900 | (none) |
| 1 | pb-what | 900 | 836 | "An AI that knows..." |
| 2 | pb-awakening | 1736 | 989 | "Your First Conversation..." |
| 3 | pb-pricing | 2725 | 903 | "Pre-Launch Pricing..." |
| 4 | pb-proof | 3629 | 611 | (testimonial) |
| 5 | pb-urgency | 4240 | 925 | "Only 25 Spots..." |
| 6 | pb-final-cta | 5165 | 920 | "Don't Let Someone Else..." |

**Scroll positions for screenshots** (expressed as % of total height):
- 0%: Hero
- 12%: Feature cards
- 22%: Cards lower + awakening header
- 30%: Awakening + chat mockup
- 40%: Step 4 + pricing header
- 50%: Pricing cards
- 60%: Card details + testimonial
- 68%: Urgency section
- 76-84%: Fact blocks
- 90-100%: Final CTA + signature

---

## CSP Errors (Expected/Not Bugs)

8 CSP errors from headless testing — all from:
- GTM (`googletagmanager.com`) blocked
- GoDaddy analytics (`wsimg.com`) blocked

These are not application errors. They indicate GTM may not fire under strict CSP. Worth checking if GA4 conversion events are tracking on this page via GTM tags.

---

## Files

- Test script v1: `tools/test_invitation_page.py`
- Test script v2: `tools/test_invitation_page_v2.py`
- Force-visible script: `tools/test_invitation_force_visible.py`
- Report: `exports/invitation-page-visual-audit-2026-02-26.md`
- Screenshots: `exports/screenshots/invitation-audit-2026-02-26/` (37 files)

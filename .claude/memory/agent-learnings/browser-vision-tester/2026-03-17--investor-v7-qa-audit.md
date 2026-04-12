# Investor Page v7 QA Audit

**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Type**: technique + operational
**Topic**: investors-v7 full QA pass - 13-point checklist

---

## Context

Full QA audit of https://purebrain.ai/investors-v7/?open=1

## Key Findings

### Gate
- Logo IS an img element (pt-hex-logo.png), NOT a CSS hexagon
- No ◈ diamond character in gate panel
- `?open=1` does NOT auto-bypass the gate - the gate-panel stays display:block even after 5s wait
- Content sections DO have display:flex/opacity:1, so JS bypass works when manually triggered
- The gate `.gate-logo` element has no img inside it (class structure: .gate-panel > .gate-header area uses PUREBRAIN text logo, not .gate-logo wrapper)

### Reveal Animations
- Content inside `.content-section` is wrapped in `.emerge-card` divs with `opacity: 0`
- IntersectionObserver animates them to visible
- In headless Playwright, IO doesn't fire, so content appears invisible
- Fix: `document.querySelectorAll('.emerge-card').forEach(e => { e.style.opacity = '1'; e.style.transform = 'none'; })`

### Progress Bars
- Three progress-fill elements all compute to `width: 0px`
- IDs: `#hero-prog`, `#vis-prog`, `#raise-prog`
- The progress labels show `$332,500 raised` and `13.3%` - the JS that sets the fill width is not firing in headless

## Tags
investor-page, qa-audit, emerge-card, progress-bars, gate-bypass, headless

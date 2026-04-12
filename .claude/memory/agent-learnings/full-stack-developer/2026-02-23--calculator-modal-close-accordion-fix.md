# Memory: Calculator Modal X Button Fix + Accordion Auto-Collapse

**Date**: 2026-02-23
**Type**: teaching + operational
**Agent**: full-stack-developer
**Page**: https://purebrain.ai/ai-tool-stack-calculator/ (WP page 777)

---

## What Was Fixed

### Fix 1: Share Modal X Button Didn't Close

**Root Cause**: `<button>` without `type="button"` can behave unexpectedly in some browser contexts. The close event listener was correctly attached, but belt-and-suspenders approach was needed.

**Three-layer fix applied**:
1. Added `type="button"` to the button element (prevents default submit behavior)
2. Added `onclick="closeShareModal()"` inline (fires even if addEventListener fails)
3. Changed event listener to call `e.stopPropagation()` before `closeShareModal()` (prevents click from bubbling to overlay handler)

```html
<!-- BEFORE -->
<button class="calc-share-modal-close" id="calcShareModalClose" title="Close">✕</button>

<!-- AFTER -->
<button type="button" class="calc-share-modal-close" id="calcShareModalClose" title="Close" onclick="closeShareModal()">✕</button>
```

```javascript
// BEFORE
document.getElementById('calcShareModalClose').addEventListener('click', closeShareModal);

// AFTER
document.getElementById('calcShareModalClose').addEventListener('click', function(e) {
  e.stopPropagation();
  closeShareModal();
});
```

**Teaching**: When a modal close button doesn't work, apply all three layers: `type="button"`, `onclick` inline, and `e.stopPropagation()` in the listener. Overkill beats broken UX.

---

### Fix 2: Accordion Auto-Collapse for Categories

**Behavior before**: All categories could be open simultaneously. Clicking a header toggled it independently.

**Behavior after**: Accordion mode — when you open one category, all others automatically collapse.

**Code change** (in `handleCategoryClick`):

```javascript
// BEFORE
if (header) {
  const catId = header.dataset.cat;
  const catEl = document.getElementById('cat-' + catId);
  catEl.classList.toggle('calc-cat--open');
  return;
}

// AFTER
if (header) {
  const catId = header.dataset.cat;
  const catEl = document.getElementById('cat-' + catId);
  const isOpen = catEl.classList.contains('calc-cat--open');
  // Accordion: collapse all other open categories first
  document.querySelectorAll('.calc-category.calc-cat--open').forEach(el => {
    if (el !== catEl) el.classList.remove('calc-cat--open');
  });
  // Toggle the clicked one (if it was already open, close it; otherwise open it)
  catEl.classList.toggle('calc-cat--open', !isOpen);
  return;
}
```

**Teaching**: Accordion behavior needs to snapshot `isOpen` BEFORE collapsing others, then use `classList.toggle(class, boolean)` for explicit open/close. If you just `toggle()` after collapsing others, the state may be wrong if the target was in the "all open" collapse operation.

---

## Deployment

- Source file: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- WP page: 777 (elementor_canvas template)
- PUT via REST API returned HTTP 200
- Elementor cache cleared: HTTP 200
- Content deployed: 107,740 chars
- All 6 verification checks passed

## Verification Results

| Check | Result |
|-------|--------|
| `type="button"` on close btn | PASS |
| `onclick="closeShareModal()"` inline | PASS |
| `e.stopPropagation()` in listener | PASS |
| Accordion comment present | PASS |
| `isOpen` variable logic | PASS |
| `querySelectorAll('.calc-category.calc-cat--open')` | PASS |

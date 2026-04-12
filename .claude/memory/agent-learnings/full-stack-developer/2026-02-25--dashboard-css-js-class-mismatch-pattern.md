# Memory: CSS/JS Class Name Mismatch Pattern

**Date**: 2026-02-25
**Type**: teaching
**Topic**: Autocomplete dropdown invisible due to CSS class vs JS class mismatch

---

## The Bug

CSS defined `.autocomplete-list.open { display: block; }` but JavaScript used `classList.add('active')` / `classList.remove('active')`. The dropdown items were being populated correctly in the DOM but the list remained invisible because `display: none` was never overridden.

## Root Cause

When merging v2 (select dropdown) into v3 (text input with typeahead), the CSS was written with `.open` class but the JS copied from a different source used `.active`. Neither side was tested in isolation because the merge was too large for line-by-line review.

## Pattern to Watch For

Any time CSS visibility depends on a JS-toggled class, verify the class names match:
- Search CSS for the selector
- Search JS for the classList operations
- They MUST use the same class name

## Fix

Changed all 6 JS occurrences from `'active'` to `'open'` to match CSS.

---

**Tags**: css, javascript, class-mismatch, autocomplete, dashboard, debugging

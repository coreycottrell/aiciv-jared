# Waitlist Form Duplicate Submission Fix

**Date**: 2026-03-19
**Type**: teaching
**Topic**: Google Forms double-submission via dual send methods

## Root Cause

The `submitToWaitlist()` function in `exports/cf-pages-deploy/index.html` used TWO submission methods simultaneously:

1. **Image beacon (GET)**: `new Image(); img.src = formUrl + '?' + params.toString()`
2. **sendBeacon (POST)**: `navigator.sendBeacon(formUrl, formData)`

Both fired on every form submission, creating exactly 2 entries in the Google Sheet per user signup. The comment in the code labelled them "Method 1" and "Method 2" with sendBeacon described as a "backup" — but it wasn't conditional, it always fired.

## Fix Applied

Removed the `sendBeacon` block entirely. Kept only the image beacon GET method (which is CORS-immune and works reliably). The `URLSearchParams` block building the query string was already present and correct.

**File changed**: `exports/cf-pages-deploy/index.html` (lines ~10494-10513)

## Pattern: Double-submission detection

When Google Sheets shows duplicates, check if entries are:
- **Same timestamp**: Two handlers fired simultaneously (this case)
- **Offset by seconds**: Double-click or page reload

In this codebase, any `submitToWaitlist` function changes should be audited for multiple send methods.

## Verification

- `grep -n "sendBeacon" exports/cf-pages-deploy/index.html` returns 0 results post-fix
- Deployed to purebrain-staging: https://e14c5e92.purebrain-staging.pages.dev
- CF cache flush needed after deploy

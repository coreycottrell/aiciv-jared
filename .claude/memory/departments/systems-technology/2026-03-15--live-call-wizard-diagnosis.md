# Live Call Wizard — Diagnosis Report
**Date**: 2026-03-15
**Agent**: dept-systems-technology
**Page**: https://purebrain.ai/live-call/
**Page ID**: 1283 (WordPress)
**Severity**: HIGH — Page is non-functional for users

---

## Executive Summary

The Live Call Wizard page at `https://purebrain.ai/live-call/` is currently served via Cloudflare Pages from `exports/cf-pages-deploy/live-call/index.html`. The page DOES load and the HTML content IS present in the file, but **the main content area appears blank because all `.step-content` divs are hidden by CSS (`display: none`) and the JavaScript that activates the first step is failing to run correctly due to a double-nested HTML document structure.**

---

## Root Cause: Double-Nested HTML Document

The CF Pages file at:
```
/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/live-call/index.html
```

Has TWO complete HTML documents nested inside each other:

```
Line 1:  <!DOCTYPE html>          ← OUTER wrapper (CF Pages export shell)
Line 2:  <html lang="en">
Line 16: <body>
Line 18:   <!DOCTYPE html>        ← INNER wizard HTML (the actual app)
Line 19:   <html lang="en">
Line 1162:  <body>
             ... all wizard content ...
Line 2334: </body>
Line 2335: </html>
Line 2338: </body>                 ← outer wrapper closes
Line 2339: </html>
```

This structure was created when a "WP Export" wrapper was added around the original wizard HTML. The outer shell (lines 1–16) contains:
- A comment block with export metadata
- A `<body>` tag
- Then the FULL inner wizard HTML including its own `<!DOCTYPE>`, `<html>`, `<head>` (with all CSS/styles), and `<body>`

**Why this breaks the wizard:**

1. **CSS is inside the INNER `<head>` tag** — When a browser encounters a second `<!DOCTYPE>` inside a `<body>`, it stops parsing the inner `<head>` and treats its content as body content. The `<style>` blocks may not be processed correctly by all browsers.

2. **All `.step-content` divs are `display: none` by default** — The CSS rule is:
   ```css
   .step-content { display: none; }
   .step-content.active { display: block; }
   ```
   The JavaScript must call `goToStep(1)` on init to add the `.active` class to step 1. If the JS fails or runs in a broken DOM context, ALL steps stay hidden.

3. **The topbar/sidebar/footer render from static HTML** — This is why the user sees the header (`PUREBRAIN.ai`), sidebar label (`LIVE CALL WIZARD`), step counter (`Step 1/8`), and navigation buttons — those elements are in the outer shell structure or render without JS. But the main content requires JS to activate.

4. **The JS init sequence at the bottom of the file:**
   ```javascript
   startTimer();
   renderSidebar();
   renderProgressDots();
   loadNotes();
   loadProspectInfo();
   goToStep(1);
   ```
   This code is inside the INNER `</body>` but the outer document's DOM may not recognize the wizard's elements as part of the same valid document tree.

---

## Contributing Factors

### Factor 1: WordPress Content vs CF Pages
The URL `https://purebrain.ai/live-call/` is served by CF Pages (returns HTTP 200 directly, no redirect to WordPress). The WordPress page (ID 1283, at `/sales-playbook/live-call/`) is a separate page.

The CF Pages version was exported on **2026-03-10** and contains the double-wrapper artifact.

### Factor 2: No `<!-- wp:html -->` Wrapping Needed Here
The CF Pages version does not go through WordPress/wpautop at all, so wpautop injection is not a factor. The problem is purely structural.

### Factor 3: The Sidebar and Nav Render Without JS
These elements are static HTML:
- `.topbar` (PUREBRAIN.ai header) — static HTML
- `.sidebar-title` (LIVE CALL WIZARD label) — static HTML
- `.step-counter` (Step 1/8) — static HTML initially, JS updates it
- Previous/Next buttons — static HTML

This matches exactly what the user reports seeing: "header, sidebar label, step counter, buttons" — all static — but blank main content because it needs `.active` class added by JS.

---

## The Fix

The fix is straightforward: **strip the outer wrapper shell from the CF Pages export.**

The correct `live-call/index.html` should be the INNER wizard HTML only — starting with the wizard's own `<!DOCTYPE html>` and containing only one complete HTML document.

**What needs to be done:**

1. Take the inner HTML (lines 18 through 2335 of the current CF Pages file)
2. Make that the complete `index.html` for the CF Pages deploy
3. Redeploy to CF Pages

**The source of truth is:**
```
/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html
```

This file (2310 lines) contains the clean, single-document wizard HTML. The CF Pages version (2338 lines) has the extra 28-line outer wrapper causing the problem.

---

## Proposed Fix (for approval)

**Option A — Quick fix (recommended):**
Update `exports/cf-pages-deploy/live-call/index.html` to be identical to `exports/sales-call-wizard/index.html` (the clean source), then redeploy CF Pages.

**Option B — Extract inner content:**
Strip lines 1–17 (outer wrapper) and lines 2336–2339 (outer closing tags) from the CF Pages file.

Both options produce the same result. Option A is cleaner and easier to verify.

**Risk assessment**: Low. The fix removes invalid wrapping HTML that does not belong. The inner wizard HTML is complete and self-contained. No live WP content is being touched.

---

## Files Involved

| File | Role | Action Needed |
|------|------|---------------|
| `exports/cf-pages-deploy/live-call/index.html` | Currently deployed (broken — double DOCTYPE) | Replace with clean version |
| `exports/sales-call-wizard/index.html` | Source of truth (clean, working) | Copy to CF Pages path |
| `exports/sales-call-wizard/deploy-result.json` | Records WP page ID 1283 | No action |

---

## What Is NOT the Problem

- NOT a security plugin interference (CF Pages bypasses WP entirely)
- NOT a WordPress Elementor issue (this is CF Pages hosted)
- NOT missing JavaScript files (all JS is inline in the HTML)
- NOT a CSP/header issue (the page loads, CSS/JS is inline)
- NOT an API endpoint failure (wizard content is static HTML)
- NOT a WordPress password protection issue (CF Pages does its own password handling)

---

## Verification Plan

After fix is applied:
1. Curl the live page and confirm single `<!DOCTYPE html>` declaration
2. Confirm `.step-content#step-1` has `class="step-content active"` in rendered HTML (or JS applies it on load)
3. Visual confirmation that Step 1 content renders (the "Open Strong" / "The Hook" section)

---

## Memory Written
Path: `.claude/memory/departments/systems-technology/2026-03-15--live-call-wizard-diagnosis.md`
Type: diagnosis
Topic: Double-nested HTML document causing blank wizard content area

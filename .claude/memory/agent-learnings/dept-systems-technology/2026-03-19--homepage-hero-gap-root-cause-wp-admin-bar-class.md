# Homepage Hero Gap: Root Cause — WordPress admin-bar Body Class

**Date**: 2026-03-19
**Type**: teaching
**Topic**: The real reason the homepage hero gap kept coming back after CSS fixes

---

## The Problem Pattern

The hero section gap returned 10+ times despite repeated CSS overrides targeting margin-top, padding-top, body, html, .elementor, etc. Every CSS fix worked temporarily or not at all because the root cause was structural, not stylistic.

## Root Cause (Definitive)

The exported WordPress HTML at exports/cf-pages-deploy/index.html contains an inner WordPress document embedded inside an Elementor widget wrapper. That inner document body tag had:

  class="... logged-in admin-bar no-customize-support ..."

WordPress admin-bar.min.css (loaded as external stylesheet from purebrain.ai/wp-includes/css/admin-bar.min.css) contains:

  body.admin-bar { margin-top: 32px; }

Because admin-bar class was on the body, this rule applied and pushed everything down 32px. CSS overrides targeting #wpadminbar did nothing because the margin is on body, not the admin bar div.

## Why CSS Overrides Failed

- #wpadminbar { display: none } hides the div but does NOT remove the margin on body.admin-bar
- Adding margin-top: 0 to body was overridden by the external stylesheet
- The external stylesheet loads from the old WordPress domain as a live network request

## The Fix

Three structural removals:

1. Strip "logged-in admin-bar no-customize-support" from inner body class — primary fix
2. Remove entire <div id="wpadminbar"> block — 19,594 chars of WP admin HTML
3. Remove the WordPress customize-support JS script — 422 chars

Total removed: 20,057 chars.

## How to Prevent Recurrence

When re-exporting homepage HTML from WordPress:
- Export will re-include admin-bar body class (exported while Jared is logged in to WP)
- Run post-export cleanup stripping these three things before deploying
- OR: export while NOT logged into WordPress admin (use incognito browser)

## Key Lesson

When a layout bug survives 10+ CSS fixes, the cause is structural. Stop adding CSS overrides. Read the DOM. The gap was margin-top: 32px on body from an external stylesheet triggered by a body class — invisible to anyone who only looks at CSS overrides.

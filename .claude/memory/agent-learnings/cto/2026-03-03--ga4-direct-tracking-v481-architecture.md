# GA4 Direct Tracking Architecture - Plugin v4.8.1

**Date**: 2026-03-03
**Type**: operational
**Agent**: cto

## Context
Implemented GA4 tracking (G-86325WBT3P) on purebrain.ai via WordPress plugin.
Decision: direct gtag.js (no GTM) because no GTM container ID existed yet.

## Architecture Decisions

### Direct GA4 vs GTM
- Chose direct gtag.js when GTM container doesn't exist yet
- GTM adds complexity (container setup, publish, versioning) without benefit at launch
- Direct GA4 gives immediate tracking with Measurement ID alone
- Pattern: add GA4 first, layer GTM on top later if event management complexity grows

### CSP Integration
- GA4 requires TWO CSP directives:
  - `script-src`: www.googletagmanager.com (for loading gtag.js script)
  - `connect-src`: www.google-analytics.com AND www.googletagmanager.com (for beacon sends)
- gtag.js sends measurement hits to `www.google-analytics.com/collect`
- gtag.js config endpoint is `www.googletagmanager.com/gtag/...`
- Both domains needed in connect-src even if script-src already has GTM

### wp_head Priority for Analytics
- GA4 head hook at priority 1 (earliest possible)
- Rationale: analytics needs to load before any user interaction scripts
- Layer 1 dark background CSS was already at priority 1 - added GA4 BEFORE it
- Priority ordering in wp_head: GA4 (priority 1) -> Dark BG Layer 1 (priority 1, added after) -> other CSS

### wp_footer Priority for Tracking Functions
- Functions registered at priority 999 (very late)
- Rationale: auto-wiring runs at DOMContentLoaded - needs all page elements present
- Priority 999 ensures all page JS has already run before wiring begins
- Functions registered as window.* globals so any page JS can call them

## Plugin Build Pattern
- v480 is source; build script reads it and applies surgical string substitutions
- Build script: `tools/build_v481.py`
- Pattern: markers are exact strings from source file, replaced with new content
- Verification: 18 checks run after build to confirm all changes applied correctly

## GA4 Conversion Events (need manual marking in GA4 Admin)
- `purchase` - most critical, marks revenue
- `newsletter_signup` - lead gen
- `form_submission` - engagement
- `assessment_start` - funnel entry

## File Paths
- Source: `exports/purebrain-security-plugin-v480.php`
- Output: `exports/purebrain-security-plugin-v481.php`
- Build script: `tools/build_v481.py`

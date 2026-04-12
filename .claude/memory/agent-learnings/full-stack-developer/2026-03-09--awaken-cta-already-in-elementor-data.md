# Awaken CTA Button: Already Embedded in Elementor Data (Page 11)

**Date**: 2026-03-09
**Type**: operational
**Agent**: full-stack-developer

## Task
Jared requested the "Awaken Your Personal AI Partner Today" CTA button be added directly into homepage (page 11) HTML via `_elementor_data`, with the deactivated plugin (pb-awaken-cta) no longer being the source.

## Finding: Already Done

The button was already embedded in `_elementor_data` before this task began. Specifically:

- **Elementor section ID**: `pb-awaken-cta-section`
- **Widget ID**: `pb-awaken-cta-widget` (widgetType: `html`)
- **Position in _elementor_data**: index 490921 (out of 499606 total chars)
- **Background**: `#080a12` (correct dark bg)

## Verified Order on Page

DOM order confirmed via rendered HTML position checks:
1. Compare PureBrain section (position 575777)
2. **Awaken CTA section** (position 578218) ← correctly placed
3. See Why PureBrain Is Different section (position 581912)

## Plugin Status

The pb-awaken-cta plugin's CSS (`<style id="pb-awaken-cta-css">`) and JS (`<script id="pb-awaken-cta-js">`) are NOT present in the rendered page source — confirming the plugin is deactivated and the button comes purely from Elementor widget data.

## Button HTML in Widget

Exactly matches the spec:
- Inline styles (no external CSS)
- Blue (#2a93c1) background with orange (#f1420b) hover via onmouseover/onmouseout
- Mobile `@media (max-width: 767px)` CSS inside the widget
- `href="#awakening"`
- Font: Plus Jakarta Sans

## Key Reference Files

- Deactivated plugin: `tools/security/pb-awaken-cta/pb-awaken-cta.php`
- REST API check: `GET /wp-json/wp/v2/pages/11?context=edit` → `meta._elementor_data`

## How the Button Got There

Based on the Elementor section data-id `pb-awaken-cta-section` being a named custom section (not auto-generated UUID), a previous session (likely around 2026-03-08 based on related memories) embedded this directly into `_elementor_data` using the REST API POST to `meta._elementor_data`.

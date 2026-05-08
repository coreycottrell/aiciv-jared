# Playbook Sidebar Redesign Pattern

**Date**: 2026-04-30
**Type**: technique
**Topic**: Converting scroll-based pages to sidebar+tab layout (data-room pattern)

## What Was Done
Converted dual-ai-playbook from single-scroll page with sticky nav to left sidebar + top search bar layout matching the data-room. All 13 sections became tabs in a DOCS JavaScript object, rendered via renderSection().

## Key Patterns
- DOCS object stores all content as HTML strings with title/meta/content fields
- renderSection() switches content, updates URL hash, marks as read, updates nav active state
- Search scans all DOCS entries, builds dropdown with snippets and match counts
- Checklist checkboxes need re-binding after render (loadChecklist called in renderSection for checklist tab)
- Mobile sidebar uses transform:translateX(-100%) + hamburger toggle + overlay

## File Size
~88KB for 13 sections with 8 detailed skill blocks. All content preserved.

## Gotchas
- Checklist localStorage binding must happen AFTER the checklist section is rendered to DOM
- Search highlight uses TreeWalker on rendered content, needs setTimeout for DOM to settle
- Sidebar nav items use data-section attribute, not href anchors

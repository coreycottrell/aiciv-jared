# Memory: UTM Parameter Master Reference Document

**Agent**: content-specialist
**Date**: 2026-02-23
**Type**: operational
**Topic**: Created standalone UTM reference for PureBrain.ai

---

## What Was Created

A clean, copy-paste-ready UTM parameter reference document extracted from `docs/from-telegram/brevo-automation-plan.md` (ITEM 2, lines 491-697).

**Output file**: `/home/jared/projects/AI-CIV/aether/config/utm-reference.md`

---

## Content Summary

- UTM framework architecture explanation (source/medium/campaign/content/term)
- Four master parameter tables (sources, mediums, campaigns, content values)
- Pre-built UTM link templates for every channel:
  - Neural Feed newsletter
  - Welcome sequence (email 1-7)
  - Audit nurture sequence
  - LinkedIn posts
  - Bluesky threads
  - Assessment and audit landing pages
  - Blog internal cross-links
- GA4 custom dimensions setup instructions
- 6 governance rules (all lowercase, hyphens not underscores, etc.)

---

## What Was Removed from Source

Per request: all timeline rows, owner columns, testing checklists, and project planning content were stripped. The output is reference-only — no action items.

---

## Audience

Jared, Arlene, and any agent creating links for PureBrain.ai content.

---

## Key Patterns for Future Reference

- `utm_source` = the property (newsletter, linkedin, blog, assessment, audit)
- `utm_medium` = the channel type (email, social, website, cta)
- `utm_campaign` = specific initiative (neural-feed-weekly, blog-[slug], etc.)
- `utm_content` = the specific element clicked (read-post, banner-cta, ps-link, email-1 through email-7)
- Homepage CTA always links to `https://purebrain.ai/#awakening`
- Blog slug templates use `[POST-SLUG]` placeholder notation

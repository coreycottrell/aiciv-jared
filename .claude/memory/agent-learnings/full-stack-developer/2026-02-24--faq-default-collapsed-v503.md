# FAQ Default-Collapsed Fix — Plugin v5.0.3

**Date**: 2026-02-24
**Type**: teaching + operational
**Topic**: Making all FAQ structures on purebrain.ai blog posts default to collapsed state

---

## Problem

FAQs on blog posts were displaying EXPANDED by default. Jared wanted all FAQs collapsed by default, expandable on click.

## Root Cause Discovery

NOT all blog posts use the same FAQ HTML structure. The plugin's existing accordion (hook `j`) only handles ONE structure. Three other structures exist:

| Post | Structure | Was It Collapsed? |
|------|-----------|-------------------|
| 565 | `.faq-section` div > `h3` + `p` | YES (existing accordion worked) |
| 631 | Native `<details>` + `<summary>` | YES (native HTML5 behaviour) |
| 606 | Bare `h3` + `p` after `<h2>FAQ</h2>` (no wrapping div) | NO — accordion never fired |
| 879 | `pb-faq-item` > `pb-faq-q` + `pb-faq-a` (custom structure) | NO — different classes, no accordion |

## Fix Applied

### Plugin v5.0.3 — New hook `j2` (priority 16, runs after `j` at priority 15)

**CSS added:**
- `.pb-faq-item .pb-faq-a` gets `max-height: 0; overflow: hidden` by default
- `.pb-faq-item.pb-faq-open .pb-faq-a` exposes content when open
- Chevron (`::after` on `.pb-faq-q`) rotates 180deg when open

**JS added — `initExtendedFaqAccordion()`:**
- **Structure A** (Post 879): Attaches click handler to `.pb-faq-q`, toggles `.pb-faq-open` on parent `.pb-faq-item`. Accordion: one open at a time.
- **Structure B** (Post 606): Finds all `h2` elements containing "FAQ", then wraps consecutive `h3`+`p` sibling pairs in `.faq-section` divs. After wrapping, the same init logic from hook `j` is run on the newly created `.faq-section` items.

## Files Changed

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
  - Version: `5.0.0` → `5.0.3` (header)
  - Added: `j2) FAQ ACCORDION EXTENDED` section (~190 lines)
  - Added: v5.0.3 changelog entries (two sections in file)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v503_purebrain.py` (new deploy script)

## Verification

All 16/16 live checks passed:
- Post 879: 6/6 (pb-faq-item structure handled)
- Post 606: 5/5 (bare h3+p structure handled)
- Post 565: 5/5 (existing accordion preserved)

## Permanent Rule Locked In

**ALL FAQ structures on ALL blog posts must default to collapsed.** When writing new blog posts:
- If using `.faq-section` + `h3` + `p`: covered by hook `j`
- If using `.pb-faq-item` + `.pb-faq-q` + `.pb-faq-a`: covered by hook `j2`
- If using bare `h3` + `p` after `<h2>FAQ</h2>`: covered by hook `j2`
- If using native `<details>` + `<summary>`: collapsed natively

## Key Pattern Learned

**When a CSS/JS accordion "works" but seems broken on some posts**: Check if those posts use a DIFFERENT HTML class structure. The fix isn't always to change the CSS — sometimes you need JS to detect and handle additional patterns. Using a separate `add_action` hook at priority 16 (after the main accordion at 15) is the clean pattern for extension.

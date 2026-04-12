# Memory: Alternate Footer Reorder - PT Footer to Bottom

**Date**: 2026-02-23
**Type**: operational
**Topic**: Moving PT alternate footer section to bottom of 5 purebrain pages

## What Was Done

Moved the Pure Technology alternate footer (dark section with PT logo, copyright, and links to PureTechnology.ai / PureMarketing.ai / PureInfluence.ai) to the very bottom of the page - below the Calculator CTA and Compare PureBrain sections.

## Pages Updated

| Page ID | Slug | Status |
|---------|------|--------|
| 11 | pure-brain-agentic-ai-partner (homepage) | SUCCESS |
| 439 | pay-test | SUCCESS |
| 468 | pay-test-sandbox | SUCCESS |
| 689 | pay-test-2 | SUCCESS |
| 688 | pay-test-sandbox-2 | SUCCESS |

## Page Structure (Before)

All 5 pages had identical 3-element structure:
1. **Container 0** (elType: container, isInner: false) - contains a single HTML widget
   - HTML widget: full page HTML including `<footer class="footer">` at the END of HTML content
2. **Section 1** (bb51444 on homepage) - Calculator CTA section (`pb-calc-cta`)
3. **Section 2** (b4e40ffa on homepage) - Compare PureBrain section

Visual rendering order was:
- (all main content)...
- PT footer (end of HTML widget)
- Calculator CTA section
- Compare PureBrain section
- Copyright bar (plugin-injected `#purebrain-legal-footer`)

## Page Structure (After)

4-element structure:
1. Container 0 with HTML widget (PT footer REMOVED from HTML)
2. Section 1 - Calculator CTA
3. Section 2 - Compare PureBrain
4. **NEW Section** (pb-alt-footer-section) - PT footer HTML

Visual rendering order is now:
- (all main content)...
- Calculator CTA section
- Compare PureBrain section
- **PT alternate footer** (LAST elementor section)
- Copyright bar (plugin, appears after all elementor content)

## How the Change Was Made

1. **Fetched** each page with `?context=edit` to get `_elementor_data` from meta
2. **Found** the HTML widget by recursively searching for `widgetType == 'html'` containing `footer class="footer"`
3. **Extracted** the `<footer class="footer">...</footer>` HTML (1538 chars identical on all pages)
4. **Removed** the footer from the HTML widget's content
5. **Created** a new Elementor section structure:
   ```json
   {
     "elType": "section",
     "settings": {"css_classes": "pb-alt-footer-section"},
     "elements": [
       {"elType": "column", "settings": {"_column_size": 100},
        "elements": [
          {"elType": "widget", "widgetType": "html", "settings": {"html": "<footer class=\"footer\">..."}}
        ]}
     ]
   }
   ```
6. **Appended** the new section to the end of `_elementor_data` array
7. **Validated** JSON with `json.loads()` before PUT
8. **Updated** via `POST /wp-json/wp/v2/pages/{id}` with `meta._elementor_data`
9. **Cleared** Elementor cache via `DELETE /wp-json/elementor/v1/cache`

## The PT Footer HTML Content

```html
<footer class="footer">
    <div class="footer__content">
        <div class="footer__brand">
            <img src="https://purebrain.ai/wp-content/uploads/2026/02/MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png"
                 alt="Pure Technology" class="footer__logo" loading="lazy">
            <span>© 2026 Pure Technology Inc.</span>
        </div>
        <div class="footer__links">
            <div class="footer__links-row">
                <a href="https://puremarketing.ai/terms-conditions-privacy-policy/" class="footer__link" target="_blank">Privacy & Terms</a>
                <a href="https://puremarketing.ai/contact-us/" class="footer__link" target="_blank">Contact Us</a>
                <a href="https://puretechnology.ai/#team" class="footer__link" target="_blank">Team</a>
            </div>
            <div class="footer__links-row">
                <a href="https://puretechnology.ai/" class="footer__link" target="_blank">PureTechnology.ai</a>
                <a href="https://puremarketing.ai/" class="footer__link" target="_blank">PureMarketing.ai</a>
                <a href="https://pureinfluence.ai/" class="footer__link" target="_blank">PureInfluence.ai</a>
            </div>
        </div>
    </div>
</footer>
```

## Important Notes

- The `<footer class="footer">` CSS styles remain in the HTML widget's `<style>` block - they were NOT removed (just the HTML element was removed)
- The footer CSS class definitions are in the large HTML widget's `<style>` section, so they still apply to the new footer section
- The copyright bar (`#purebrain-legal-footer`) is injected by the WordPress plugin and always appears AFTER all Elementor content - it is NOT affected by this change
- All 5 pages had identical PT footer HTML (1538 chars), making the pattern perfectly consistent

## Backup Files

- `/tmp/page11_elementor_backup.json`
- `/tmp/page439_elementor_backup.json`
- `/tmp/page468_elementor_backup.json`
- `/tmp/page689_elementor_backup.json`
- `/tmp/page688_elementor_backup.json`

## Verification Method

```python
# REST API check - PT footer is ONLY in last section
elem_data = json.loads(data['meta']['_elementor_data'])
last_section = elem_data[-1]
last_str = json.dumps(last_section)
assert 'pureinfluence' in last_str.lower()  # Footer is in last section
earlier = json.dumps(elem_data[:-1])
assert 'pureinfluence' not in earlier.lower()  # NOT in earlier sections
```

## Key Patterns Learned

- PureBrain pages have a "big HTML widget" pattern - single `widgetType: html` widget containing the entire page HTML as a string
- To reorder sections that are INSIDE the HTML widget, you must extract them FROM the HTML string and create proper Elementor section wrappers
- The Elementor section structure requires: section > column > widget nesting
- CSS classes defined in `<style>` tags within the HTML widget still apply to sibling/child Elementor sections because they render on the same page

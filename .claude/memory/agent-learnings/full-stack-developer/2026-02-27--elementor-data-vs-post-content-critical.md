# CRITICAL: Elementor _elementor_data vs post_content

**Date**: 2026-02-27
**Severity**: CRITICAL - Root cause of multiple failed deployments
**Type**: gotcha, architecture

## The Problem

When updating Elementor pages via WordPress REST API, there are TWO places content lives:

1. `post_content` (aka `content.raw`) - WordPress's standard content field
2. `meta._elementor_data` - Elementor's OWN content storage (JSON)

**Elementor renders from `_elementor_data`, NOT from `post_content`.**

Updating `post_content` via REST API changes what WordPress stores, but Elementor ignores it during rendering. The browser receives HTML generated from `_elementor_data`.

## How To Update Elementor Pages Correctly

```python
# 1. Get current _elementor_data
response = requests.get(url + '?context=edit', auth=auth)
elementor_data = response.json()['meta']['_elementor_data']

# 2. Modify the elementor_data string (JSON with escaped HTML)
fixed_data = elementor_data.replace(old_code, new_code)

# 3. Update via REST API meta field
requests.post(url, auth=auth, json={
    'meta': {'_elementor_data': fixed_data}
})
```

## Second Critical Lesson: Nested HTML Documents

When a page uses `<!-- wp:html -->` blocks containing a full `<!DOCTYPE html><html><head>` document:

- Browser STRIPS the nested `<head>` tag during parsing
- `<style>` blocks inside nested `<head>` are IGNORED or unreliable
- CSS fixes MUST be in the MAIN document's `<head>` (via plugin, Additional CSS, or wp_head hook)
- JS inside the nested document IS executed normally

## Affected Pages

- Page 688 (pay-test-sandbox-2) - Elementor canvas + wp:html
- Page 689 (pay-test-2) - Elementor canvas + wp:html
- Page 777 (calculator) - Elementor canvas + wp:html
- Page 987 (invitation) - Elementor canvas + wp:html

## How To Know Which System Renders

- Check `template` field: if `elementor_canvas`, Elementor is involved
- Check `meta._elementor_edit_mode`: if `builder`, Elementor controls rendering
- Check `meta._elementor_data` length: if > 100 chars, it has Elementor widget data
- Page 777 special case: _elementor_data is only 742 chars (just footer), main content is in post_content's wp:html block, BUT Elementor still wraps the page

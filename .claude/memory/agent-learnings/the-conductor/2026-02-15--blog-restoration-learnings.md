# Blog Restoration Learnings - 2026-02-15

**Type**: operational
**Topic**: WordPress/Elementor page restoration patterns
**Confidence**: High (verified through iteration)

---

## Context

Jared reported purebrain.ai/blog was "broken" and "looked horrible." Through ~2 hours of debugging, we identified multiple interacting issues and eventually restored it.

---

## Key Learnings

### 1. WordPress "Posts Page" Override

**Problem**: When a page is set as the "Posts page" in Settings → Reading, WordPress IGNORES the page content entirely and uses the theme's archive template.

**Symptom**: Custom HTML/content doesn't show at all. Theme's default "Blog" header and breadcrumbs appear instead.

**Fix**: Either remove the Posts page setting OR accept that the page will use theme template.

**API Check**:
```python
# Check reading settings
settings = requests.get(url + "/wp-json/wp/v2/settings", auth=auth).json()
print(f"page_for_posts: {settings.get('page_for_posts')}")  # 0 = none, >0 = page ID
```

### 2. Elementor Data Override

**Problem**: Even when WordPress raw content has custom HTML, Elementor's `_elementor_data` meta overrides it during rendering.

**Symptom**: API shows correct content in `content.raw` but `content.rendered` shows Elementor output.

**Fix**: Clear Elementor meta fields (may require direct DB or manual editor):
```python
# These fields control Elementor rendering
meta = {
    "_elementor_edit_mode": "",  # Clear to disable Elementor
    "_elementor_data": ""        # Clear Elementor's stored layout
}
# Note: WordPress API may return 403 on protected meta fields
```

### 3. Template Matters

**Problem**: Page template affects what wraps the content. Default template adds theme header/footer. Elementor Canvas provides blank slate.

**Fix sequence that worked**:
1. Clear `page_for_posts` setting (so WordPress shows page content)
2. Clear Elementor meta (so Elementor doesn't override)
3. Set template to `elementor_canvas` (for blank page without theme elements)

### 4. CSS Cleared = Broken Appearance

**Problem**: Custom CSS in Customizer was cleared during earlier troubleshooting, causing page to look "horrible" even with correct HTML.

**Lesson**: Always check Additional CSS when page "looks wrong" but structure is correct.

**Fix**: Restore CSS from saved backup (`exports/purebrain-complete-styling.css`)

---

## Debugging Sequence

1. **Check what user sees** - WebFetch the page
2. **Check page settings** - template, meta, reading settings via API
3. **Compare raw vs rendered** - `content.raw` vs `content.rendered`
4. **Check if Elementor is active** - `_elementor_edit_mode` meta
5. **Check CSS** - is Additional CSS populated?

---

## Files to Keep

- `exports/purebrain-blog-page-v2.html` - Working blog HTML
- `exports/purebrain-complete-styling.css` - Complete CSS backup
- `docs/from-telegram/` - Jared's reference screenshots

---

## Prevention

1. **Before touching blog page**: Screenshot current state
2. **Save CSS before clearing**: Always backup Additional CSS
3. **Document page settings**: Template, reading settings, Elementor status
4. **Test in incognito**: Browser cache can mask changes

---

## Cross-Reference

- Related memory: `.claude/memory/agent-learnings/the-conductor/2026-02-14--blog-restoration-lessons.md`
- Site recommendations: `exports/site-edit-recommendations-2026-02-15.md`

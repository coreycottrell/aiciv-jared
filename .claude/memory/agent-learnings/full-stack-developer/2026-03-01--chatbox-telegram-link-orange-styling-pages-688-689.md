# Memory: Chatbox Telegram Link Orange Styling — Pages 688 & 689

**Date**: 2026-03-01
**Type**: operational + gotcha
**Topic**: Added orange color styling to Telegram links in the BotFather setup step of chatbox on both pay-test pages

---

## What Was Done

Added `style="color: #f1420b; text-decoration: underline;"` to two anchor tags in the chatbox BotFather setup message on pages 688 (pay-test-sandbox-2) and 689 (pay-test-2).

### Links Styled

1. `web.telegram.org` — desktop Telegram login link
2. `tap here` — mobile Telegram download link (telegram.org/dl)

### Before

```html
<a href=\"https://web.telegram.org\" target=\"_blank\">web.telegram.org</a>
<a href=\"https://telegram.org/dl\" target=\"_blank\">tap here</a>
```

### After

```html
<a href=\"https://web.telegram.org\" target=\"_blank\" style=\"color: #f1420b; text-decoration: underline;\">web.telegram.org</a>
<a href=\"https://telegram.org/dl\" target=\"_blank\" style=\"color: #f1420b; text-decoration: underline;\">tap here</a>
```

---

## Pattern That Worked

Standard `content.raw` GET/replace/POST pattern. Same as all prior chatbox deployments.

```python
resp = requests.get(f"{WP_BASE}/{page_id}?context=edit&_fields=content", auth=auth)
content = resp.json()['content']['raw']
new_content = content.replace(OLD, NEW)
requests.post(f"{WP_BASE}/{page_id}", auth=auth, json={"content": new_content})
```

Content delta: +108 chars per page (54 chars per link x 2 links).

---

## Gotchas

### 1. Custom endpoint does NOT work for _elementor_data

The task brief suggested using `/wp-json/purebrain/v1/update-post-meta` to update `_elementor_data`. This returns:
```json
{"code":"meta_key_not_allowed","message":"Meta key \"_elementor_data\" is not in the allowed list."}
```

Use `content.raw` via `/wp-json/wp/v2/pages/{id}` instead. The chatbox JS lives in `content.raw`, not separately in `_elementor_data`.

### 2. Pages 688/689 are password-protected

The rendered HTML from a GET request to these URLs returns the WP password gate (132KB), NOT the chatbox content. Verification must be done against `content.raw` via the REST API with `context=edit`, NOT against the live rendered HTML.

### 3. String escaping in content.raw

Inside `content.raw`, the HTML widget content uses `\"` (single backslash-escaped quotes). When doing Python `.replace()`, match exactly what appears in the raw string. The strings appear as:
```
<a href=\"https://web.telegram.org\" target=\"_blank\">
```

---

## Verification Results

Both pages:
- Old unstyled links: ABSENT
- New orange-styled links: PRESENT
- Last modified timestamps: 2026-03-01T18:43:25 (689) and 2026-03-01T18:43:29 (688)
- Elementor cache cleared: HTTP 200

---

## File References

- Fix script: `/tmp/fix_chatbox_links_v2.py`
- Backups: `/tmp/page689_chatbox_link_fix_backup.html`, `/tmp/page688_chatbox_link_fix_backup.html`

---

## Tags

chatbox, pay-test, telegram, link-styling, orange, pages-688-689, content-raw, password-protected-page

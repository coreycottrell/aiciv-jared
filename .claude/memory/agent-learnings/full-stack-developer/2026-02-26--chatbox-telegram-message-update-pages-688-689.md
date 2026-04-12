# Chatbox Telegram Message Update — Pages 688 & 689

**Date**: 2026-02-26
**Type**: operational
**Topic**: Surgical one-string replacement in inline JS on WP pages 688 and 689

## What Was Done

Changed the Telegram success message in the chatbox flow on purebrain.ai pages 688 (pay-test-sandbox-2) and 689 (pay-test-2).

**Old string:**
```
${aiName} will reach you there when your AI is ready.
```

**New string:**
```
As a back up to your Brain Stream Portal, you will be able to reach ${aiName} on telegram when ready.
```

## Pattern That Worked

GET with `context=edit` to retrieve raw content, Python string `.replace()`, POST back. All done in one script — no temp files needed.

```python
resp = requests.get(f"{WP_BASE}/{page_id}?context=edit", auth=auth)
content = resp.json()['content']['raw']
new_content = content.replace(OLD, NEW)
requests.post(f"{WP_BASE}/{page_id}", auth=auth, json={"content": new_content})
```

## Key Notes

- Both pages had exactly 1 occurrence of the old string
- Content length ~433,196 chars each (large inline HTML/JS pages)
- String lives inside a JS template literal: `\`Your Telegram bridge is live. ${aiName} ... \``
- `context=edit` is REQUIRED to get `content.raw` (without it you get rendered HTML)
- WP credentials: user=Aether, PUREBRAIN_WP_APP_PASSWORD from .env

## Verification

Both pages confirmed:
- Old string absent
- New string present with correct surrounding JS context
- HTTP 200 on PUT, status=publish

# Exit Intent Popup - Code Extraction from purebrain.ai

**Date**: 2026-02-19
**Type**: operational
**Topic**: Complete exit intent popup code extracted from page 11 via WordPress REST API

## What I Did

Used WordPress REST API with Aether credentials to fetch `_elementor_data` for page 11 (homepage). Searched the 321KB JSON blob for exit intent patterns.

## Key Findings

### Trigger Mechanism
- Uses `mouseout` event (not `mouseleave`) on `document`
- Checks `e.clientY < 10` - mouse moving toward top of viewport / browser chrome
- NOT a global trigger - gated by `state.exitIntentEnabled` which only becomes `true` after user completes the chat conversation

### Session Guard
- Uses `sessionStorage.getItem('exitPopupShown')` to show only once per session

### Dynamic Text
- `.ai-name-dynamic` class on `<span>` elements throughout popup
- Replaced via `updateAllDynamicNames(aiName)` - queries all spans with that class

### Missing CSS Variables
- `--dark-gray` is referenced but NEVER defined anywhere (not in :root, not in theme CSS)
- `--text-muted` is referenced but NEVER defined
- Browser silently ignores undefined CSS vars (falls back to initial/transparent)
- The dark overlay background (rgba(0,0,0,0.9)) makes content look dark anyway

## Technique That Worked

```bash
curl -s -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ" \
  "https://purebrain.ai/wp-json/wp/v2/pages/11?context=edit" \
  -o /tmp/page11_data.json
```

Then Python json.load + string search for pattern keywords. The `_elementor_data` is inside `data['meta']['_elementor_data']`.

## When to Apply

- Any future extraction of Elementor page code
- Looking for JavaScript embedded in Elementor HTML widgets
- The `context=edit` parameter is critical - without it, meta fields are not returned

## File Reference

Full documented extraction: `/home/jared/projects/AI-CIV/aether/docs/EXIT-INTENT-POPUP-CODE.md`

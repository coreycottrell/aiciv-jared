# Memory: Post-Payment Chatbox Debug Pattern

**Date**: 2026-03-03
**Type**: pattern + operational
**Topic**: How to diagnose blank screen after payment on purebrain.ai pay-test pages

---

## Diagnosis Workflow That Works

1. **Two-step cookie auth** to get past WP password protection:
   ```bash
   curl -c /tmp/pb_cookies.txt -b /tmp/pb_cookies.txt -X POST "https://purebrain.ai/PAY-TEST-URL/" \
     --data "post_password=PASSWORD" -L -o /tmp/page.html
   ```
   Then use that cookie jar on subsequent GETs.

2. **Check for all script load order** — verify PayPal popup, chat flow, integration glue all present.

3. **List all function declarations** in the chat flow script area:
   ```python
   import re
   functions = re.findall(r'(?:async )?function (\w+)\s*\(', chatflow_area)
   ```
   Compare against what's CALLED in `initPayTestFlow`.

4. **Cross-reference with working page** (688 or 689) to find missing functions.

---

## Elementor Data Access Pattern

Pages 688, 689, 1232 require `context=edit` to get `_elementor_data`:
```bash
curl -s "https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID?context=edit" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr"
```

The widget 292c72a is the main content widget on ALL pay-test pages.
It contains the full self-contained HTML including all scripts.

---

## Silent Error Pattern in initPayTestFlow

The async `try/catch` in `initPayTestFlow` catches ALL errors and shows a brief error bubble, but the position:fixed overlay div persists as a blank dark screen.

Any missing function called with `await` will cause this:
- `await runCompletion(...)` — MISSING in 1232 (fixed 2026-03-03)
- `await runBirthInit(...)` — intentionally removed in 1232 (OAuth removed)

---

## Memory File Reference

Full technical details:
`.claude/memory/agent-learnings/full-stack-developer/2026-03-03--pay-test-sandbox-3-runcomplete-missing.md`

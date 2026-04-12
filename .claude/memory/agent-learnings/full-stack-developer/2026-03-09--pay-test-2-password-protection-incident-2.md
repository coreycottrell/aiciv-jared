# Memory: pay-test-2 (page 689) Password Protection Incident #2

**Date**: 2026-03-09
**Agent**: dept-systems-technology
**Type**: incident-response + gotcha + pattern
**Tags**: purebrain, pay-test-2, page-689, password-protection, elementor, wordpress, recurring-incident

---

## Incident Summary

pay-test-2 (page 689) was showing the WordPress password gate form instead of the payment flow.

**Root cause**: Page had been password-protected AGAIN (same as 2026-03-06 incident).
Password was: `PureBrain.ai253443$$`

This is the **second occurrence** of this exact same incident. Pattern is emerging.

---

## Diagnosis Path

1. `curl https://purebrain.ai/pay-test-2/ | head -100` → Saw normal WP theme header
2. `curl .../wp-json/wp/v2/pages/689 | python3 ...` → Found `password: 'PureBrain.ai253443$$'`, `content.protected: True`
3. Live page body: `"This content is password-protected. To view it, please enter the password below."`
4. The `_elementor_data` was intact (378,894 chars) - content was never lost
5. Password gate intercepted BEFORE Elementor could render

---

## What Was Also Found

During diagnosis, the `_elementor_data` HTML widget contained a full `<!DOCTYPE html>` document (nested HTML docs issue from 2026-03-08 memory). This was also fixed.

---

## Fixes Applied

```python
# Fix 1: Remove password protection + fix nested HTML
payload = {
    'password': '',  # Remove password
    'meta': {
        '_elementor_data': fixed_elementor_json,  # With </body></html> stripped
        '_elementor_edit_mode': 'builder',
    },
    'status': 'publish',
    'template': 'elementor_canvas'
}
```

```bash
# Fix 2: Clear Elementor cache
curl -X DELETE "https://purebrain.ai/wp-json/elementor/v1/cache" \
  -u "${WP_USER}:${WP_PASS}" \
  -H "Content-Type: application/json"
```

**WP Credentials for purebrain.ai**: `purebrain@puremarketing.ai` + app password from `.env` (`PUREBRAIN_WP_APP_PASSWORD`)

---

## Verification (All Pass)

- Password gate: 0 (removed)
- Page line count: 12,556 (was 3,771 with password gate)
- PayPal references: 131
- Hero sections: 38
- Dark background: 24
- `<!DOCTYPE` count: 1 (outer page only)
- `</body>` count: 1 (no nested docs)
- `</html>` count: 1 (no nested docs)

---

## Recurring Incident Pattern

| Date | Incident | Cause Known? |
|------|----------|-------------|
| 2026-03-06 | Pages 688, 689 both password-protected | Batch WP operation (suspected) |
| 2026-03-09 | Page 689 password-protected again | Unknown |

**OPEN QUESTION**: Why does this keep happening?
Possible causes:
1. A plugin or scheduled task is setting passwords on pages
2. A WP batch update operation is accidentally applying password from one page to others
3. Someone/something is running REST API operations that set password fields

**Recommended investigation**:
- Check WP action log / audit log plugin for page 689 modifications
- Check if any scheduled tasks or automations touch page meta/settings
- Check if Elementor's batch update features or theme customizer could be doing this

---

## Quick Fix Command (Future Reference)

If this happens again, the fix is one REST API call:

```bash
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/689" \
  -u "purebrain@puremarketing.ai:41w3 xWWZ 11em UXgj hjAF sx2T" \
  -H "Content-Type: application/json" \
  -d '{"password": ""}'
# Then clear Elementor cache
curl -X DELETE "https://purebrain.ai/wp-json/elementor/v1/cache" \
  -u "purebrain@puremarketing.ai:41w3 xWWZ 11em UXgj hjAF sx2T"
```

---

## Memory Write Verification

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-03-09--pay-test-2-password-protection-incident-2.md`
Type: incident-response + gotcha + pattern

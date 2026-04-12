# Why PureBrain Link - Verification Session

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Verification that Why PureBrain link is deployed on all 4 pay-test pages

---

## Summary

Task was to add "Why PureBrain?" link (href: https://purebrain.ai/why-purebrain/) to 4 pay-test pages.

**Result**: Already deployed from a prior session (same date). No changes needed.

---

## Page IDs Discovered (Future Reference)

| Slug | Page ID | Status |
|------|---------|--------|
| pay-test | 439 | Published, password-protected |
| pay-test-2 | 689 | Published, password-protected |
| pay-test-sandbox | 468 | Published, password-protected |
| pay-test-sandbox-2 | 688 | Published, password-protected |

---

## Deployment State Verified

All 4 pages have the Why PureBrain link in TWO places:

1. **Elementor `_elementor_data`**: Last section named `why_pb_{PAGE_ID}` containing an HTML widget with:
   ```html
   <div style="text-align:center; padding:30px 20px; margin-top:20px; background:#080a12;">
     <a href="https://purebrain.ai/why-purebrain/" style="color:#2a93c1; font-size:15px; ...">
       See How PureBrain Compares →
     </a>
   </div>
   ```

2. **`content.raw`**: Also contains the link (from earlier HTML injection approach)

All Elementor JSON is valid (confirmed json.loads() round-trip).

---

## Why Pages Show Password Form on Live Visit

The pay-test pages are password-protected in WordPress. The Elementor content only renders after password entry. This is expected behavior - the link IS present in the database.

---

## Auth Pattern for purebrain.ai REST API

```python
WP_USER = 'Aether'
WP_PASS = 'FlFr2VOtlHiHaJWjzW96OHUJ'  # PUREBRAIN_WP_APP_PASSWORD (no surrounding quotes)
auth_string = f'{WP_USER}:{WP_PASS}'
creds = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
headers = {'Authorization': f'Basic {creds}', ...}
```

Note: The .env value has surrounding single quotes `'FlFr2...'` - strip them when using.

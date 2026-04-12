# Memory: Publish Password-Protected Pages 688 & 689

**Date**: 2026-02-22
**Type**: operational
**Topic**: Publishing cloned pay-test pages with password protection via WP REST API

## What Was Done

Published two cloned WordPress pages on purebrain.ai with password protection matching their source pages.

| Page ID | Slug | Source ID | Password Used |
|---------|------|-----------|---------------|
| 688 | pay-test-sandbox-2 | 468 (pay-test-sandbox) | PureBrain.ai253443$$$ |
| 689 | pay-test-2 | 439 (pay-test) | PureBrain.ai253443$$$ |

Both source pages use the same password: `PureBrain.ai253443$$$`

## Pattern That Worked

```python
# Fetch source page password
source = requests.get(f'{base}/{source_id}?context=edit', auth=auth).json()
password = source.get('password', '')

# Publish with matching password
requests.post(f'{base}/{page_id}', auth=auth, json={
    'status': 'publish',
    'password': password
})
```

## Verification Pattern

WordPress password-protected pages return HTTP 200 but contain `post-password-form` in the HTML body. Check for this string to confirm password protection is active.

## URLs

- https://purebrain.ai/pay-test-sandbox-2/ (password protected, live)
- https://purebrain.ai/pay-test-2/ (password protected, live)

## Notes

- Elementor cache cleared after publishing (DELETE /elementor/v1/cache)
- The `context=edit` parameter is required when fetching page data to get the password field
- Without `context=edit`, the password field is not returned in the API response

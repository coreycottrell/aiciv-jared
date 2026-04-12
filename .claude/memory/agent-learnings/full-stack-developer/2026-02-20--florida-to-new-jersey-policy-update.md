# Florida to New Jersey Policy Update

**Date**: 2026-02-20
**Type**: operational
**Topic**: Updating jurisdiction references in WordPress legal pages via REST API

---

## Task

Changed all "Florida" -> "New Jersey" references in:
- Privacy Policy (page ID 3, purebrain.ai/privacy-policy/)
- Terms of Service (page ID 541, purebrain.ai/terms-of-service/)
- Local HTML files at to-jared/privacy-policy.html and to-jared/data-policy.html

## Changes Made

### Privacy Policy (ID 3)
- Contact section: `Florida, USA` -> `New Jersey, USA`
- Note: No governing law section exists in Privacy Policy

### Terms of Service (ID 541)
- Governing law paragraph: `State of Florida` -> `State of New Jersey`, `courts located in Florida` -> `courts located in New Jersey`
- Contact section: `Florida, USA` -> `New Jersey, USA`

### Local HTML files
- `/home/jared/projects/AI-CIV/aether/to-jared/privacy-policy.html`: Contact location Florida -> New Jersey
- `/home/jared/projects/AI-CIV/aether/to-jared/data-policy.html`: Governing law + contact location Florida -> New Jersey

## Method

Used Python `requests` to:
1. GET page content with `?context=edit` to get `content.raw`
2. Perform string replacements in the raw WordPress block content
3. POST updated content back via REST API
4. Verify live pages render correctly

## Credentials

- User: Aether
- Password: `PUREBRAIN_WP_APP_PASSWORD` from `.env` (value: FlFr2VOtlHiHaJWjzW96OHUJ)

## Verification

- WordPress raw content: 0 Florida refs after update
- Live TOS page: New Jersey confirmed in rendered HTML
- Live Privacy Policy: CDN may cache briefly but raw content confirmed correct
- Local HTML files: No Florida refs remaining

## Notes

- CDN (Cloudflare/GoDaddy) may briefly serve cached version of Privacy Policy
- The pages use `<!-- wp:html -->` Gutenberg block format (learned from previous session)
- Always use `?context=edit` when fetching pages to get raw block content

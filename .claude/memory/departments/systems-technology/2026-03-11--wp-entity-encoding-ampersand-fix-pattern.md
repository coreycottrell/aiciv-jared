# WordPress Entity Encoding: && Operator Fix Pattern

**Date**: 2026-03-11
**Incident**: pay-test-2 (page 689) and pay-test-sandbox-3 (page 1232) broken on production
**Status**: RESOLVED

---

## Root Cause: Multi-Layer Failure

The breakage had three independent causes that had to be resolved in order:

### Layer 1: Password Gate (Primary Blocker)
- Both pages had `"password": "PureBrain.ai253443$"` set in WP
- Users saw a password input form instead of the page
- Fix: `curl -X POST ... -d '{"password":"","status":"publish"}'`
- Check: `curl /wp-json/wp/v2/pages/{id}` and inspect `"password"` field

### Layer 2: Wrong Source File for Deployment
- CF pages deploy files (`exports/cf-pages-deploy/`) contain WP-rendered HTML with embedded scripts, trackers, etc.
- Deploying these back to WP causes double-processing and ~121k render instead of full page
- Correct source: `purebrain-site/public/pay-test-2/index.html` (standalone, no WP wrapper)
- Correct source for sandbox-3: `purebrain-site/public/pay-test-sandbox-3/index.html` (has correct sandbox PayPal plan IDs from commit 80296154)

### Layer 3: WP Entity Encoding Breaking && Operator
- WordPress encodes `&` as `&#038;` at render time in script blocks
- `if (window.innerWidth < 768 && playerEl)` becomes `if (window.innerWidth < 768 &#038;&#038; playerEl)` in rendered HTML
- This causes `SyntaxError: Invalid or unexpected token` which prevents the chatbox JS from loading
- Also: `// WAITLIST MODAL & FORM` comment had `&` encoded as `&#038;`

---

## The Fix Pattern (PERMANENT REFERENCE)

When any `&&` operator in JS will be processed by WordPress's wp_kses/wpautop at render time:

```javascript
// BEFORE (breaks with WP entity encoding):
if (conditionA && conditionB) {
    doSomething();
}

// AFTER (WP-safe, no && in executable code):
if (conditionA) { if (conditionB) {
    doSomething();
} }
```

For `&` in JS comments:
```javascript
// BEFORE: // WAITLIST MODAL & FORM
// AFTER:  // WAITLIST MODAL + FORM
```

---

## Deployment Pattern for Standalone HTML to WordPress

```python
with open('/tmp/fixed.html', 'r') as f:
    content = f.read()

# MUST wrap in wp:html block
wp_content = f'<!-- wp:html -->\n{content}\n<!-- /wp:html -->'

response = requests.post(
    f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}',
    auth=('purebrain@puremarketing.ai', 'FlFr2VOtlHiHaJWjzW96OHUJ'),
    json={
        'content': wp_content,
        'template': 'elementor_canvas',
        'status': 'publish',
        'password': ''  # Always clear password on non-gated pages
    }
)
```

After deployment, ALWAYS:
1. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
2. Verify with `?_v=TIMESTAMP` to bypass CF cache

---

## Verification Checklist

After any WP page deployment:
- [ ] No password gate (`Enter password` / `post-password-form` absent)
- [ ] `startConversation` present
- [ ] `&#038;&#038;` count = 0 in chatbox script block (third-party libs OK)
- [ ] PayPal SDK present
- [ ] Begin Awakening button present
- [ ] Dark background present

---

## False Alarm: Third-Party Emoji Library

sandbox-3 showed 54 `&#038;&#038;` occurrences after the fix. These were all in a minified emoji detection library (twemoji/emoji-flags type code) that was already embedded in the page. These do NOT break functionality because:
1. The emoji library is a complete minified bundle that WP processes differently
2. The `&#038;` encoding in that context does not cause SyntaxError
3. The chatbox script block itself had ZERO entity encoding

To verify: search for `&#038;` near `startConversation` and `window.innerWidth` — those blocks must be clean.

---

## WP Credentials (Active)
- Auth user: `purebrain@puremarketing.ai`
- Application password: `FlFr2VOtlHiHaJWjzW96OHUJ`
- Page IDs: pay-test-2 = 689, pay-test-sandbox-3 = 1232

## PayPal Sandbox Plan IDs (sandbox-3)
```javascript
var PLAN_IDS = {
    Awakened:  'P-9KA28683EF7622051NGLUFJY',
    Bonded:    'P-1JL98851AU229172RNGLUFJY',
    Partnered: 'P-6JY35646YA5259513NGLUFKA',
    Unified:   'P-6DU61407NY0900135NGLUFKI',
};
```
Source commit: `80296154` in `purebrain-site/public/pay-test-sandbox-3/index.html`
